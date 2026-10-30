# RSCOE Website Chatbot

A small Python chatbot that answers from the public content of
[JSPM's RSCOE website](https://www.jspmrscoe.edu.in/). It uses lexical matching
instead of a paid AI API, so it is inexpensive and suitable for free hosting.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py` and `requirements.txt`.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/).
3. Select **Deploy an app**, choose the repository, and set the main file to
   `app.py`.
4. Deploy. No secrets or paid API keys are required.

The app fetches the official website when it starts and caches the result for
one hour. Use **Refresh website content** in the sidebar after the website
changes.

## Other free options

- **Render:** create a web service with build command
  `pip install -r requirements.txt` and start command
  `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`.
- **Hugging Face Spaces:** choose the Streamlit SDK and upload the same files.

## Important limitation

This version only answers using text that is publicly available on the
configured homepage. It does not crawl every linked page, authenticate users,
or generate answers with an LLM. This makes responses predictable and keeps
deployment free. Add more pages to `load_website_content` if the site exposes
important information on separate URLs.
