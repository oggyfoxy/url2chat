import streamlit as st
from agent import query2answer
import phospho
from urllib.parse import urlparse

import config

# By default, phospho reads the PHOSPHO_API_KEY and PHOSPHO_PROJECT_ID from the environment variables
if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
    phospho.init()
# Initialize URL
if "url" not in st.session_state:
    st.session_state.url = None
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = phospho.new_session()

st.markdown(
    "# 📖 url2chat - Chat with any website\n*Built by 🧪[phospho](https://phospho.ai), Open Source Text Analytics for LLM Apps*"
)

ROLE_TO_AVATAR = {
    "user": "🦸‍♂️",
    "assistant": "📖",
}

if st.session_state.url is None:
    url = st.text_input("Enter the URL of a website to chat with it")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        button_wikipedia = st.button("Wikipedia")
        if button_wikipedia:
            url = "https://en.wikipedia.org/"
    with col2:
        button_karpathy = st.button("A. Karpathy's blog")
        if button_karpathy:
            url = "http://karpathy.github.io"
    with col3:
        button_hackernews = st.button("Hacker News")
        if button_hackernews:
            url = "https://news.ycombinator.com"
    if url:
        # Format checks
        if not url.startswith("http"):
            url = "https://" + url

        # Parse the URL to only have the domain
        o = urlparse(url)
        domain = o.hostname

        st.session_state.url = f"https://{domain}"
        # Trigger a rerun to start chatting
        st.rerun()

else:
    # TODO: Add a check to see if the URL is valid
    # Button to change the URL
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Change URL", use_container_width=True):
            st.session_state.url = None
            st.session_state.messages = []
            st.session_state.session_id = phospho.new_session()
            st.rerun()
    with col2:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = phospho.new_session()
            st.rerun()

    with st.chat_message("assistant", avatar=ROLE_TO_AVATAR["assistant"]):
        st.markdown(f"You're chatting with {st.session_state.url}. Ask me anything! 📖")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=ROLE_TO_AVATAR[message["role"]]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is this website about?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user", avatar=ROLE_TO_AVATAR["user"]):
            st.markdown(prompt)

        # Display assistant response in chat message container
        chat_answer, url_sources = query2answer(
            prompt, st.session_state.url, st.session_state.messages
        )
        with st.chat_message("assistant", avatar=ROLE_TO_AVATAR["assistant"]):
            st.markdown(chat_answer)
            # Display the sources in a hidden accordion container
            with st.expander("Sources", expanded=False):
                for source in url_sources:
                    st.markdown("- " + source)

        # If enabled, log the interaction to Phospho
        if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
            phospho.log(
                input=prompt,
                output=chat_answer,
                # TODO: for chats, group tasks together in sessions
                session_id=st.session_state.session_id,
                metadata={"sources": url_sources},
            )
        st.session_state.messages.append({"role": "assistant", "content": chat_answer})
