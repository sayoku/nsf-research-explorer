import networkx as nx
from src.agent.tool import NSFAgent, query_nsf_api
import json

class KGBuilder():
    """
    Knowledge graph builder for NSF Awards using NetworkX.
    Transforms data into a connected graph of PIs, Institutions, and Awards.
    """

    def __init__(self):
        self.graph = nx.Graph()
        self.agent = NSFAgent()

    def add_award(self, award):
        """
        Add a single award and its relationships to the graph.

        Args: 
            Dictionary award : award data from the NSF API's response. 
        """
        # Extract information from single award and save to identifiers
        award_id = award['response'].get('id', 'Unknown')
        pi_name = award['response'].get('pdPIName', 'Unknown PI')
        institution = award['response'].get('awardeeName', 'Unknown Institution')
        program = award['response'].get('fundProgramName', 'Unknown Program')
        amount = award['response'].get('estimatedTotalAmt', 0)
        start_date = award['response'].get('startDate', 'N/A')
        abstract = award['response'].get('abstractText', '')

        # Add award node - and award details
        self.graph.add_node(
            f"Award_{award_id}",
            type = 'Award',
            id = award_id,
            program = program,
            amount = amount,
            start_date = start_date,
            abstract = abstract[:200]
        )
        # Add PI Node
        if not self.graph.has_node(pi_name):
            self.graph.add_node(
                pi_name,
                type = 'PI',
                name = pi_name
            )
        # Add institution node 
        if not self.graph.has_node(institution):
            self.graph.add_node(
                institution,
                type='Institution',
                name=institution
            )

        # Add edges (relationships)
        self.graph.add_edge(pi_name, f"Award_{award_id}", relationship='investigates')
        self.graph.add_edge(institution, f"Award_{award_id}", relationship='hosts')
        self.graph.add_edge(pi_name, institution, relationship='affiliated_with')

        # Extract topic and keywords using extract_keywords

        keywords = self.extract_keywords(self, abstract)
        # Further limiting amount of keywords used
        for key in keywords[:5]:
            topicword = f"Topic_{key}"
            if not self.graph.has_note(topicword):
                self.graph.add_node(
                    topicword,
                    type = 'Topic'
                )
        self.graph.add_edge(topicword, f"Award_{award_id}", relationship = 'focuses on')


    def extract_keywords(self, text): 
        """
        Extracting keywords from text (in this case, the abstract)

        Args: 
            String text : text to extract keywords from
        Returns: 
            List keywords : a list of keywords
        """
        # There probably is a better way to do this, still thinking on it. 
        common = ["research", "study", "investigation", "development", "analysis"]
        words = text.lower().split() 
        keywords = [w for w in words if len(w) > 5 and w not in common]
        # return the first 10 keywords, making sure they're not duplicates, and convert back to list
        return list(set(keywords[:10]))

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
        
        awards = results['response'].get('award',[])
        # add each award to the graph, so that it's under the max awards
        for award in awards[:max_awards]:
            self.add_award(award)

        # Get the number of awards you loaded, either max awards or the length - whichever is lower. 
        number_loaded = min(len(awards), max_awards)
        # Print number of awards loaded and then the updated number of nodes and edges.
        print(f"Loaded {number_loaded} awards into the knowledge graph.")
        print(f"The graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

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

    def get_graph_info(self):
        """
        Get statistics and information about the graph, and printing the results.
        """
        # Dictionary of values for the node attribute 'type'
        type_attributes = nx.get_node_atributes(self.graph, 'type')
        
        # Dictionary of node types and how many occurences
        node_types = {}
        for type_val in type_attributes.values(): 
            # Get values and add one if found
            node_types[type_val] = type_val.get(type_val, 0) + 1

        # Print the summary 
        print(f"Total Nodes: {nx.number_of_nodes(self.graph)}")
        print(f"Total Edges: {nx.number_of_edges(self.graph)}")
        print(f"Graph Density: {nx.density(self.graph)}")
        print(f"Node types: ")
        for type, count in node_types.items():
            print(f"   {type}: {count}")

        # Return dictionary of node_types
        return node_types

if __name__ == "__main__":

    # Create kg 
    kg = KGBuilder()

    # Load data 
    kg.load_from_query("Water research grants in Tennessee at UT Knoxville.", max_awards = 10)

    # Display graph info
    kg.get_graph_info()

    # Get all PI's from the graph
    node_types = nx.get_node_attributes(kg.graph, 'type')
    pis = [node for node, node_type in node_types.items() if node_types == 'PI']

    # Take a PI and get (and print) the first three of their awards.
    if pis:
        ex_pi = pis[0]
        print(f"Awards for {ex_pi} \n")
        awards = kg.get_pi_awards
        for award in awards[:3]:
            print(f"   {award}")

# TODO : test the methods and functionality