import anthropic
import requests
import json
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

"""
Tool: Given a structured input, query the NSF API and output the data in a json. 
"""

def query_nsf_api(params):
    """
    Query the nsf api with the given parameters:

    Args:
        Dict params : dictionary with API parameters
            {
            "parameter":"value" 
            "parameter":"value"
            "parameter":"value"
            }    
    Returns:
        json response from the nsf api

    """
    
    # base url
    base_url = "http://api.nsf.gov/services/v1/awards.json?"
    
    # Requests library handles parameter formatting
    response = requests.get(base_url, params=params)
    # If it was successful, 
    if response.status_code == 200: 
        # Returns a python dictionary 
        return response.json()
    else:
        print("Error upon querying, status code: " + response.status_code)  
        return None
    
class NSFAgent: 
    """
    LLM Agent translating natural language into structures NSF API parameters (in a json dictionary)
    """
    
    def __init__(self, api_key=None): 
        """
        Initialize the agent with the model

        Args: 
            String api_key = Anthropic API Key 
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

        system_prompt = """

        You are a translator for NSF Research Award Queries. Your job is to take user responses and reformat them into a json of request parameters and values. 
        A full list of request parameters may be found on the NSF API, but key request parameters include:
        keyword: search term
        rpp: results per page, range 1 to 25, maximum of 3000 results are displayed
        ActiveAwards: true
        ExpiredAwards: true
        id: unique identifier 
        agency: NSF, agency name
        awardeeCity: city name
        awardeeCountryCode: country codes
        awardeeDistrctCode: append state abbreviation and district code
        awardeeName: name of entity, ex: "university+of+south+florida"
        awardeeStateCode
        awardeeZipCode: 9 digit zip code
        cdfaNumber: catalog of Federal Domestic Assistance Number
        coPDPI: co principal investigator name
        estimatedTotalAmtFrom: estimated total from amount (values greater than)
        estimatedTotalAmtTo: estimated total to amount (search for values less than)
        fundsObligatedAmtFrom: funds obligated from amount - greater than
        fundsObligatedAmtTo: funds obligated less than amount
        pdPIName: Project Director/PI Name, Principal Investigator or Project Director (ex. "SUMNET+STARFIELD")

        Output rules: 
            1. Include only the JSON, no explanations or markdown. 
            2. Only include parameters clearly specified in the user query. 
            3. Use + instead of spaces in multi-word-values
            4. Dates are formatted as MM/DD/YYYY
            5. Convert descriptions to integers (ex: over 1 million = 1000000)
            6. If the query is unclear or impossible, output: {"error": "description of issue"}

        Now translate the user's query into NSF API parameters.
        
        """ 

    def translate_query(self, query):
        """
        Translate natural langauge query into NSF API params

        Args: 
            String query : User question about NSF grants
        Returns: 
            Dict params : structured parameters for NSF API or error dict 
        """
        #client = anthropic.Anthropic()

        message = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system = self.system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        response = message.content[0].text
        return response

    def execute_agent(self, query):
        """
        Execute query (translating, checking for error, and returning the results from the nsf api)

        Args: 
            String query : Natural language (user) question
        Returns 
            Tuple report : (params, nsfapi_response)
        """
        # Get the translated query into params 
        params = self.translate_query(query)
        # Check for error, if there is an error, return params and null
        if "error" in params:
            print({params['error']})
            return params, None 

        # otherwise print the json of params
        print(json.dumps(params, indent = 3)) # the translated params 
        # the results are the queried results using params
        results = query_nsf_api(params)
        # return both
        return params, results


# Testing query_nsf_api, should also test the NSF Agent

if __name__ == "__main__":

    agent = NSFAgent()
    # Testing function with keyword search
    # Currently using a json formatted string and not a whole file
    result = query_nsf_api({'keyword' : 'water', 'awardeeStateCode':'TN', 'awardeeName':'university+of+tennessee+knoxville'})
    #result = query_nsf_api({'awardeeStateCode':'TN', 'awardeeName':'university+of+tennessee+knoxville'})

    if result:  # not None (null) 
        # Access total count data through in the json output
        total = result['response']['metadata']['totalCount']
        print("Found {total} awards for 'water'".format(total=total))
    else:
        print("Failed, no data.")