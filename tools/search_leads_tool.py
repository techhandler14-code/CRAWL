"""
search_leads_tool.py

Lets the agent answer questions about leads ALREADY in the database, e.g.
"show me pending dentist leads". This is a thin wrapper - all the real
query logic already exists in crud.get_leads() from Phase 4, we're just
exposing it as something the agent can call.

This IS a real @tool (like import_leads_tool, unlike filters/dedup/cleanup),
because figuring out which niche/status the user means from their sentence
is a genuine judgment call, not a fixed rule.
"""

from langchain.tools import tool
from database.crud import get_leads, get_all_niches


@tool
def search_leads_tool(niche: str = None, status: str = None) -> list[dict]:
    """Search for leads already saved in the database, optionally filtered
    by niche and/or status. Use this when the user asks to see, find,
    check on, or count leads they already have saved - NOT for finding
    brand new leads on Google Maps (use extract_leads_tool for that
    instead). Valid status values are EXACTLY one of: "Pending",
    "No Reply", "Conversion" - no other value is valid. To get leads of
    ANY status, do not include the status argument at all (do not pass
    "all" or "any" - simply omit the argument entirely). Niche matching
    is partial, so "dentist" will correctly match a saved niche of
    "dentists" - you do not need to guess the exact plural/spelling."""
    return get_leads(niche=niche, status=status)


@tool
def list_niches_tool() -> list[str]:
    """Returns the list of every distinct niche currently saved in the
    database. Use this when the user asks how many niches there are,
    what niches exist, or to list/see all niches. This takes no
    arguments."""
    return get_all_niches()