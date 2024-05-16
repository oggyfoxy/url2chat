import streamlit as st
from loguru import logger

# AN exception will be raised if the secret is not found
EXA_API_KEY = st.secrets["EXA_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# We want to only output a warning if these secret is not found
try:
    PHOSPHO_API_KEY = st.secrets["PHOSPHO_API_KEY"]
except KeyError:
    PHOSPHO_API_KEY = None
    logger.warning(
        "PHOSPHO_API_KEY not set as a streamlit secret (.streamlit/secrets.toml). phospho is disabled."
    )

try:
    PHOSPHO_PROJECT_ID = st.secrets["PHOSPHO_PROJECT_ID"]
except KeyError:
    PHOSPHO_PROJECT_ID = None
    logger.warning(
        "PHOSPHO_PROJECT_ID not set as a streamlit secret (.streamlit/secrets.toml). phospho is disabled."
    )

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
