import networkx as nx
from anthropic import Anthropic
import os
import sys
import json 
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Try to get API key from environment variable first
api_key = os.getenv("ANTHROPIC_API_KEY")

#  If running on Streamlit Cloud, check streamlit secrets
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
    except:
        pass

class KGQueryAgent():
    """
    Natural language query agent for an existing KG
    Translates user input into graph traversal operations
    Returns subgraphs
    """
    
    def __init__(self, graph: nx.Graph, api_key=None):
        """
        Args: 
            nx.Graph graph : loaded networkx graph from KGBuilder
            api_key : API Key
        """
        self.graph = graph
        self.client = Anthropic(api_key=api_key)

        self.system_prompt = """
        You are a knowledge graph query assistant. Your job is to translate natural language queries into structured graph operations.
        The knowledge graph has these node types:
        - PI: Principal Investigators (researchers)
        - Institution: Universities and research organizations
        - Award: Research grants/awards
        - Topic: Research topics and keywords

        Available graph operations:
        1. find_by_type: Find all nodes of a specific type
        2. find_by_name: Find nodes with names matching a pattern
        3. find_neighbors: Find all neighbors of a node
        4. find_by_topic: Find awards related to a topic
        5. find_by_amount: Find awards within a funding range
        6. find_pi_awards: Find all awards for a specific PI
        7. find_institution_pis: Find all PIs at an institution
        8. find_copi_awards: Find all awards where a specific person is a co-investigator
        9. find_collaborators: Find all collaborators (PIs and COPIs) of a specific person

        Output ONLY a JSON object with this structure:
        {
        "operation": "operation_name",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        },
        "explanation": "Brief explanation of what you're doing"
        }

        Examples:

        Query: "Show me all water research"
        Output: {"operation": "find_by_topic", "parameters": {"topic": "water"}, "explanation": "Finding awards related to water research"}

        Query: "What awards does John Smith have?"
        Output: {"operation": "find_pi_awards", "parameters": {"pi_name": "john smith"}, "explanation": "Finding all awards for PI John Smith"}

        Query: "Show research at Ohio State"
        Output: {"operation": "find_institution_pis", "parameters": {"institution": "ohio state"}, "explanation": "Finding all PIs at Ohio State University"}

        Query: "Awards over $500,000"
        Output: {"operation": "find_by_amount", "parameters": {"min_amount": 500000}, "explanation": "Finding awards with funding over $500,000"}

        Query: "Who are the co-investigators on award 1234567?"
        Output: {"operation": "find_award_copis", "parameters": {"award_id": "1234567"}, "explanation": "Finding all co-PIs on award 1234567"}
        
        Query: "Who has John Smith collaborated with?"
        Output: {"operation": "find_collaborators", "parameters": {"person_name": "john smith"}, "explanation": "Finding all collaborators of John Smith"}

        Query: "Water research at Vanderbilt"
        Output: 
        {
        "operations": [
            {"operation": "find_by_topic", "parameters": {"topic": "water"}},
            {"operation": "find_institution_pis", "parameters": {"institution": "vanderbilt"}}
        ],
        "explanation": "Finding water research awards at Vanderbilt by intersecting topic and institution results"
        }

        Now process the user's query.
        """

    def parse_query(self, query: str) -> dict: 
        """Use claude to parse the natural language query into operations
            
        Args: 
            String query: Natural language query from user
            
        Returns:
            Dict : parsed query with operations and paramters
        """
        message = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system = self.system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        # This is the raw response
        response_raw = message.content[0].text
        response = response_raw
        # Take the json and find the start and end to the information we want
        if "```json" in response_raw:
            start = response_raw.find("```json") + 7
            end = response_raw.find("```", start)
            # slice the string and strip in case
            response = response_raw[start:end].strip() 
        elif "```" in response_raw:
            start = response_raw.find("```") + 3
            end = response_raw.find("```", start)
            # slice the string and strip in case
            response = response_raw[start:end].strip() 
            
        # Parse json into python dictionary
        params = json.loads(response)
        return params
        
    # Operation #1 
    def find_by_type(self, node_type: str) -> list:
        """ Finds all nodes of a specific type"""
        # Get node types (get attribute of type)
        node_types = nx.get_node_attributes(self.graph, 'type')
        return [n for n, ntype in node_types.items() if ntype.lower() == node_type.lower()]
        
    # Operation #2
    def find_by_name(self, name_pattern: str) -> list:
        """Find nodes with names matching a pattern (not case sensitive)"""
        pattern = name_pattern.lower()
        matching_nodes = []
            
        for node in self.graph.nodes():
            if pattern in str(node).lower(): #if the pattern is found, add the matching nodes to the list
                matching_nodes.append(node) 
            
        return matching_nodes
        
    # Operation #3
    def find_neighbors(self, node: str, max_depth: int = 1) -> list:
        """Find all neighbors up to a max depth"""
        if node not in self.graph:
            return[]
        neighbors = {node}
        current_level = {node}

        for i in range(max_depth):
            next_level = set() # Empty set for next level
            for node in current_level: # For each node in current level, 
                next_level.update(nx.neighbors(self.graph, node)) #add it's neighbors to the next layer
            neighbors.update(next_level) # Add new nodes to total
            current_level = next_level # Move to the next level

        return list(neighbors)
    
    # Operation 4
    def find_by_topic(self, topic_keyword: str) -> list:
        """Find awards related to a topic"""
        # Match topic to keyword
        topic_nodes = []
        for node in self.graph.nodes():
            if node.startswith('Topic_') and topic_keyword.lower() in node.lower():
                topic_nodes.append(node)
        
        # Grab them awards
        award_nodes = set()
        for topic in topic_nodes:
            for neighbor in nx.neighbors(self.graph, topic):
                if neighbor.startswith('Award_'):
                    award_nodes.add(neighbor)
        
        # Return subgraph (topics + awards + connections)
        all_nodes = set(topic_nodes) | award_nodes
        for award in award_nodes:
            all_nodes.update(nx.neighbors(self.graph, award))
        
        return list(all_nodes)

    # Operation 5
    def find_by_amount(self, min_amount: int = 0, max_amount: int = float('inf')) -> list:
        """Find awards within a funding range."""
        matching_awards = []
        
        for node in self.graph.nodes():
            if node.startswith('Award_'): # Awards only 
                amount = self.graph.nodes[node].get('amount', 0)
                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    amount = 0
                if min_amount <= amount <= max_amount:
                    matching_awards.append(node)
        
        # Include PI and insitution connections
        all_nodes = set(matching_awards)
        for award in matching_awards:
            all_nodes.update(nx.neighbors(self.graph, award))
        
        return list(all_nodes)
    
    # Operation 6
    def find_pi_awards(self, pi_name: str) -> list:
        """Find all awards for a specific PI."""
        pi_node = None       # Find PI node 
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node] # pull data and check type and if it matches
            if node_data.get('type') == 'PI' and pi_name.lower() in str(node).lower():
                pi_node = node 
                break
        
        if not pi_node:
            return []
        
        # Get all neighbors
        return self.find_neighbors(pi_node, max_depth=1)
    
    # Operation 7
    def find_institution_pis(self, institution_name: str) -> list:
        """Find all PIs at an institution."""
        inst_node = None # Find instiution node 
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            if node_data.get('type') == 'Institution' and institution_name.lower() in str(node).lower():
                inst_node = node
                break
        
        if not inst_node:
            return []
        
        # Get all neighbors
        return self.find_neighbors(inst_node, max_depth=1) # Just the PI 
    
    # Operation 8 
    def find_copi_awards(self, copi_name: str) -> list:
        """Find all awards where the person is a named copi"""
        copi_node = None
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            if (node_data.get('type') in ('Co-PI', 'PI') and
                    copi_name.lower() in str(node).lower()):
                copi_node = node
                break

        if not copi_node:
            return []
        
        award_nodes = set()
        for neighbor in nx.neighbors(self.graph, copi_node):
            if neighbor.startswith('Award_'):
                edge_data = self.graph.edges[copi_node, neighbor]
                if edge_data.get('relationship') == 'co_investigates':
                    award_nodes.add(neighbor)
 
        all_nodes = {copi_node} | award_nodes
        for award in award_nodes:
            all_nodes.update(nx.neighbors(self.graph, award))
        return list(all_nodes)

    # Operation 9 
    def find_collaborators(self, person_name: str) -> list:
        """Find all people a given person as collaborated with"""
        person_node = None
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            if (node_data.get('type') in ('PI', 'Co-PI') and
                    person_name.lower() in str(node).lower()):
                person_node = node
                break
        if not person_node:
            return []
        
        collab_nodes = set()
        for neighbor in nx.neighbors(self.graph, person_node):
            edge_data = self.graph.edges[person_node, neighbor]
            if edge_data.get('relationship') == 'collaborates_with':
                collab_nodes.add(neighbor)
 
        # Return the person, collaborators, and shared awards
        all_nodes = {person_node} | collab_nodes
        for collab in collab_nodes:
            for neighbor in nx.neighbors(self.graph, collab):
                if neighbor.startswith('Award_'):
                    edge_data = self.graph.edges[collab, neighbor]
                    if edge_data.get('relationship') in ('investigates', 'co_investigates'):
                        all_nodes.add(neighbor)
        return list(all_nodes)

    # Execute operations, since we end up with a json, I'm just going to do a bunch of if-elseifs 
    def execute_ops(self, operation: str, parameters:dict) -> list:
        # Returns nodes of interest in a list 
        if operation == "find_by_type":
            return self.find_by_type(parameters.get("node_type", ""))
        elif operation == "find_by_name":
            return self.find_by_name(parameters.get("name_pattern", ""))
        elif operation == "find_neighbors":
            return self.find_neighbors(parameters.get("node_name", ""), parameters.get("max_depth", 1))
        elif operation == "find_by_topic":
            return self.find_by_topic(parameters.get("topic", ""))
        elif operation == "find_by_amount":
            return self.find_by_amount(parameters.get("min_amount", 0), parameters.get("max_amount", float('inf')))
        elif operation == "find_pi_awards":
            return self.find_pi_awards(parameters.get("pi_name", ""))
        elif operation == "find_institution_pis":
            return self.find_institution_pis(parameters.get("institution", ""))
        elif operation == "find_copi_awards":                          
            return self.find_copi_awards(parameters.get("copi_name", ""))
        elif operation == "find_collaborators":                        
            return self.find_collaborators(parameters.get("person_name", ""))
        
        else:     
            return []
    
    def subquery (self, user_query:str) -> tuple: 
        """Process natural language query and return relevant subgraph
        Args:
            user_query (str): Natural language query 
        Returns: 
            tuple: (subgraph, explanation, nodes_of_interest)
        """
        # Parse query
        parsed = self.parse_query(user_query)
        
        # Do all the operations that are necessary. First is if there are multiple
        if "operations" in parsed: 
            result_sets = [] # set of results lol
            for op in parsed["operations"]: # for each op in the list of operations returned from claude
                nodes = self.execute_ops(op["operation"], op["parameters"]) # execute the operation 

                # If the op returned PIs, expand to their awards first 
                awards = set() 
                for n in nodes: # with each node
                    node_data = self.graph.nodes[n] # get the data of n 
                    if n.startswith("Award_"):
                        awards.add(n)
                    elif node_data.get('type') in ('PI', 'Co-PI', 'Institution', 'Topic'): # it's not an award, so get the type
                        for neighbor in nx.neighbors(self.graph, n):
                            if neighbor.startswith("Award_"):
                                awards.add(neighbor) # add the node's neighbors that are awards
                            # PIs connect to institutions, not awards directly 
                            # go one step further from PI neighbors
                            elif self.graph.nodes[neighbor].get('type') in ('PI', 'Co-PI'): # if the next neighbor is of type PI 
                                for neighbor2 in nx.neighbors(self.graph, neighbor): # grab the awards adjacent to PI
                                    if neighbor2.startswith("Award_"):
                                        awards.add(neighbor2)
                result_sets.append(awards)

            # Intersect award sets, then re-expand to include neighbors
            matching_awards = set.intersection(*result_sets) if result_sets else set() # unpack list of sets, return empty if result_sets is empty
            nodes_of_interest = set(matching_awards)
            for award in matching_awards:
                for neighbor in nx.neighbors(self.graph, award):
                    nodes_of_interest.add(neighbor)
                    # Go one more to catch institution nodes
                    for neighbor2 in nx.neighbors(self.graph, neighbor):
                        if self.graph.nodes[neighbor2].get('type') == 'Institution':
                            nodes_of_interest.add(neighbor2)
            nodes_of_interest = list(nodes_of_interest)
        else: 
            # Execute operation: 
            nodes_of_interest = self.execute_ops(parsed["operation"], parsed["parameters"])

        # Create subgraph
        if nodes_of_interest: 
            subgraph = self.graph.subgraph(nodes_of_interest).copy()
        else: 
            subgraph = nx.Graph() # New one lele
        return subgraph, parsed["explanation"], nodes_of_interest
    