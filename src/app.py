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
    **Explore :rainbow[NSF grants] using natural language queries and knowledge graph visualization** 

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

    if st.button("Send snow!"):
        st.snow()

# Main content
if st.session_state.loaded == True:
    # Tabs for different info
    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "PIs", "Institutions", "Knowledge Graph"])

    # tab1
    with tab1:
        st.header("Knowledge graph overview and summary")
        # Get stats and organize them into columns
        stats = st.session_state.kg.get_deduplication_stats()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Nodes", nx.number_of_nodes(st.session_state.kg.graph))
        with col2:
            st.metric("Total Edges", nx.number_of_edges(st.session_state.kg.graph))
        with col3:
            density = nx.density(st.session_state.kg.graph)
            # show as 4-decimal float 
            st.metric("Graph Density", f"{density:.4f}")
        with col4:
            st.metric("Unique PIs", stats['unique_pis'])

        st.subheader("Node type breakdown")
        # Use get_graph_info to get counts of types
        type_counts = st.session_state.kg.get_graph_info()
        # Show as bar chart
        st.bar_chart(type_counts)

    # tab2
    with tab2:
        st.header("Principal Investigators")

        # Get all PI's from the graph
        node_types = nx.get_node_attributes(st.session_state.kg.graph, 'type')
        pis = [node for node, node_type in node_types.items() if node_type == 'PI']

        # If there are PI's, 
        if pis:
            selected_pi = st.selectbox("Select a PI:", pis)


            if selected_pi:
                st.subheader(f"Awards for {selected_pi}")
                awards = st.session_state.kg.get_pi_awards(selected_pi)

                if awards:
                    st.write(f"**Total Awards:** {len(awards)}")
                    for award in awards:
                        with st.expander(f"{award}"):
                            award_data = st.session_state.kg.graph.nodes[award]
                            st.write(f"**Program:** {award_data.get('program', 'N/A')}")
                            st.write(f"**Amount:** {award_data.get('amount', 0)}")
                            st.write(f"**Start Date:** {award_data.get('start_date', 'N/A')}")
                            st.write(f"**Abstract:** {award_data.get('abstract', 'N/A')}")
                else:
                    st.info("No awards found for this PI")
    # tab3
    with tab3:
        st.header("Institutions")

        node_types = nx.get_node_attributes(st.session_state.kg.graph, 'type')
        institutions = [node for node, node_type in node_types.items() if node_type == 'Institution']

        # If there are insitutions, 
        if institutions:
            selected_inst = st.selectbox("Select an Institution:", institutions)


            if selected_inst:
                st.subheader(f"PI's at {selected_inst}")
                # Pull institution PIs from KG Builder
                inst_pis = st.session_state.kg.get_institution_pis(selected_inst)

                if inst_pis:
                    st.write(f"**Total PIs:** {len(inst_pis)}")
                    
                    for pi in inst_pis:
                        # Use get_pi_awards to get award count for each PI
                        pi_awards = st.session_state.kg.get_pi_awards(pi)
                        
                        with st.expander(f"👤 {pi} ({len(pi_awards)} award(s))"):
                            if pi_awards:
                                for award in pi_awards:
                                    award_data = st.session_state.kg.graph.nodes[award]
                                    st.write(f"**{award}**")
                                    st.write(f"  - Amount: {award_data.get('amount', 0)}")
                                    st.write(f"  - Program: {award_data.get('program', 'N/A')}")
                                    st.divider()
                            else:
                                st.write("No award details available")
                else:
                    st.info("No institutions found in the current graph")

    # tab4
    with tab4:
        st.header("Knowledge graph visualization")

        st.markdown(
            """ 
            A work in progress: currently using NetworkX and Matpotlib.pyplot

            """
        )        

        # Visualization options
        layout_type = st.selectbox(
            "Select layout:",
            ["Spring", "Circular", "Kamada-Kawai"]
        )
        
        node_size = st.slider("Node size:", 100, 1000, 300)
        
        if st.button("Generate Visualization"):
            with st.spinner("Generating graph visualization..."):
                fig, ax = plt.subplots(figsize=(14, 10))
                
                # Choose layout and use according networkX layout
                if layout_type == "Spring":
                    pos = nx.spring_layout(st.session_state.kg.graph)
                elif layout_type == "Circular":
                    pos = nx.circular_layout(st.session_state.kg.graph)
                else:
                    pos = nx.kamada_kawai_layout(st.session_state.kg.graph)
                
                # Color nodes by type
                node_types = nx.get_node_attributes(st.session_state.kg.graph, 'type')
                color_map = {
                    'PI': '#CF9FFF',
                    'Institution': '#4ECDC4',
                    'Award': '#6495ED',
                    'Topic': '#E37383'
                }
                # Loop through each node in the graph, and grab it's type, if not found, return ''. 
                # Get the color for the type, default is the teal color.
                node_colors = [color_map.get(node_types.get(node, ''), '#95E1D3') 
                             for node in st.session_state.kg.graph.nodes()]
                
                # Draw graph
                nx.draw(
                    st.session_state.kg.graph,
                    pos,
                    node_color=node_colors,
                    node_size=node_size,
                    with_labels=True,
                    font_size=6,
                    font_weight='bold',
                    ax=ax,
                    edge_color='#CCCCCC',
                    alpha=0.7
                )
                
                # Legend
                legend_elements = [
                    plt.Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color, markersize=10, label=node_type)
                    for node_type, color in color_map.items()
                ]
                ax.legend(handles=legend_elements, loc='lower right')
                
                st.pyplot(fig)

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