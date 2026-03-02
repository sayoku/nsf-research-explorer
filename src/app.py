import streamlit as st
#import networkx as nx
import matplotlib.pyplot as plt
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent.tool import NSFAgent
from kgraph.mem import KGBuilder

# Configure page
st.set_page_config(page_title="NSF Research Explorer", layout="wide")

# Add title and desc using markdown
st.title("NSF Research Award Explorer")
st.markdown(
    """ 
    **Explore :rainbow[NSF grants] NSF grants using natural language queries and visualize the knowledge graph** 

    """
)

# Yippee!
if st.button("Send balloons!"):
    st.balloons()

# Manage sessions, avoiding duplicates
if 'kg' not in st.session_state:
    st.session_state.kg = KGBuilder()
if 'loaded' not in st.session_state:
    st.session_state.loaded = False

# Add sidebar for query
with st.sidebar:
    st.header("Query Settings")

    # Natural language user query
    query = st.text_input(
        "Enter your search query:",
        placeholder="e.g., Water research in Tennessee",
        help="Use natural language to search for NSF grants"
    )

    # How many awards to use - still deciding on the best way
    max_awards = st.slider( # Could also use st.text-input() 
        "Maximum awards to load:",
        min_value=5,
        max_value=100,
        value=10,
        step=5
    )