from exa_py import Exa
from typing import List
from openai import OpenAI
import tiktoken
from loguru import logger

import config

exa = Exa(config.EXA_API_KEY)

# For now we use the sync openai client
openai_client = OpenAI(api_key=config.OPENAI_API_KEY)


def get_text_chunks(
    query: str,
    url: str,
    num_sentences: int = 15,
    highlights_per_url: int = 5,
) -> List[str]:
    """
    Return a lsit of text chunks from the given URL that are relevant to the query.
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

    chunks = [sr.highlights[0] for sr in search_response.results]

    return chunks


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
Context information is below.
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


def invoke_llm(prompt: str, model_name: str = "gpt-3.5-turbo") -> str:
    """
    Invoke the language model with the given prompt and return the response.
    """
    completion = openai_client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    return completion.choices[0].message.content


def query2answer(query: str, url: str) -> str:
    """
    Given a query and an URL, return the answer to the query.
    """
    logger.info(f"Query: {query}")
    chuncks = get_text_chunks(query, url)
    logger.info(f"Retrieved {len(chuncks)} chunks from {url}")
    prompt = generate_prompt_from_chuncks(chuncks, query)
    # TODO: add a check on token lenght to avoid exceeding the max token length of the model.
    llm_answer = invoke_llm(prompt)
    logger.info(f"Answer: {llm_answer}")
    return llm_answer
