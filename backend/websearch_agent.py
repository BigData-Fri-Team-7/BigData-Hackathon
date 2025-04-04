import os
import json
from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load environment variables from .env
load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

def serpapi_search(query: str, num_results: int = 10) -> dict:
    """
    Performs a Google Patents search using SerpAPI and returns the full JSON response.
    
    Args:
        query (str): The search query.
        num_results (int): Number of results to retrieve.
        
    Returns:
        dict: The complete JSON response from SerpAPI.
    """
    if not SERP_API_KEY:
        raise ValueError("Missing SERPAPI_API_KEY in environment variables.")

    params = {
        "engine": "google_patents",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": num_results,
        "hl": "en",  # Ensure English results
        "gl": "us"   # Set region to US for consistency
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    except Exception as e:
        print(f"[SerpAPI Error] {e}")
        return {}

def build_patent_query(patent_title: str) -> str:
    """
    Builds a dynamic query for retrieving related patents based on the given patent title.
    
    Args:
        patent_title (str): The title of the patent being processed.
        
    Returns:
        str: A formatted query string.
    """
    return (
        f"Retrieve related patents for the patent titled '{patent_title}'. "
        "For each related patent, please provide the title, filing and publication dates, "
        "inventor(s), assignee, a brief abstract or description, and a direct link to the full patent details. "
        "Present the results in a clearly structured list, sorted by relevance."
    )

def print_patent_details(results: dict):
    """
    Parses and prints detailed patent information from the SerpAPI JSON response.
    
    Args:
        results (dict): The JSON response from SerpAPI.
    """
    organic_results = results.get("organic_results", [])
    if not organic_results:
        print("No organic results found!")
        return

    for idx, patent in enumerate(organic_results, 1):
        print(f"Result {idx}:")
        print(f"Title: {patent.get('title', 'No Title')}")
        # Use 'patent_link' if available; fallback to 'link' or 'scholar_link'
        link = patent.get("patent_link") or patent.get("link") or patent.get("scholar_link", "")
        print(f"Link: {link}")
        snippet = patent.get("snippet", "")
        # Append additional snippet content if available
        additional = " ".join(patent.get("snippet_highlighted_words", []))
        if additional:
            snippet += " " + additional
        print(f"Snippet: {snippet if snippet else 'No snippet available'}")
        print(f"Publication Date: {patent.get('publication_date', 'Unknown')}")
        print(f"Priority Date: {patent.get('priority_date', 'N/A')}")
        print(f"Filing Date: {patent.get('filing_date', 'N/A')}")
        print(f"Grant Date: {patent.get('grant_date', 'N/A')}")
        print(f"Inventor: {patent.get('inventor', 'Unknown')}")
        print(f"Assignee: {patent.get('assignee', 'Unknown')}")
        print(f"PDF: {patent.get('pdf', 'N/A')}")
        print("-" * 60)

def main():
    # For testing purposes, use a sample patent title.
    patent_title = "Your Patent Title"
    query = build_patent_query(patent_title)
    num_results = 10

    results = serpapi_search(query, num_results)
    if results:
        print_patent_details(results)
    else:
        print("No results returned from SerpAPI.")

if __name__ == "__main__":
    main()
