import streamlit as st

EXA_API_KEY = st.secrets["EXA_API_KEY"]
assert (
    EXA_API_KEY
), "EXA_API_KEY is not set as a streamlit secret (.streamlit/secrets.toml)"

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
assert (
    OPENAI_API_KEY
), "OPENAI_API_KEY is not set as a streamlit secret (.streamlit/secrets.toml)"
