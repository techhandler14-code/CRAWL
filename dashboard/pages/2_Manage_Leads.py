"""
2_Manage_Leads.py

Browse your leads one niche at a time, and update their status
(Pending / No Reply / Conversion) directly in an editable table.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd

from database.crud import get_all_niches, get_leads, update_status
from utils.styling import inject_custom_css, render_sidebar_branding

st.set_page_config(page_title="Manage Leads - Lead Extractor", page_icon="📍", layout="wide")
inject_custom_css()
render_sidebar_branding()

st.markdown("# Manage Leads")
st.caption("Browse leads by niche and update their status")

niches = get_all_niches()

if not niches:
    st.info("No leads yet. Head to **Extract Leads** to find your first batch.")
else:
    selected_niche = st.selectbox("Niche", options=niches)
    leads = get_leads(niche=selected_niche)

    if not leads:
        st.info(f"No leads found for '{selected_niche}'.")
    else:
        # Build a table with just the columns worth showing, in a sensible order
        df = pd.DataFrame(leads)
        display_df = df[["id", "name", "address", "phone", "status"]].copy()

        st.caption(f"{len(display_df)} leads in '{selected_niche}'")

        # st.data_editor renders an editable table. column_config lets us
        # control each column individually - most stay read-only (disabled),
        # but "status" becomes an actual dropdown the user can change inline.
        edited_df = st.data_editor(
            display_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "name": st.column_config.TextColumn("Business Name", disabled=True, width="medium"),
                "address": st.column_config.TextColumn("Address", disabled=True, width="large"),
                "phone": st.column_config.TextColumn("Phone", disabled=True, width="medium"),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "No Reply", "Conversion"],
                    required=True,
                    width="small",
                ),
            },
            # id stays in the underlying data (we need it to save changes
            # back to the right row) but leaving it out of column_order
            # means it never actually takes up space on screen
            column_order=["name", "phone", "address", "status"],
            hide_index=True,
            use_container_width=True,
            key=f"editor_{selected_niche}",
        )

        if st.button("Save changes", type="primary"):
            changes = 0
            for _, row in edited_df.iterrows():
                original_status = display_df.loc[
                    display_df["id"] == row["id"], "status"
                ].values[0]

                if row["status"] != original_status:
                    update_status(int(row["id"]), row["status"])
                    changes += 1

            if changes:
                st.success(f"Updated {changes} lead(s).")
                st.rerun()  # refresh the page so the table reloads from the DB
            else:
                st.info("No changes to save.")