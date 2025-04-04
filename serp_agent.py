import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load environment variables from .env
load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")


def serpapi_search(query: str, num_results: int = 10) -> list:
    """
    Performs a Google Patents search using SerpAPI and returns a list of results.

    Args:
        query (str): The search query.
        num_results (int): Number of results to retrieve.

    Returns:
        List[dict]: List of dictionaries containing patent info (title, link, snippet, date).
    """
    if not SERP_API_KEY:
        raise ValueError("Missing SERPAPI_API_KEY in environment variables.")

    params = {
        "engine": "google_patents",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": num_results
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        patents = results.get("patents_results", [])

        return [
            {
                "title": p.get("title", "No Title"),
                "link": p.get("link", ""),
                "snippet": p.get("snippet", "No description"),
                "date": p.get("filing_date", p.get("publication_date", "Unknown"))
            }
            for p in patents
        ]

    except Exception as e:
        print(f"[SerpAPI Error] {e}")
        return []
