from typing import List
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

# you can get the API's following this guide: https://github.com/googleapis/google-api-python-client/tree/main
my_api_key = os.getenv("GOOGLE_API_KEY")
my_cse_id = os.getenv("GOOGLE_CSE_ID")


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    results = res.get("items", [])
    return results


def get_relevant_urls_from_google(domain: str, query: str) -> List[str]:
    results = google_search(f"site:{domain}", my_api_key, my_cse_id, num=10)
    relevant_urls = [
        result["link"]
        for result in results
        if "link" in result and domain in result["link"]
    ]
    return relevant_urls
