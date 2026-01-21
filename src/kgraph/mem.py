import networkx as nx
from src.agent.tool import NSFAgent, query_nsf_api

# graph = nx.Graph()
# pdPIName
# keyword
# awardeeName
# graph.add_nodes_from( )

if __name__ == "__main__":
    agent = NSFAgent()
    query = "Find water research grants in Tennessee at UT Knoxville."
    params, results = agent.execute_agent(query)
    if results: 
        # Example of working with results data 
        total = results['response']['metadata'].get('totalCount',0)
        print("Found {total} matching awards".format(total=total))

    # This will output the summary 
    # print(agent.complete_reply(query, results))
