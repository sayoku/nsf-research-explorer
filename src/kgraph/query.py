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
        response = ""
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
                if min_amount <= amount <= max_amount: # check if it's within bounds
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
        return self.find_neighbors(inst_node, max_depth=2)
    
    def query (self, user_query:str) -> tuple: 
        """Process natural language query and return relevant subgraph
        Args:
            user_query (str): Natural language query 
        Returns: 
            tuple: (subgraph, explanation, nodes_of_interest)
        """
        # Parse query
        parsed = self.parse_query(user_query)
