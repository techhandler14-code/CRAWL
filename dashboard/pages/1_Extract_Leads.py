"""
1_Extract_Leads.py

Lets you search for new leads through the agent, right from the browser.

Fixes the niche fragmentation problem we actually saw on the Home page
(the agent inventing slightly different niche labels across runs) two
ways: (1) you pick from EXISTING niches via dropdown instead of typing
free text, and (2) when we do call the agent, we explicitly tell it which
exact niche string to use - not leaving that choice up to the LLM anymore.
"""

import sys
from pathlib import Path

# pages/ is one folder deeper than Home.py, so we need one extra .parent
# to reach the project root from here
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from database.crud import get_all_niches
from utils.styling import inject_custom_css, render_sidebar_branding
from agent.agent_executor import get_agent_executor

st.set_page_config(page_title="Extract Leads - Lead Extractor", page_icon="📍", layout="wide")
inject_custom_css()
render_sidebar_branding()

st.markdown("# Extract Leads")
st.caption("Search Google Maps for new local business leads with no website")

existing_niches = get_all_niches()

niche_choice = st.selectbox(
    "Niche",
    options=existing_niches + ["+ Add new niche"],
    index=None,
    placeholder="Select an existing niche, or add a new one",
)

# The "+ Add new niche" option is a sentinel value - if picked, we reveal
# a text box instead. Otherwise the selected niche IS the final answer.
if niche_choice == "+ Add new niche":
    niche = st.text_input("New niche name", placeholder="e.g. dentists")
else:
    niche = niche_choice

col1, col2 = st.columns(2)
with col1:
    business_type = st.text_input("Business type", placeholder="e.g. dentists, electricians")
with col2:
    city = st.text_input("City", placeholder="e.g. Lahore")

if st.button("Extract Leads", type="primary"):
    if not niche:
        st.error("Please select or enter a niche first.")
    elif not business_type or not city:
        st.error("Please enter both a business type and a city.")
    else:
        query = f"{business_type} in {city}"

        # This explicit instruction is the real fix for niche fragmentation -
        # we're not hoping the agent picks a consistent label anymore, we're
        # telling it exactly what to use, every time.
        agent_input = (
            f"Find {query} that don't have a website. "
            f"Whenever you call extract_leads_tool, always set niche exactly "
            f"to '{niche}' - do not use any other spelling or wording."
        )

        with st.spinner("Searching Google Maps... this can take a minute or two on the free tier."):
            executor = get_agent_executor()
            result = executor.invoke({"input": agent_input})

        # Pull the REAL numbers from intermediate_steps, rather than trusting
        # the LLM's own prose summary to be accurate - each step here is
        # (action, observation), where observation is the actual dictionary
        # our extract_leads_tool returned
        total_saved = 0
        total_found = 0
        for action, observation in result.get("intermediate_steps", []):
            if isinstance(observation, dict) and "newly_saved_to_db" in observation:
                total_saved += observation["newly_saved_to_db"]
                total_found += observation.get("raw_results_found", 0)

        st.success(
            f"Done! Saved {total_saved} new lead(s) to the '{niche}' niche "
            f"(scanned {total_found} raw results from Google Maps)."
        )
        st.caption(f"Agent's summary: {result['output']}")