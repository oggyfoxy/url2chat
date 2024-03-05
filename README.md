# url2chat: chat with any website

## Requirements

To run this app you need to have:

- an [OpenAI](https://platform.openai.com/api-keys) API key
- an [Exa](https://exa.ai) API key (there is a free tier available)

## Instalation

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
```

## Usage

```bash
streamlit run main.py
```

This will open a new tab in your default browser with the app running.
