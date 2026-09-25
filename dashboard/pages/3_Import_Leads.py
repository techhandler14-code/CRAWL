"""
3_Import_Leads.py

Lets you bring in leads you already collected manually (CSV or Excel).
Unlike Extract Leads, this doesn't go through the agent - there's no
reasoning needed here (you already know exactly what file and what niche
you want), so we call import_leads() directly. Faster, and avoids
burning an LLM call for a task with no real decision to make.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import tempfile
import os

from database.crud import get_all_niches
from utils.styling import inject_custom_css, render_sidebar_branding
from tools.import_leads_tool import import_leads

st.set_page_config(page_title="Import Leads - Lead Extractor", page_icon="📍", layout="wide")
inject_custom_css()
render_sidebar_branding()

st.markdown("# Import Leads")
st.caption("Bring in leads you've already collected manually, from a CSV or Excel file")

existing_niches = get_all_niches()

niche_choice = st.selectbox(
    "Niche / label",
    options=existing_niches + ["+ Add new niche"],
    index=None,
    placeholder="Select an existing niche, or add a new one",
)

if niche_choice == "+ Add new niche":
    niche = st.text_input("New niche name", placeholder="e.g. plumbers")
else:
    niche = niche_choice

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if st.button("Import", type="primary"):
    if not niche:
        st.error("Please select or enter a niche first.")
    elif not uploaded_file:
        st.error("Please upload a file first.")
    else:
        # import_leads() expects a real file path on disk, but Streamlit
        # gives us the uploaded file as bytes in memory - so we write it
        # to a temporary file first, just so our existing function (built
        # back in Phase 5) can read it exactly like any other file.
        file_extension = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            with st.spinner("Importing and cleaning your leads..."):
                result = import_leads(tmp_file_path, niche)

            st.success(
                f"Imported {result['newly_inserted']} new lead(s) into '{niche}' "
                f"(found {result['total_rows_in_file']} rows, "
                f"{result['after_dedup']} unique after removing duplicates)."
            )
        except ValueError as e:
            st.error(str(e))
        finally:
            os.remove(tmp_file_path)  # clean up the temporary file either way