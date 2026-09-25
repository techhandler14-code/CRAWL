"""
6_Roadmap.py

An honest list of features we deliberately scoped out of the MVP, and
why. Built instead of padding the sidebar with fake/dead links - this
page is real content, not decoration.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from utils.styling import inject_custom_css, render_sidebar_branding

st.set_page_config(page_title="Roadmap - Lead Extractor", page_icon="📍", layout="wide")
inject_custom_css()
render_sidebar_branding()

st.markdown("# Roadmap")
st.caption("What's intentionally not built yet, and why")

ROADMAP_ITEMS = [
    (
        "Rating-based filtering",
        "Google Maps ratings are available but sit in a pricier Apify field "
        "tier. Currently shown as a display-only consideration; a hard "
        "filter (e.g. 'only businesses under 4 stars') is a natural next step.",
    ),
    (
        "WhatsApp click-to-chat links",
        "Auto-generate a wa.me/ link from each lead's cleaned phone number, "
        "for one-click outreach directly from the dashboard.",
    ),
    (
        "AI-drafted outreach messages",
        "Use the free Hugging Face LLM to draft a short, personalized first "
        "message per lead, based on business name and niche - edited by "
        "hand before sending.",
    ),
    (
        "Map view",
        "Plot leads on an OpenStreetMap/Leaflet map using the lat/lng "
        "Apify already returns, to visually cluster nearby leads.",
    ),
    (
        "Auto niche-tagging",
        "Currently niches are chosen manually via dropdown to avoid "
        "fragmentation. A smarter auto-classification step could reduce "
        "manual tagging as the number of niches grows.",
    ),
    (
        "LangGraph rebuild",
        "This project was deliberately built first on classic LangChain "
        "AgentExecutor to learn its real strengths and limitations "
        "hands-on. A LangGraph rebuild is the planned next learning "
        "milestone, applying those lessons to a more robust architecture.",
    ),
]

for title, description in ROADMAP_ITEMS:
    st.markdown(f"### {title}")
    st.write(description)
    st.divider()