import streamlit as st
import networkx as nx
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
    
    #Search button, which queries the NSF API using KGBuilder
    if st.button("Search", type="primary"):
        if query:
            with st.spinner("Searching NSF database..."):
                st.session_state.kg = KGBuilder()  # Resetting
                st.session_state.kg.load_query_results(query, max_awards=max_awards)
                st.session_state.loaded = True
                st.success(f"Loaded {max_awards} awards!")
        else:
            st.warning("Please enter a search query")

# Main content
if st.session_state.loaded == True:
    # Tabs for different info
    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "PIs", "Institutions", "Knowledge Graph"])

    # tab1
    with tab1:
        st.header("Knowledge graph overview and summary")
        # Get stats and organize them into columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Nodes", nx.number_of_nodes(st.session_state.kg.graph))
        with col2:
            st.metric("Total Edges", nx.number_of_edges(st.session_state.kg.graph))
        with col3:
            density = nx.density(st.session_state.kg.graph)
            # show as 4-decimal float 
            st.metric("Graph Density", f"{density:.4f}")

    # tab2
    with tab2:
        st.header("Principal Investigators")

    # tab3
    with tab3:
        st.header("Institutions")

    # tab4
    with tab4:
        st.header("Knowledge graph visualization")

else:
    st.info("Enter a query in the sidebar to get started")

    # Example queries for funsies
    st.subheader("Example Queries:")
    examples = [
        "Water research in Tennessee",
        "Cognitive science at Ohio State University",
        "Grants over $100,000 in California",
        "Environmental research in New York",
        "Machine learning research"
    ]
    
    for example in examples:
        st.code(example)