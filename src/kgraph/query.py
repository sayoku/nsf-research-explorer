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
