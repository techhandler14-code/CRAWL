"""
filters.py
 
Simple filtering logic applied to raw search results.
 
Note: this is a plain Python function, NOT a LangChain @tool like
apify_maps_tool. That's a deliberate choice - filtering to "no website only"
is a fixed rule every single time, not something the agent needs to reason
about or decide on. Remember from Module 1: not everything needs to be
agentic. Giving the LLM a "decision" it will make the same way 100% of the
time just adds unnecessary risk (it could get it wrong) for zero benefit.
"""
 
 
def filter_no_website(leads: list[dict]) -> list[dict]:
    """
    Takes a list of raw leads (as returned by apify_maps_tool) and keeps
    only the ones that do NOT have a website.
    """
    return [lead for lead in leads if not lead.get("has_website")]
 
 
# Quick manual test
if __name__ == "__main__":
    sample_leads = [
        {"name": "Business A", "has_website": True},
        {"name": "Business B", "has_website": False},
        {"name": "Business C", "has_website": False},
    ]
 
    filtered = filter_no_website(sample_leads)
    print(f"Started with {len(sample_leads)} leads, kept {len(filtered)} with no website:")
    for lead in filtered:
        print(lead)