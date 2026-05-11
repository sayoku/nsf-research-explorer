import streamlit as st
import steamlit.components.v1 as components
import networkx as nx
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent.tool import NSFAgent
from kgraph.mem import KGBuilder
from kgraph.query import KGQueryAgent 

# pyvis integrates with networkx
def build_pyvis_html(graph: nx.Graph, height: int = 600, physics: bool = True, node_size: int = 20) -> str:
    """
    Convert a networkx graph to a pvis html string
    Node colors correspond to type, clicking a node shows all attributes
    Returns full HTML string for st.components.v1.html()
    """
    # Import pyvis
    try:
        from pyvis.network import Network
    except ImportError:
        return  "<p style='color:red'>pyvis is not installed. Run: pip install pyvis</p>"

    import tempfile, pathlib

    # Colors match current matplotlib colors, basic and highlighted 
    COLORS = {
        "PI":          {"background": "#CF9FFF", "border": "#9B59D0", "highlight": {"background": "#E0C0FF", "border": "#7B3FB0"}},
        "Institution": {"background": "#4ECDC4", "border": "#2BA39B", "highlight": {"background": "#80E8E2", "border": "#1A8077"}},
        "Award":       {"background": "#6495ED", "border": "#3A6BC0", "highlight": {"background": "#A0B8F5", "border": "#2A55A0"}},
        "Topic":       {"background": "#E37383", "border": "#B84055", "highlight": {"background": "#F0A0B0", "border": "#902030"}},
    }
    # Example: Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net = Network(height=f"{height}px", width="100%", bgcolor="#0F1117", font_color="#E8E8E8", directed=False)

    # make a copy of the graph 
    g = graph.copy()
    for node, data in g.nodes(data=True):
        ntype = data.get("type", "")

        # title, rendered as html on hover
        lines = [f"<b>{node}</b>", f"<i>Type: {ntype}</i>", "<hr style='margin:4px 0'>"] 
        for k, v in data.items():
            if k in ("type", "title", "label", "color", "size"):
                continue
            if k == "abstract" and v:
                chunk = str(v)[:300] + ("…" if len(str(v)) > 300 else "")
                lines.append(f"<b>{k}:</b> {chunk}")
            elif k == "amount" and v:
                lines.append(f"<b>{k}:</b> ${int(v):,}")
            elif v:
                lines.append(f"<b>{k}:</b> {v}")
        g.nodes[node]["title"] = "<br>".join(lines)

        # label, visible text on node
        label = node
        if node.startswith("Award_"):
            label = node.replace("Award_", "")[:12] # bye bye yucky
        elif node.startswith("Topic_"):
            label = node.replace("Topic_", "").replace("_", " ") # bye bye other yucky
        elif len(node) > 22:
            label = node[:20] + "…"
        g.nodes[node]["label"] = label

        g.nodes[node]["color"] = COLORS.get(ntype)
        g.nodes[node]["size"] = node_size if ntype != "Topic" else max(node_size - 6, 8)
        
    # build network and load using from_nx()
    net = Network(height=f"{height}px", width="100%", bgcolor="#0F1117", font_color="#E8E8E8", directed=False)
    net.from_nx(g) # Translate nodes and edges

    # Use physics thru barnes_hut()
    if physics: 
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120, spring_strength=0.04, damping=0.09)
    else:
        net.toggle_physics(False)

    # generate html
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        tmp_path = f.name
    net.save_graph(tmp_path)
    html = pathlib.Path(tmp_path).read_text(encoding="utf-8")
    os.unlink(tmp_path)
    return html

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
if 'subgraph' not in st.session_state:          
    st.session_state.subgraph = None  

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
                # st.session_state.kg = KGBuilder()  # Resetting
                st.session_state.kg.load_query_results(query, max_awards=max_awards)
                st.session_state.loaded = True
                st.success(f"Loaded {max_awards} awards!")
        else:
            st.warning("Please enter a search query")

    # Add a reset button below Search
    if st.button("Reset Graph", type="secondary"):
        st.session_state.kg = KGBuilder()
        st.session_state.loaded = False
        st.success("Graph cleared!")

    if st.button("Send snow!"):
        st.snow()

    st.header("Subgraph Query")
    nl_query = st.text_input("Ask about the graph:", placeholder="e.g., Show water research")
    if st.button("Query Graph"):
        agent = KGQueryAgent(st.session_state.kg.graph)
        subgraph, explanation, nodes = agent.subquery(nl_query)
            
        st.success(explanation)
        st.info(f"Found {len(nodes)} relevant nodes")
            
        # Store subgraph in session
        st.session_state.subgraph = subgraph


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
                
                # Display subgraph
                if 'subgraph' in st.session_state and st.session_state.subgraph is not None: 
                    st.subheader("Subgraph Query Result")
                if len(st.session_state.subgraph.nodes()) > 0:
                    fig2, ax2 = plt.subplots(figsize=(12, 8))
                    
                    pos2 = nx.spring_layout(st.session_state.subgraph)
                    
                    node_types = nx.get_node_attributes(st.session_state.subgraph, 'type')
                    color_map = {
                        'PI': '#CF9FFF',
                        'Institution': '#4ECDC4',
                        'Award': '#6495ED',
                        'Topic': '#E37383'
                    }
                    node_colors = [color_map.get(node_types.get(node, ''), '#95E1D3')
                                for node in st.session_state.subgraph.nodes()]
                    
                    # Draw graph
                    nx.draw(
                    st.session_state.subgraph,
                    pos2,
                    node_color=node_colors,
                    node_size=node_size,
                    with_labels=True,
                    font_size=6,
                    font_weight='bold',
                    ax=ax2,
                    edge_color='#CCCCCC',
                    alpha=0.7
                    )
                    st.pyplot(fig2)
                else: 
                    st.warning("subgraph is empty - no nodes matched your query")



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