# serp_patents.py
import os
from serpapi import GoogleSearch
from config import SERPAPI_API_KEY

def search_patents(query: str, num_results: int = 10) -> list:
    params = {
        "engine": "google_patents",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num_results
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    # Return the organic results if present, else an empty list
    return results.get("organic_results", [])

def get_patent_details(patent_id: str) -> dict:
    params = {
        "engine": "google_patents_details",
        "patent_id": patent_id,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    return search.get_dict()

if __name__ == "__main__":
    # Prototype testing code for verifying the API response.
    query = "(Coffee)"
    results = search_patents(query)
    print("Organic Results:")
    print(results)
