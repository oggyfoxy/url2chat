from typing import Dict, List, Optional, Tuple

import config
import tiktoken
from exa_py import Exa
from loguru import logger
from openai import OpenAI

import phospho

exa = Exa(config.EXA_API_KEY)

# For now we use the sync openai client
openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

# By default, phospho reads the PHOSPHO_API_KEY and PHOSPHO_PROJECT_ID from the environment variables
if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
    phospho.init()


def get_text_chunks(
    query: str,
    url: str,
    num_sentences: int = 5,
    highlights_per_url: int = 3,
) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Return a list of text chunks from the given URL that are relevant to the query.
    """

    highlights_options = {
        "num_sentences": num_sentences,  # how long our highlights should be
        "highlights_per_url": highlights_per_url,
    }
    search_response = exa.search_and_contents(
        query,
        highlights=highlights_options,
        num_results=10,
        use_autoprompt=True,
        include_domains=[url],
    )

    chunks = ["\n".join(sr.highlights) for sr in search_response.results]
    url_to_highlights = {sr.url: sr.highlights for sr in search_response.results}

    return chunks, url_to_highlights


def generate_prompt_from_chuncks(chunks: List[str], query: str) -> str:
    """
    Generate a prompt from the given chunks and question.
    TODO: add a check on token lenght to avoid exceeding the max token length of the model.
    """
    assert len(chunks) > 0, "Chunks should not be empty"

    concatenated_chunks = ""
    for chunck in chunks:
        concatenated_chunks += chunck + "\n\n"

    prompt = f"""
Query: {query}
Read the following text and answer the query.
---------------------
{concatenated_chunks}
---------------------
Given the context information and not prior knowledge, answer the query.
Do not start your answer with something like Based on the provided context information...
Query: {query}
Answer: 
"""
    return prompt


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def invoke_llm(
    prompt: str,
    model_name: str = "gpt-4o",
    previous_messages: Optional[List[Dict[str, str]]] = None,
) -> Optional[str]:
    """
    Invoke the language model with the given prompt and return the response.
    """
    if previous_messages is None:
        previous_messages = []
    completion = openai_client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant replying to questions given a context.",
            }
        ]
        + previous_messages
        + [
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    return completion.choices[0].message.content


def query2answer(
    query: str,
    url: str,
    session_messages: List[Dict[str, str]],
    session_id: str,
    model_name: str = "gpt-4o",
) -> Tuple[str, List[str]]:
    """
    Given a query and an URL, return the answer to the query.
    """

    logger.info(f"Query: {query}")
    url_sources = []

    try:
        chunks, url_to_highlights = get_text_chunks(query, url)
        url_sources = list(url_to_highlights.keys())
        logger.info(f"Retrieved {len(chunks)} chunks from {url}")
        prompt = generate_prompt_from_chuncks(chunks, query)
        # TODO: add a check on token length to avoid exceeding the max token length of the model.
        llm_answer = invoke_llm(prompt, previous_messages=session_messages)
        if llm_answer is None:
            llm_answer = (
                "Sorry, I was not able to answer, the OpenAI API returned None."
            )
        logger.info(f"Answer: {llm_answer}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        llm_answer = "Sorry, I was not able to answer. Either you setup a wrong URL or the URL is too new."

    # If enabled, log the interaction to Phospho
    if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
        phospho.log(
            input=query,
            output=llm_answer,
            session_id=session_id,
            metadata={
                "sources": url_sources,
                "url": url,
                "system_prompt": f"You are a helpful assistant replying to questions given a context.\n{prompt}",
                "model": model_name,
                "version_id": "exa_old",
            },
        )
    return llm_answer, url_sources
