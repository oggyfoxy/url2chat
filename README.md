# url2chat: chat with any website

## Hosted version

[Try this app here!](https://url2chat.streamlit.app).

## Requirements

To run this app you need to have:

- an [OpenAI](https://platform.openai.com/api-keys) API key
- an [Exa](https://exa.ai) API key (there is a free tier available)
- a [Google API key](https://cloud.google.com/docs/authentication/api-keys) with authorization for `Custom Search API` and a [Google custom search engine](http://www.google.com/cse/). [Read more.](https://stackoverflow.com/questions/37083058/%20programmatically-searching-google-in-python-using-custom-search)
- (optional) a [Phospho](https://phospho.ai) API key and project id

## Installation

Set up a virtual environment and install the requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Setup the streamlit secrets int the `.streamlit/secrets.toml` file:

```toml
EXA_API_KEY=""
OPENAI_API_KEY=""
GOOGLE_API_KEY=""
GOOGLE_CSE_ID=""
```

(Optional) Add your phospho api key and project id to get text analytics:

```toml
PHOSPHO_API_KEY=""
PHOSPHO_PROJECT_ID=""
```

## Usage

```bash
streamlit run main.py
```

This will open a new tab in your default browser with the app running.


