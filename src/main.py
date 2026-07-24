from fastapi import FastAPI
from pydantic import BaseModel
import networkx as nx
import sys, os
 
# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent.tool import NSFAgent
from kgraph.mem import KGBuilder
from kgraph.query import KGQueryAgent 

app = FastAPI()
kg = KGBuilder()

class QueryRequest(BaseModel):
    query: str
    max_awards: int = 10

class SubqueryRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "NSF Research Explorer API"}

@app.post("/api/query/")
async def run_nsf_query(req: QueryRequest):
    summary = kg.load_query_results(req.query, req.max_awards)
    if summary: 
        return {"summary": summary, "stats": kg.get_deduplication_stats()}
    else: 
        return{"summary": None, "stats": kg.get_deduplication_stats()}
    
@app.post("/api/graph/subgraph/")
async def run_graph_subquery(req: SubqueryRequest):
    agent = KGQueryAgent(kg.graph)
    subgraph, explanation, nodes = agent.subquery(req.query)

    graph_json = nx.node_link_data(subgraph)

    return {
        "explanation": explanation,
        "node_count": len(nodes),
        "graph": graph_json
    }

@app.post("/api/reset/")
async def reset_graph():
    global kg
    kg = KGBuilder()
    return {"message": "Graph cleared"}

# GET - PI's
@app.get("/api/pis/")
async def get_pis():
    node_types = nx.get_node_attributes(kg.graph, "type")
    return {
        "pis": [n for n, t in node_types.items() if t == "PI" ],
        "copis": [n for n, t in node_types.items() if t == "Co-PI" ]
    }

# A specific PI
@app.get("/api/pis/{pi_name}/")
async def get_specific_pi(pi_name: str): 
    awards = kg.get_pi_awards(pi_name)
    award_details = [{"id": a, **kg.graph.nodes[a]} for a in awards]
    return {"pi": pi_name, "awards": award_details}\
    
# A specific copi
@app.get("/api/copis/{copi_name}/")
async def get_specific_copi(copi_name: str):
    awards = kg.get_copi_awards(copi_name)
    collaborators = kg.get_collaborators(copi_name)
    return {"copi": copi_name, "awards": awards, "collaborators": collaborators}

# GET - Institutions
@app.get("/api/institutions/")
async def get_institutions():
    node_types = nx.get_node_attributes(kg.graph, 'type')
    return {"institutions": [n for n, t in node_types.items() if t == "Institution"]}

# A pi's at a specific Institution
@app.get("/api/institutions/{inst}/")
async def get_institution_pis(inst: str):
    inst_pis = kg.get_institution_pis(inst)
    if inst_pis: 
        result = {}
        for pi in inst_pis:
            result[pi] = kg.get_pi_awards(pi)
    return {"institution": inst, "pi_awards": result}

# GET - Awards
@app.get("/api/awards/")
async def get_awards():
    node_types = nx.get_node_attributes(kg.graph, 'type')
    return {"awards": [n for n, t in node_types.items() if t == "Award"]}

# A specific award
@app.get("/api/awards/{award}")
async def get_award(award: str):
    if award not in kg.graph: 
        return {"error": "award not found"}
    
    node_types = nx.get_node_attributes(kg.graph, "type")
    award_id = award.removeprefix("Award_")
    award_data = dict(kg.graph.nodes[award])
    neighbors = list(kg.graph.neighbors(award))
    pi_nodes = [n for n in neighbors if node_types.get(n) == 'PI']
    copi_nodes = [n for n in neighbors if node_types.get(n) == 'Co-PI']
    link = f"https://www.nsf.gov/awardsearch/show-award?AWD_ID={award_id}"

    return {
        "award_id": award_id,
        "award_data": award_data,
        "neighbors": neighbors,
        "pi_nodes": pi_nodes,
        "copi_nodes": copi_nodes,
        "link_to_award": link
        }

# GET - KG
@app.get("/api/graph/")
async def get_graph():
    if kg.graph.number_of_nodes() == 0:
        return {"graph": None}
    return {"graph": nx.node_link_data(kg.graph)}

# Graph stats 
@app.get("/api/graph/stats/")
async def get_graph_stats():
    return {
        "stats": kg.get_deduplication_stats(),
        "node_count": kg.graph.number_of_nodes(),
        "edge_count": kg.graph.number_of_edges(),
        "density": nx.density(kg.graph) if kg.graph.number_of_nodes() > 0 else 0
    }
