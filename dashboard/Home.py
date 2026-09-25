"""
Home.py

Entry point of the Streamlit dashboard (Streamlit automatically treats
this file, plus everything in dashboard/pages/, as one multi-page app).
Shows an overview: total leads, niches tracked, and a status breakdown.
"""

import sys
from pathlib import Path

# Streamlit runs this file directly, so Python doesn't automatically know
# our project root (parent of dashboard/) should be importable. This adds
# it manually - same idea as the Path trick in database/db.py, just
# needed here for a different reason (streamlit run vs python -m).
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from collections import Counter

from database.crud import get_leads, get_all_niches
from utils.styling import inject_custom_css, metric_card, status_badge, render_sidebar_branding

st.set_page_config(
    page_title="Lead Extractor",
    page_icon="📍",
    layout="wide",
)

inject_custom_css()
render_sidebar_branding()

# --- Load all the data we need for this page ---
all_leads = get_leads()  # no filters passed = every lead in the database
niches = get_all_niches()

total_leads = len(all_leads)
# Counter is a dict-like tool built into Python that counts how many
# times each value appears - here, how many leads have each status
status_counts = Counter(lead["status"] for lead in all_leads)

# --- Hero stats row ---
st.markdown("# Overview")

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Total Leads", total_leads)
with col2:
    metric_card("Niches Tracked", len(niches))
with col3:
    metric_card("Pending", status_counts.get("Pending", 0))
with col4:
    metric_card("Conversions", status_counts.get("Conversion", 0))

st.write("")  # a little vertical spacing before the next section
st.markdown("### Leads by niche")

if not niches:
    st.info("No leads yet. Head to **Extract Leads** to find your first batch.")
else:
    for niche in niches:
        niche_leads = [lead for lead in all_leads if lead["niche"] == niche]
        niche_status_counts = Counter(lead["status"] for lead in niche_leads)

        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.markdown(f"**{niche}**")
            st.caption(f"{len(niche_leads)} leads")
        with col_b:
            badges = [
                status_badge(status)
                for status in ["Pending", "No Reply", "Conversion"]
                if niche_status_counts.get(status, 0) > 0
            ]
            st.markdown(" ".join(badges), unsafe_allow_html=True)

        st.divider()