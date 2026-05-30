import networkx as nx
import os
import sys
import json 

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

from agent.tool import NSFAgent, query_nsf_api

# Import spaCy for NER

try: 
    import spacy
    SPACY_AVAIL = True
except ImportError:
    SPACY_AVAIL = False
    print("Warning: spaCy not installed.")

class KGBuilder():
    """
    Knowledge graph builder for NSF Awards using NetworkX.
    Transforms data into a connected graph of PIs, Institutions, and Awards.
    """
    _COMMON_WORDS = ["research", "study", "investigation", "development", "analysis", "award", "researchers", "nsf"]

    def __init__(self):
        self.graph = nx.Graph()
        self.agent = NSFAgent()

        # Deduplication sets 
        self.pi_names = set()
        self.copi_names = set()
        self.institution_names = set()
        self.award_ids = set()
        self.nlp = None # set externally

    def normalize_name(self, name):
        """
        Normalize names for deduplication

        Args:
            String name : name from API

        Returns:
            String normalized name
        """

        if not name or name == "Unknown PI" or name == "Unknown Institution":
            return name
        
        # Strip whitespace, replace + with space 
        name = name.strip().replace('+', ' ')
        
        # Strip email addresses off names ex: "Erik Fredericks frederer@gvsu.edu"
        tokens = [t for t in name.split() if '@' not in t]
        name = ' '.join(tokens) # any other whitespace
        if not name: 
            return name

        # Looking for Last, First pattern, eg: Conger, Lauren or Garzella, Jack J
        if ',' in name: 
            parts = name.split(',', 1) # Split on first comma only, put them into array
            last = parts[0].strip()
            first = parts[1].strip()
            # Reoder if neither looks like institution
            if (first and last and len(last.split()) <= 3 and not any(c.isdigit() for c in name)):
                name = f"{first} {last}" # Here it is yippee

        normalized = ' '.join(name.lower().split()).title() # lowercase, title case
        # Title case
        normalized = normalized.title()

        return normalized
    
    def set_nlp(self, nlp): 
        self.nlp = nlp
    
    def parse_copi_names(self, raw_copi):
        """
        Parse coPI field into a list of normalized co-investigator strings

        Args: 
            String/List of Dicts - raw_copi
        Returns:
            List[str]: normalized coPI name strings
        """
        if not raw_copi:
            return []

        # Normalize list of raw entries, multiple co-PIs separated by ; 
        if isinstance(raw_copi, list):
            entries = [str(e).strip() for e in raw_copi if e]
        else: 
            entries = [e.strip() for e in str(raw_copi).split(';') if e.strip()]

        names = []
        for entry in entries: # dropping any email token
            tokens = [t for t in entry.split() if '@' not in t]
            if not tokens:
                continue
            raw_name = ' '.join(tokens)
            normalized = self.normalize_name(raw_name)
            if normalized:
                names.append(normalized)
        return names

    def extract_keywords_ner(self, text): 
        """
        Extracting keywords from text using spaCy NER

        Extracts:
        - ORG - organizations
        - GPE - geopolitical places/entities
        - PRODUCT - products/technologies
        - NORP - nationalities/groups
        - Key noun and noun phrases 

        Args: 
            String text : text to extract keywords from
        Returns: 
            List keywords : a list of keywords
        """
        if not text or not self.nlp:
            return []
        
        doc = self.nlp(text[:2000])
        keywords = set()

        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE', 'PRODUCT', 'NORP', 'FAC', 'LOC']:
                clean = ent.text.strip().lower()
                # Clean the entity text, filter out common words
                if clean not in self._COMMON_WORDS and len(clean) > 2: 
                    keywords.add(clean)

        # Extract noun chunks (concepts)
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in ('NOUN', 'PROPN'): 
                # filter individual tokens 
                clean_tokens = [token.text for token in chunk
                    if token.pos_ in ('NOUN', 'PROPN', 'ADJ') 
                    and not token.is_stop and not token.is_punct 
                    and len(token.text)> 2 
                    and token.text.lower() not in self._COMMON_WORDS
                ]
                if clean_tokens: 
                    chunk_text = ' '.join(clean_tokens).strip().lower()
                    if 3 < len(chunk_text) < 40 and chunk_text not in self._COMMON_WORDS:
                        keywords.add(chunk_text)

        return list(keywords)[:8]
     
    def extract_keywords_simple(self, text): 
        """
        Extracting keywords from text (in this case, the abstract)

        Args: 
            String text : text to extract keywords from
        Returns: 
            List keywords : a list of keywords
        """
        words = text.lower().split() 
        keywords = [w for w in words if len(w) > 5 and w not in self._COMMON_WORDS]
        # return the first 10 keywords, making sure they're not duplicates, and convert back to list
        return list(set(keywords[:10]))
    
    def extract_keywords(self, text):
        """
        Puts all keyword extraction together.
        Use NER if available, and use simple if necessary
        """
        # return self.extract_keywords_ner(text)
        if self.nlp: 
            return self.extract_keywords_ner(text)
        else: 
            return self.extract_keywords_simple(text)

    def add_award(self, award):
        """
        Add a single award and its relationships to the graph.

        Args: 
            Dictionary award : award data from the NSF API's response. 
        """
        # Extract information from single award and save to identifiers
        award_id = award.get('id', 'Unknown')
        raw_pi_name = award.get('pdPIName', 'Unknown PI')
        raw_institution = award.get('awardeeName', 'Unknown Institution')
        program = award.get('fundProgramName', 'Unknown Program')
        amount = award.get('estimatedTotalAmt', 0)
        start_date = award.get('startDate', 'N/A')
        abstract = award.get('abstractText', '')

        # coPI key varies slightly
        raw_copi = (award.get('coPDPI') or award.get('coPIName') or award.get('coPI') or award.get('coPrincipalInvestigator'))

        # Normalize names 
        pi_name = self.normalize_name(raw_pi_name)
        copi_names = self.parse_copi_names(raw_copi)
        institution = self.normalize_name(raw_institution)

        # Skip if award already exists
        if award_id in self.award_ids:
            return
        self.award_ids.add(award_id)

        # Add award node - and award details
        self.graph.add_node(
            f"Award_{award_id}",
            type = 'Award',
            id = award_id,
            program = program,
            amount = amount,
            start_date = start_date,
            abstract = abstract, 
            copi_count = len(copi_names)
        )
        
        # Add PI Node
        if pi_name not in self.pi_names:
            self.pi_names.add(pi_name)
            self.graph.add_node(pi_name, type='PI', name=pi_name)

        # Add Institution node
        if institution not in self.institution_names:  
            self.institution_names.add(institution)
            self.graph.add_node(institution, type='Institution', name=institution)

        # Add edges (relationships)
        self.graph.add_edge(pi_name, f"Award_{award_id}", relationship='investigates')
        self.graph.add_edge(institution, f"Award_{award_id}", relationship='hosts')
        self.graph.add_edge(pi_name, institution, relationship='affiliated_with')

        # Add copi Node + edges 
        for copi_name in copi_names:
            if not copi_name or copi_name == pi_name:
                continue   # skip blank
 
            # Add copi node 
            if copi_name not in self.copi_names and copi_name not in self.pi_names:
                self.copi_names.add(copi_name)
                self.graph.add_node(copi_name, type='Co-PI', name=copi_name)
                # If the same person is both PI and copi on different awards we keep existing node but keep its type as PI 
                if copi_name not in self.pi_names:
                    # PI somewhere else, just track name 
                    self.copi_names.add(copi_name)
 
            # copi & award 
            self.graph.add_edge(copi_name, f"Award_{award_id}", relationship='co_investigates')
            # copi and Institution (same award inst)
            self.graph.add_edge(copi_name, institution, relationship='affiliated_with')
            # copi collaboration edge
            self.graph.add_edge(pi_name, copi_name, relationship='collaborates_with')

        # Extract topic and keywords using extract_keywords
        keywords = self.extract_keywords(abstract)

        # Further limiting amount of keywords used
        for key in keywords:
            topicword = f"Topic_{key.replace(' ', '_')}" # Clean up spaces
            if not self.graph.has_node(topicword):
                self.graph.add_node(topicword, type = 'Topic')
            self.graph.add_edge(f"Award_{award_id}", topicword, relationship = 'focuses on')

    def get_awards_by_topic(self, topic_keyword):
        """
        Find all awards related to a topic
        
        Args:
            String topic_keyword: Topic to search for
            
        Returns:
            list: Award node IDs
        """
        topic_id = f"Topic_{topic_keyword.replace(' ', '_')}"
        
        if topic_id not in self.graph:
            return []
        
        # Get all neighbors that are awards
        return [n for n in nx.neighbors(self.graph, topic_id) 
                if n.startswith('Award_')]

    def load_query_results(self, query, max_awards = 100): 
        """
        Query the NSF API and load the responses into the knowledge graph.

        Args: 
            String query: The natural language query
            Int max_awards: the maximum number of awards to load (default 100)
        """
        # Query the NSF API, use the tool
        params, results = self.agent.execute_agent(query)

        if not results:
            print("No results found.")
            return
        
        awards = results['response'].get('award',[]) # Needing the response key
        # add each award to the graph, so that it's under the max awards
        for award in awards[:max_awards]:
            self.add_award(award)

        # Get the number of awards you loaded, either max awards or the length - whichever is lower. 
        number_loaded = min(len(awards), max_awards)
        # Print number of awards loaded and then the updated number of nodes and edges.
        print(f"Loaded {number_loaded} awards into the knowledge graph.")
        print(f"The graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

        # Print deduplication stats
        print(f"Unique PIs: {len(self.pi_names)}")
        print(f"Unique Co-PIs: {len(self.copi_names)}")          
        print(f"Unique Institutions: {len(self.institution_names)}")
        print(f"Unique Awards: {len(self.award_ids)}")

    def get_pi_awards(self, pi_name): 
        """
        Get all awards of a PI 
        """
        # in case there is are no pi's
        if pi_name not in self.graph:
            return []
        
        # Get the neighbors of the PI node which start with "Award_"
        return [n for n in nx.neighbors(self.graph, pi_name)
            if n.startswith('Award_')]

    def get_copi_awards(self, copi_name):
        """Get all awards where this person is a co-pi."""
        # in case there is are no copi's
        if copi_name not in self.graph:
            return []
        
        award_nodes = []
        for n in nx.neighbors(self.graph, copi_name):
            if n.startswith('Award_'):
                edge_data = self.graph.edges[copi_name, n]
                if edge_data.get('relationship') == 'co_investigates':
                    award_nodes.append(n)
        return award_nodes
    
    def get_collaborators(self, pi_name):             
        """Get all people (pi/copi) this person has collaborated with."""
        if pi_name not in self.graph:
            return []
        collabs = []
        # Pull everyone with a collaborative relationship 
        for n in nx.neighbors(self.graph, pi_name):
            edge_data = self.graph.edges[pi_name, n]
            if edge_data.get('relationship') == 'collaborates_with':
                collabs.append(n)
        return collabs

    def get_institution_pis(self, institution_name): 
        """
        Get all PIs at an insitution 
        """
        # in case there are no institution names
        if institution_name not in self.graph:
            return []
        
        # Get node types (get attribute of type)
        node_types = nx.get_node_attributes(self.graph, 'type')
        
        # Get the neighbors for the institution name, neighbors of type PI
        return [n for n in nx.neighbors(self.graph, institution_name)
            if node_types.get(n) == 'PI']
    
    def get_deduplication_stats(self):
        return {
            'unique_pis': len(self.pi_names),
            'unique_copis': len(self.copi_names),
            'unique_institutions': len(self.institution_names),
            'unique_awards': len(self.award_ids),
            'total_nodes': nx.number_of_nodes(self.graph),
            'total_edges': nx.number_of_edges(self.graph)
        }

    def get_graph_info(self):
        """
        Get statistics and information about the graph, and printing the results.
        """
        # Dictionary of values for the node attribute 'type'
        type_attributes = nx.get_node_attributes(self.graph, 'type')
        
        # Dictionary of node types and how many occurences
        node_types = {}
        for type_val in type_attributes.values(): 
            # Get values and add one if found
            node_types[type_val] = node_types.get(type_val, 0) + 1

        # Print the summary 
        print(f"Total Nodes: {nx.number_of_nodes(self.graph)}")
        print(f"Total Edges: {nx.number_of_edges(self.graph)}")
        print(f"Graph Density: {nx.density(self.graph)}")
        print(f"Node types: ")
        for type, count in node_types.items():
            print(f"   {type}: {count}")
        print()

        # Print deduplication stats:
        stats = self.get_deduplication_stats()
        print(f"Unique PIs: {stats['unique_pis']}")
        print(f"Unique Institutions: {stats['unique_institutions']}")
        print(f"Unique Awards: {stats['unique_awards']}")

        # Return dictionary of node_types
        return node_types

if __name__ == "__main__":

    # Create kg 
    kg = KGBuilder()

    # Load data 
    kg.load_query_results("Environmental research grants in Memphis, TN over 10,000", max_awards = 15)
    kg.load_query_results("Cognitive science research at The Ohio State University", max_awards = 15)

    # Display graph info
    kg.get_graph_info()

    # Get all PI's from the graph
    node_types = nx.get_node_attributes(kg.graph, 'type')
    pis = [node for node, node_type in node_types.items() if node_type == 'PI']

    # Take 3 PI's and get (and print) the first three of their awards.
    if pis:
        ex_pis = pis[:3]
        for pi in ex_pis: 
            print(f"Awards for {pi}")
            awards = kg.get_pi_awards(pi)
            for award in awards[:3]:
                print(f"   {award}")
            print()
                    