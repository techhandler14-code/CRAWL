"""
import_leads_tool.py
 
Lets you bring in leads you already collected manually (CSV or Excel file),
instead of only ones extracted via Apify. Reuses fuzzy_dedup_tool and
phone_cleanup_tool so imported leads get the same cleaning as scraped ones.
 
Unlike filters.py/fuzzy_dedup_tool.py/phone_cleanup_tool.py, this ONE is a
real @tool - because "should I import this file, and what should I label
it?" genuinely depends on what the user asks for in their prompt. That's
a real decision, not a fixed rule, so the agent needs to see it.
"""

import pandas as pd
from langchain.tools import tool

from tools.phone_cleanup_tool import clean_phone_number
from tools.fuzzy_dedup_tool import deduplicate_leads
from database.crud import insert_leads_bulk

# Common header variations we'll recognize, mapped to our standard field
# names. Add more synonyms here anytime you hit a file with a header this
# doesn't catch.

COLUMN_SYNONYMS = {
    "name": ["name", "business name", "company name", "business_name"],
    "address": ["address", "location", "business address"],
    "phone": ["phone", "phone number", "contact", "contact number", "mobile"],
    "website": ["website", "site", "url", "web"],
}

def _map_columns(df: pd.DataFrame) -> dict:
    """
    Figures out which actual column in the file corresponds to which
    standard field we need, using the synonym list above.
    Returns something like {"name": "Business Name", "phone": "Contact #"}.
    """
    normalized_cols = {col.strip().lower(): col for col in df.columns}
    mapping = {}
 
    for standard_field, synonyms in COLUMN_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in normalized_cols:
                mapping[standard_field] = normalized_cols[synonym]
                break
 
    return mapping

def _get_cell(row: pd.Series, column_name: str | None) -> str | None:
    """
    Safely reads one cell's value as a clean string, or None if the
    column doesn't exist or the cell is empty. Handles pandas' quirk of
    turning empty cells into NaN (a special "not a number" float) instead
    of just None.
    """
    if column_name is None:
        return None
    value = row.get(column_name)
    if pd.isna(value):
        return None
    return str(value).strip()

def import_leads(file_path: str, label: str) -> dict:
    """Does the real work: reads the file, maps columns, cleans data,
    dedups, and saves to the database."""
 
    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type. Please use a .csv or .xlsx file.")
 
    column_map = _map_columns(df)
 
    if "name" not in column_map:
        raise ValueError(
            f"Couldn't find a business name column. Columns found in file: {list(df.columns)}"
        )
 
    raw_leads = []
    for _, row in df.iterrows():
        website_value = _get_cell(row, column_map.get("website"))
        raw_phone = _get_cell(row, column_map.get("phone"))
 
        raw_leads.append({
            "name": _get_cell(row, column_map["name"]),
            "address": _get_cell(row, column_map.get("address")),
            "phone": clean_phone_number(raw_phone) if raw_phone else None,
            "has_website": bool(website_value),
        })
 
    deduped_leads = deduplicate_leads(raw_leads)
    inserted_count = insert_leads_bulk(deduped_leads, niche=label)
 
    return {
        "total_rows_in_file": len(df),
        "after_dedup": len(deduped_leads),
        "newly_inserted": inserted_count,
    }

@tool
def import_leads_tool(file_path: str, label: str) -> dict:
    """Import leads from a CSV or Excel file already on disk into the
    database, tagging them with the given label as their niche. Use this
    when the user asks to import, upload, or bring in leads from a file
    they already have. file_path must be the full path to a .csv or
    .xlsx file, and label is the niche name to tag the imported leads with."""
    return import_leads(file_path, label)

if __name__ == "__main__":
    import sys
 
    if len(sys.argv) != 3:
        print("Usage: python tools/import_leads_tool.py <file_path> <label>")
    else:
        result = import_leads(sys.argv[1], sys.argv[2])
        print(result)