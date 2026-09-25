"""
5_Usage.py

Shows how much of your $5/month free Apify credit you've used this
month, so you always know where you stand before ever risking real
charges.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from database.crud import get_monthly_usage, get_total_usage
from utils.styling import inject_custom_css, metric_card, render_sidebar_branding

st.set_page_config(page_title="Usage - Lead Extractor", page_icon="📍", layout="wide")
inject_custom_css()
render_sidebar_branding()

st.markdown("# Usage")
st.caption("Apify free credit tracking - resets on the 1st of every month")

MONTHLY_FREE_CREDIT = 5.00

monthly_usage = get_monthly_usage()
total_usage = get_total_usage()
remaining = max(MONTHLY_FREE_CREDIT - monthly_usage, 0)
percent_used = min(monthly_usage / MONTHLY_FREE_CREDIT, 1.0)

col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Used This Month", f"${monthly_usage:.2f}")
with col2:
    metric_card("Remaining", f"${remaining:.2f}")
with col3:
    metric_card("All-Time Total", f"${total_usage:.2f}")

st.write("")
st.markdown(f"**{percent_used * 100:.1f}% of your $5.00 monthly free credit used**")
st.progress(percent_used)

if percent_used >= 0.9:
    st.warning(
        "You're close to your free monthly limit. Extra usage this month "
        "may incur real charges on your Apify account.",
        icon="⚠️",
    )
elif percent_used >= 0.7:
    st.info(
        "You've used a good chunk of this month's free credit - still "
        "comfortable room left, just worth keeping an eye on.",
        icon="ℹ️",
    )
else:
    st.success("Comfortably within your free monthly credit.", icon="✅")

st.caption(
    "Note: this tracks estimated usage logged by our own tools "
    "(~$1.50 per 1,000 scraped results), not a live balance pulled "
    "directly from Apify - check your Apify console for the exact figure."
)