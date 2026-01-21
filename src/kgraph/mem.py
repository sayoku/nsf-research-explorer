import networkx as nx
from src.agent.tool import NSFAgent, query_nsf_api
import json

class KGBuilder():

    def __init__(self):
        self.graph = nx.Graph()
        self.agent = NSFAgent()

    def add_award(self, award):
        # Extract information from single award and save to identifiers
        award_id = award['response'].get('id', 'Unknown')
        pi_name = award['response'].get('pdPIName', 'Unknown PI')
        institution = award['response'].get('awardeeName', 'Unknown Institution')
        program = award['response'].get('fundProgramName', 'Unknown Program')
        amount = award['response'].get('estimatedTotalAmt', 0)
        start_date = award['response'].get('startDate', 'N/A')
        abstract = award['response'].get('abstractText', '')

        # Add award node
        self.graph.add_node(
            f"Award_{award_id}",
            type = 'Award',
            id = award_id,
            program = program,
            amount = amount,
            start_date = start_date,
            abstract = abstract[:200]
        )
        # Add PI Node
        if not self.graph.has_node(pi_name):
            self.graph.add_node(
                pi_name,
                type = 'PI',
                name = pi_name
            )
        # Add institution node 
        if not self.graph.has_node(institution):
            self.graph.add_node(
                institution,
                type='Institution',
                name=institution
            )

        # Add edges (relationships)
        self.graph.add_edge(pi_name, f"Award_{award_id}", relationship='investigates')
        self.graph.add_edge(institution, f"Award_{award_id}", relationship='hosts')
        self.graph.add_edge(pi_name, institution, relationship='affiliated_with')

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
