from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys, os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent.tool import NSFAgent
from kgraph.mem import KGBuilder
from kgraph.query import KGQueryAgent 

app = FastAPI()

kg = KGBuilder()
# kg.set_nlp(nlp)

# Response/requests: 

class QueryRequest(BaseModel):
    query: str
    max_awards: int = 10 # Only for now 

class SubqueryRequest(BaseModel):
    query: str

# POST /api/query 
# ie the search button that takes a query and searches 

@app.post("/api/query")
def run_query(req: QueryRequest):
    summary = kg.load_query_results(req.query, max_awards=req.max_awards)
    if summary: 
        return {"summary": summary, "stats": kg.get_deduplication_stats()}
    else: 
        raise HTTPException(status_code=404, detail="No results found.")

# POST /api/grapj/subgraph 
# Query the graph, it technically functions as a GET but it is a query

@app.post("/api/graph/subgraph")
def query_subgraph(req: SubqueryRequest):
    agent = KGQueryAgent(kg.graph)
    subgraph, explanation, nodes = agent.subquery(req.query)

    # Turn networkx into JSON, which will connect to the frontend
    import networkx as nx
    graph_json = nx.node_link_data(subgraph)

    return {"explanation": explanation, "node_count": len(nodes), "graph": graph_json,}


# TODO:  add a POST /api/reset that does kg = KGBuilder() again, mirroring your sidebar's reset button,

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}