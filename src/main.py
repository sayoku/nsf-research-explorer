from fastapi import FastAPI
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.put("/api/query/")
def run_nsf_query(query: str, awards: int):
    summary = kg.load_query_results(query, awards)
    if summary: 
        return {"summary": summary, "stats": kg.get_deduplication_stats()}
    else: 
        return{"summary": None, "stats": kg.get_deduplication_stats()}