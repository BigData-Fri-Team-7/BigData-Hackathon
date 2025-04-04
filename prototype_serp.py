# prototype_serp.py
import os
from serpapi import GoogleSearch
from config import SERPAPI_API_KEY
import sys
sys.stdout.reconfigure(encoding='utf-8')


def prototype_search(query: str):
    params = {
        "engine": "google_patents",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": 10
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Print the full response for debugging
    print("Full API response:")
    print(results)
    
    if "organic_results" in results:
        organic_results = results["organic_results"]
        print("\nOrganic Results:")
        for res in organic_results:
            print("-" * 40)
            print(res)
    else:
        print("No 'organic_results' key found in the response.")

if __name__ == "__main__":
    query = "(Coffee)"
    prototype_search(query)
