import networkx as nx

G = nx.Graph()
G.add_nodes_from([(4, {"color": "red"}), (5, {"color": "green"})])

H = nx.path_graph(10)
G.add_nodes_from(H)
G.add_edges_from([(1, 2), (1, 3)])

# we add new nodes/edges and NetworkX quietly ignores any that are already present.

G.add_edges_from([(1, 2), (1, 3)])
G.add_node(1)
G.add_edge(1, 2)
G.add_node("spam")        # adds node "spam"
G.add_nodes_from("spam")  # adds 4 nodes: 's', 'p', 'a', 'm'
G.add_edge(3, 'm')

list(G.nodes)
#[1, 2, 3, 'spam', 's', 'p', 'a', 'm']
list(G.edges)
#[(1, 2), (1, 3), (3, 'm')]
list(G.adj[1])  # or list(G.neighbors(1))
#[2, 3]
G.degree[1]  # the number of edges incident to 1
#2

G.nodes["spam"]["color"] = "blue"
G.edges[(1, 2)]["weight"] = 10

G.remove_node(2)
G.remove_nodes_from("spam")

G.add_edge(1, 2)
H = nx.DiGraph(G)  # create a DiGraph using the connections from G
list(H.edges())
#[(1, 2), (2, 1)]