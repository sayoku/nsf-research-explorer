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
    
    # TODO: load from query - method to query NSF API and load results into graph

    def get_pi_awards(self, pi_name): 
        """
        Get all awards of a PI 
        """
        if pi_name not in self.graph:
            return []
        
        # Get the neighbors of the PI node which start with "Award_"
        return [n for n in nx.neighbors(self.graph, pi_name)
            if n.startswith('Award_')]

    def get_institution_pis(self, institution_name): 
        """
        Get all PIs at an insitution 
        """
        if institution_name not in self.graph:
            return []
        
        # Get node types
        node_types = nx.get_node_attributes(self.graph, 'type')
        
        # Get the neighbors
        return [n for n in nx.neighbors(self.graph, institution_name)
            if node_types.get(n) == 'PI']

    # TODO: find similar PIs - list of PIs in similar topics or at the same insitution

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
    agent = NSFAgent()
    query = "Find water research grants in Tennessee at UT Knoxville."
    params, results = agent.execute_agent(query)
    if results: 
        # Example of working with results data 
        total = results['response']['metadata'].get('totalCount',0)
        print("Found {total} matching awards".format(total=total))

    # This will output the summary 
    # print(agent.complete_reply(query, results))

    # TODO: test everything!
