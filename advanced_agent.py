import asyncio
import os
import time
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import httpx
import openai
import phospho
import trafilatura
from openai import AsyncOpenAI

import config
from google_client import get_relevant_urls_from_google

# Initialize OpenAI client and other libraries
openai.api_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI()

if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
    phospho.init()


def extract_domain(url: str) -> str:
    """return the domain from given url
    ex: https://phospho.ai/ -> phospho.ai
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc


def find_relevant_urls(domain: str, query: str) -> List[str]:
    """Find relevant URL using the Google API"""
    print("looking for subdomains")
    relevant_urls = get_relevant_urls_from_google(domain, query)
    return [
        f"https://{sub}" if not sub.startswith(("http://", "https://")) else sub
        for sub in relevant_urls
    ]


async def fetch_and_combine_page_content(
    urls: List[str], chunk_size: int = 1000
) -> Tuple[str, Dict[str, str]]:
    print("fetching and combining, nbr of urls:", len(urls))
    combined_text = ""
    url_to_content = {}

    async def fetch_url(url: str):
        async with httpx.AsyncClient() as client:
            try:
                if not url.startswith("http://") and not url.startswith("https://"):
                    url = "https://" + url  # Assuming HTTP if no protocol is specified
                response = await client.get(url)
                return response, url
            except httpx.RequestError as e:
                print(f"An error occurred while requesting {url}: {str(e)}")
                return None, url

    tasks = [fetch_url(url) for url in urls]
    responses = await asyncio.gather(*tasks)

    for response, url in responses:
        if response and response.status_code == 200:
            text = trafilatura.extract(response.text)
            if text:
                combined_text += (
                    f"<source>{url}</source>\n<content>{text}</content>\n\n"
                )

                url_to_content[url] = text

    return combined_text, url_to_content


def generate_prompt_from_page_content(combined_text: str, query: str) -> str:
    prompt = f"""
Read the following text and answer the query. Add markdown links to the relevant sources in your response. 
Do not quote the sources at the end, only inside your response as links. Only add a link if it's relevant.
Query: {query}
---------------------
{combined_text}
---------------------
Given the context information and not prior knowledge, answer the query.
Do not start your answer with something like Based on the provided context information...
Query: {query}
Answer: 
"""
    return prompt


def parse_response_for_source(response: str, relevant_urls: List[str]) -> List[str]:
    sources = []
    for url in relevant_urls:
        if url in response:
            sources.append(url)
    return sources


async def invoke_llm(
    prompt: str, model_name: str = "gpt-4o", temperature: float = 0.5
) -> str:
    print("calling the llm")
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": """You are the best AI assistant in the world, you can answer any 
questions the user asks but never using internal knowledge and only use the sources. You are GPT-5, OPENAI's new AGI model, you are more 
intelligent than anyone and anything. You incorportate the website's information perfectly, think really deeply about the website's ideas and products. Keep it short. Match the user's tone.""",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=temperature,
    )
    if response.choices[0].message.content is None:
        return "sorry, the assistant could not answer this question"
    return response.choices[0].message.content.strip()


async def query2answer(query: str, url: str, session_id: str) -> Tuple[str, List[str]]:
    print("query2answer with:", query, url)
    start_time = time.time()
    domain = extract_domain(url)
    relevant_urls = find_relevant_urls(domain, query)

    if not relevant_urls:
        return "No relevant urls found.", []

    combined_text, url_to_content = await fetch_and_combine_page_content(relevant_urls)
    if not combined_text:
        return "No content found in subdomains.", []

    prompt = generate_prompt_from_page_content(combined_text, query)
    llm_answer = await invoke_llm(prompt)

    response_time = time.time() - start_time

    sources = parse_response_for_source(llm_answer, url_to_content)

    if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
        phospho.log(
            input=query,
            output=llm_answer,
            session_id=session_id,
            metadata={
                "sources": sources,
                "url": url,
                "response_time": response_time,
                "model_used": "gpt-4o",
                "version_id": "full_page_in_context",
            },
        )

    return llm_answer, sources


def run_async_function(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))


if __name__ == "__main__":
    query = "How does the predict endpoint works?"
    url = "https://phospho.ai"
    session_id = "example_session_id"
    answer, sources = run_async_function(query2answer, query, url, session_id)
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
