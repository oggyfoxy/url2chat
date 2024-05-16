import time
from urllib.parse import urlparse
import config
import streamlit as st
from advanced_agent import query2answer as query2answer_new, phospho
from agent import query2answer
from streamlit_feedback import streamlit_feedback
import asyncio


def run_async_function(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func(*args, **kwargs))


# Initialize URL
# Check the query parameters for a URL
if "url" in st.query_params:
    # Check it is note None
    if st.query_params.url and st.query_params.url != "None":
        st.session_state.url = st.query_params.url
if "url" not in st.session_state:
    st.session_state.url = None
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = phospho.new_session()

st.markdown(
    "# 📖 url2chat - Chat with any website\n*Built by [oggy](https://github.com/OggyFoxy/) @ 🧪[phospho](https://phospho.ai), Open Source Text Analytics for LLM Apps: version-trafilatura*"
)

ROLE_TO_AVATAR = {
    "user": "🦸‍♂️",
    "assistant": "🤖",
}

if st.session_state.url is None:
    url = st.text_input("Enter the URL of a website to chat with it")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        button_wikipedia = st.button("Wikipedia")
        if button_wikipedia:
            url = "https://en.wikipedia.org/"
    with col2:
        button_karpathy = st.button("A.Karpathy's blog")
        if button_karpathy:
            url = "http://karpathy.github.io"
    with col3:
        button_hackernews = st.button("Hacker News")
        if button_hackernews:
            url = "https://news.ycombinator.com"
    with col4:
        button_phospho = st.button("🧪phospho.ai")
        if button_phospho:
            url = "https://phospho.ai"
    if url:
        # Format checks
        if not url.startswith("http"):
            url = "https://" + url

        # Parse the URL to only have the domain
        o = urlparse(url)
        domain = o.hostname

        st.session_state.url = f"https://{domain}"
        # Set the URL as a query parameter to trigger a rerun
        st.query_params.url = f"https://{domain}"
        # Trigger a rerun to start chatting
        time.sleep(0.1)
        st.rerun()

else:
    # Add the URL as a query parameter (the rerun will remove it from the URL bar)
    st.query_params.url = st.session_state.url
    # TODO: Add a check to see if the URL is valid
    # Button to change the URL
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Change URL", use_container_width=True):
            st.session_state.url = None
            st.query_params.pop("url", None)
            st.session_state.messages = []
            st.session_state.session_id = phospho.new_session()
            # We need to add a small delay, otherwise the query parameter is not removed before the rerun
            time.sleep(0.5)
            st.rerun()
    with col2:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = phospho.new_session()
            st.rerun()

    with st.chat_message("assistant", avatar=ROLE_TO_AVATAR["assistant"]):
        st.markdown(f"You're chatting with {st.session_state.url}.")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=ROLE_TO_AVATAR[message["role"]]):
            st.markdown(message["content"])

    # Accept user input
    if query := st.chat_input("What is this website about?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        # Display user message in chat message container
        with st.chat_message("user", avatar=ROLE_TO_AVATAR["user"]):
            st.markdown(query)

        # Display assistant response in chat message container
        chat_answer, url_sources = run_async_function(
            query2answer_new,
            query=query,
            url=st.session_state.url,
            session_id=st.session_state.session_id,
        )

        # Fallback to sync function if no URL sources are found
        if not url_sources:
            chat_answer, url_sources = query2answer(
                query=query,
                url=st.session_state.url,
                session_messages=st.session_state.messages,
                session_id=st.session_state.session_id,
                model_name="gpt-4o",
            )
        with st.chat_message("assistant", avatar=ROLE_TO_AVATAR["assistant"]):
            st.markdown(chat_answer)
            # Display the sources in a hidden accordion container
            with st.expander("Sources", expanded=False):
                for source in url_sources:
                    st.markdown("- " + source)

        st.session_state.messages.append({"role": "assistant", "content": chat_answer})


# Add feedback button
def _submit_feedback(feedback: dict):
    # Add a check if phospho is setup
    if config.PHOSPHO_API_KEY and config.PHOSPHO_PROJECT_ID:
        phospho.user_feedback(
            task_id=phospho.latest_task_id,
            raw_flag=feedback["score"],
            notes=feedback["text"],
        )
        st.toast("Thank you for your feedback!")
    else:
        st.toast("phospho is not setup, feedback not sent.")


if len(st.session_state.messages) > 1:
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
        on_submit=_submit_feedback,
        # To create a new feedback component for every message and session, you need to provide a unique key
        key=f"{st.session_state.session_id}_{len(st.session_state.messages)}",
    )
