import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent.tool import NSFAgent
from kgraph.mem import KGBuilder
from kgraph.query import KGQueryAgent 

@st.cache_resource
def load_spacy_model():
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        with st.spinner("Downloading spaCy language model (one-time setup)..."):
            from spacy.cli import download
            download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

# pyvis integrates with networkx
def build_pyvis_html(graph: nx.Graph, height: int = 600, physics: bool = True, node_size: int = 20) -> str:
    """
    Convert a networkx graph to a pvis html string
    Node colors correspond to type, clicking a node shows all attributes
    Clicking a PI, Insitution, or Award node navigates to the corresponding tab
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
        "Co-PI":       {"background": "#FFB347", "border": "#CC7A00", "highlight": {"background": "#FFD080", "border": "#AA6000"}},
        "Institution": {"background": "#4ECDC4", "border": "#2BA39B", "highlight": {"background": "#80E8E2", "border": "#1A8077"}},
        "Award":       {"background": "#6495ED", "border": "#3A6BC0", "highlight": {"background": "#A0B8F5", "border": "#2A55A0"}},
        "Topic":       {"background": "#E37383", "border": "#B84055", "highlight": {"background": "#F0A0B0", "border": "#902030"}},
    }

    # make a copy of the graph 
    g = graph.copy()
    node_titles = {} 

    for node, data in g.nodes(data=True):
        ntype = data.get("type", "")

        # build hover tooltip in html 
        # title, rendered as html on hover
        lines = [f"{node}", f"Type: {ntype}", "---"]
        for k, v in data.items():
            if k in ("type", "title", "label", "color", "size"):
                continue
            if k == "abstract" and v:
                chunk = str(v)[:200] + ("…" if len(str(v)) > 200 else "")
                lines.append(f"abstract: {chunk}")
            elif k == "amount" and v:
                lines.append(f"amount: ${int(v):,}")
            elif k == "copi_count" and v:
                lines.append(f"co-investigators: {v}")
            elif v:
                lines.append(f"{k}: {v}")
        node_titles[node] = "\n".join(lines)

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

     # Apply titles AFTER from_nx so they aren't overwritten
    for pyvis_node in net.nodes:
        nid = pyvis_node["id"]
        if nid in node_titles:
            pyvis_node["title"] = node_titles[nid]

    # Use physics thru barnes_hut()
    if physics: 
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120, spring_strength=0.04, damping=0.09)
    else:
        net.toggle_physics(False)

    net.set_options("""
    {
      "interaction": {
        "hover": true,
        "tooltipDelay": true
      }
    }
    """)

    # generate html
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        tmp_path = f.name
    net.save_graph(tmp_path)
    html = pathlib.Path(tmp_path).read_text(encoding="utf-8")
    os.unlink(tmp_path)

    tooltip_style = """
    <style>
    div.vis-tooltip {
        background-color: #1E2130 !important;
        color: #F0F0F0 !important;
        border: 1px solid #444 !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
        font-size: 13px !important;
        font-family: sans-serif !important;
        max-width: 420px !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        line-height: 1.5 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.5) !important;
    }
    </style>
    """
    html = html.replace("</head>", tooltip_style + "</head>")
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

nlp = load_spacy_model() # Cached, runs once

# Manage sessions, avoiding duplicates
if 'kg' not in st.session_state:
    st.session_state.kg = KGBuilder()
    st.session_state.kg.set_nlp(nlp)
if 'loaded' not in st.session_state:
    st.session_state.loaded = False
if 'subgraph' not in st.session_state:          
    st.session_state.subgraph = None  
if 'summary' not in st.session_state:
    st.session_state.summary = None

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
                st.session_state.summary = st.session_state.kg.load_query_results(query, max_awards=max_awards)
                st.session_state.loaded = True
                st.success(f"Loaded {max_awards} awards!")
        else:
            st.warning("Please enter a search query")

    # Add a reset button below Search
    if st.button("Reset Graph", type="secondary"):
        st.session_state.kg = KGBuilder()
        st.session_state.kg.set_nlp(nlp)
        st.session_state.loaded = False
        st.session_state.summary = None
        st.query_params.clear()
        st.success("Graph cleared!")

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "PIs", "Institutions", "Knowledge Graph", "Awards"])

    # tab1
    with tab1:
        st.header("Knowledge graph overview and summary")
        # Get stats and organize them into columns
        stats = st.session_state.kg.get_deduplication_stats()

        col1, col2, col3, col4, col5 = st.columns(5)
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
        with col5: 
            st.metric("Unique Co-PIs", stats['unique_copis'])

        st.subheader("Summary")
        if st.session_state.summary: 
            st.write(st.session_state.summary.replace("$", "\\$"))
        else: 
            st.info("Summary not available")

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
        copis = [node for node, node_type in node_types.items() if node_type == 'Co-PI']

        pi_tab, copi_tab = st.tabs([f"Lead PIs ({len(pis)})", f"Co-PIs ({len(copis)})"])

        with pi_tab: 
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
        with copi_tab: 
            if copis: 
                selected_copi = st.selectbox("Select a Co-PI:", copis)
                if selected_copi:
                    st.subheader(f"Awards where {selected_copi} is a Co-PI")
                    copi_awards = st.session_state.kg.get_copi_awards(selected_copi)
                    collaborators = st.session_state.kg.get_collaborators(selected_copi)
 
                    col_a, col_b = st.columns(2)
                    col_a.metric("Co-PI Awards", len(copi_awards))
                    col_b.metric("Collaborators", len(collaborators))
 
                    for award in copi_awards:
                        award_data = st.session_state.kg.graph.nodes[award]
                        with st.expander(award):
                            st.write(f"**Program:** {award_data.get('program', 'N/A')}")
                            st.write(f"**Amount:** ${int(award_data.get('amount', 0)):,}")
                            st.write(f"**Start Date:** {award_data.get('start_date', 'N/A')}")
                            st.write(f"**Abstract:** {award_data.get('abstract', 'N/A')}")
 
                    if collaborators:
                        st.subheader("Collaborators")
                        st.write(", ".join(collaborators))
            else:
                st.info("No co-investigators found in the current graph. "
                        "Co-PI data depends on NSF API availability for the loaded awards.")
        
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
                        
                        with st.expander(f"👤 {pi}: {len(pi_awards)} award(s)"):
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
            * **Hover** over a node to see details
            * **Drag** nodes to rearrange
            * **Scroll** to zoom
            * **Click and drag** the canvas to pan
            """
        )        

        # Controls 
        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            graph_height = st.slider("Graph height (px):", 400, 900, 620, step=50)
        with col_b:
            node_size = st.slider("Node size:", 8, 40, 18)
        with col_c:
            physics_on = st.toggle("Physics / live layout", value=True)
            show_subgraph = st.toggle(
                "Show subgraph only",
                value=False,
                disabled=st.session_state.subgraph is None,
                help="Toggle to view only the nodes returned by your Subgraph Query",
            )

        # decide graph to render
        active_graph = st.session_state.kg.graph
        graph_label = "Full Knowledge Graph"
        if show_subgraph and st.session_state.subgraph is not None:
            active_graph = st.session_state.subgraph
            graph_label = "Subgraph Query Result"
 
        st.caption(
            f"**{graph_label}** — "
            f"{nx.number_of_nodes(active_graph)} nodes · "
            f"{nx.number_of_edges(active_graph)} edges"
        )

        # Rendering graph

        with st.spinner("Rendering interactive graph…"):
            html_str = build_pyvis_html(active_graph, height=graph_height, physics=physics_on, node_size=node_size)
 
        components.html(html_str, height=graph_height + 20, scrolling=False)

    # tab5
    with tab5:
        st.header("Awards")

        # Get all PI's from the graph
        node_types = nx.get_node_attributes(st.session_state.kg.graph, 'type')
        awards = [node for node, node_type in node_types.items() if node_type == 'Award']
        
        # If there are awards, 
        if awards:
            selected_award = st.selectbox("Select an Award:", awards)

            if selected_award:
                award_data = st.session_state.kg.graph.nodes[selected_award]

                # Need to traverse nodes to get PI and CoPI data
                neighbors = list(st.session_state.kg.graph.neighbors(selected_award))
                pi_nodes = [n for n in neighbors if node_types.get(n) == 'PI']
                copi_nodes = [n for n in neighbors if node_types.get(n) == 'Co-PI']

                st.link_button("Visit NSF Award Page!", f"https://www.nsf.gov/awardsearch/show-award?AWD_ID={selected_award}", key=None, on_click="callable", args=None, kwargs=None, help=None, 
                    type="secondary", icon=None, icon_position="left", disabled=False, use_container_width=None, width="content", shortcut=None)

                st.write(f"**Program:** {award_data.get('program', 'N/A')}")
                st.write(f"**Amount:** {award_data.get('amount', 0)}")
                st.write(f"**Principal Investigator:** {', '.join(pi_nodes) or 'N/A'}")
                st.write(f"**Co-Investigator:** {', '.join(copi_nodes) or 'N/A'}")
                st.write(f"**Start Date:** {award_data.get('start_date', 'N/A')}")
                st.write(f"**Abstract:** {award_data.get('abstract', 'N/A')}")
            else: 
                st.write(f"There is no data for this award.")
        else:
            st.info("No awards found in the current graph. ")

else:
    st.info("Enter a query in the sidebar to get started")

    # Example queries for funsies
    st.subheader("Example Queries:")
    examples = [
        "Water research in Tennessee",
        "Cognitive science at The Ohio State University",
        "Grants over $100,000 in California",
        "Environmental research in New York",
        "Machine learning research"
    ]
    
    for example in examples:
        st.code(example)
