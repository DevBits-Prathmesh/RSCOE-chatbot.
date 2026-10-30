"""Simple FAQ chatbot for JSPM's RSCOE website."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import requests
import streamlit as st
from bs4 import BeautifulSoup


SITE_URL = "https://www.jspmrscoe.edu.in/"
REQUEST_TIMEOUT = 15
STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "can",
    "do",
    "for",
    "how",
    "i",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "where",
    "which",
    "who",
    "with",
}


@dataclass(frozen=True)
class KnowledgeItem:
    title: str
    content: str
    url: str


def _words(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOP_WORDS and len(word) > 2
    }


@st.cache_data(ttl=3600, show_spinner=False)
def load_website_content() -> tuple[list[KnowledgeItem], str | None]:
    """Fetch the public homepage and split useful page sections into items."""
    try:
        response = requests.get(
            SITE_URL,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "RSCOE-Chatbot/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return [], f"Could not load the website right now: {error}"

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()

    items: list[KnowledgeItem] = []
    headings = soup.find_all(["h1", "h2", "h3"])
    for index, heading in enumerate(headings):
        title = heading.get_text(" ", strip=True)
        if not title:
            continue
        content_parts: list[str] = []
        for sibling in heading.find_next_siblings():
            if sibling.name in {"h1", "h2", "h3"}:
                break
            text = sibling.get_text(" ", strip=True)
            if text:
                content_parts.append(text)
        content = " ".join(content_parts)
        if content:
            items.append(KnowledgeItem(title, content[:1200], SITE_URL))

    if not items:
        text = soup.get_text(" ", strip=True)
        if text:
            items.append(KnowledgeItem("Website homepage", text[:4000], SITE_URL))
    return items, None


def find_answer(question: str, items: Iterable[KnowledgeItem]) -> tuple[str, str | None]:
    """Return the best lexical match without pretending to know missing facts."""
    question_words = _words(question)
    if not question_words:
        return "Please ask a question about the college website.", None

    ranked = sorted(
        (
            (len(question_words & _words(f"{item.title} {item.content}")), item)
            for item in items
        ),
        key=lambda result: result[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] == 0:
        return (
            "I could not find that information in the website content I loaded. "
            f"Please check the official website: {SITE_URL}",
            SITE_URL,
        )

    item = ranked[0][1]
    return f"**{item.title}**\n\n{item.content}", item.url


st.set_page_config(
    page_title="RSCOE Chatbot",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 RSCOE Website Chatbot")
st.caption("Ask questions about the public content on JSPM's RSCOE website.")

with st.sidebar:
    st.subheader("About")
    st.write(
        "This is a simple, free-to-deploy chatbot. It searches the website "
        "content fetched at runtime and does not invent answers."
    )
    st.link_button("Open official website", SITE_URL)
    if st.button("Refresh website content"):
        load_website_content.clear()
        st.rerun()

items, load_error = load_website_content()
if load_error:
    st.warning(load_error)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! Ask me about information available on the RSCOE website. "
                "For the latest official details, use the website link in the sidebar."
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Example: What information is available on the website?")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    answer, source_url = find_answer(question, items)
    if source_url:
        answer += f"\n\n[View source page]({source_url})"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
