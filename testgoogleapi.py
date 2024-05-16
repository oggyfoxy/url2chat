from typing import List
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    results = res.get("items", [])
    return results


def get_relevant_urls_from_google(domain: str, query: str) -> List[str]:
    """
    This function uses the Google API. Instructions are in the README.md
    """
    results = google_search(
        f"site:{domain}",
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GOOGLE_CSE_ID"),
        num=10,
    )
    relevant_urls = [
        result["link"]
        for result in results
        if "link" in result and domain in result["link"]
    ]
    return relevant_urls
