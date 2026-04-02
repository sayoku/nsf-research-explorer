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
            
