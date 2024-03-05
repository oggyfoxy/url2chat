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

Setup the environment variables:

```bash
export OPENAI_API_KEY=your_openai_api_key
export EXA_API_KEY=your_exa_api_key
```

## Usage

```bash
streamlit run main.py
```

This will open a new tab in your default browser with the app running.
