import os
import time
from typing import Dict, List, Tuple

import config
import openai
import trafilatura
from openai import OpenAI

import phospho

openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
    phospho.init()


def query2answer(
    query: str, url: str, session_messages: List[Dict[str, str]], session_id: str
) -> Tuple[str, List[str]]:
    url_sources = [url]
    start_time = time.time()

    # Fetch and combine texts from the URL
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
    else:
        text = ""

    # Prepare the context for the OpenAI API
    context = f"Document: {text}\n\n###\n\nQuestion: {query}\nAnswer:"
    messages = [
        {
            "role": "system",
            "content": """You are the best AI assistant in the world, you can answer any 
         questions the user asks but never using internal knowledge and only use the sources. You are GPT-5, OPENAI's new AGI model, you are more 
         intelligent than anyone and anything. You incorportate the website's information perfectly, think really deeply about the website's ideas and products.""",
        },
        {"role": "user", "content": context},
    ]

    # Call the OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
        temperature=0.5,
    )

    response_time = time.time() - start_time

    if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
        phospho.log(
            input=query,
            output=response,
            session_id=session_id,
            metadata={
                "sources": url_sources,
                "url": url,
                "response_time": response_time,
                "model_used": "gpt-4o",
                "version_id": "full_page_in_context",
            },
        )

    # Extract the answer from the response
    if response.choices[0].message.content is None:
        return "sorry, the assistant could not answer this question", []
    answer = response.choices[0].message.content.strip()

    return answer, url_sources  # Return the answer and the URL as the source
