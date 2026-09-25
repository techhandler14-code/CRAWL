"""
fuzzy_dedup_tool.py
 
Removes near-duplicate leads that can appear when the agent searches
multiple query variations for the same niche (e.g. "dentists" and
"dental clinic" both finding "City Dental" / "City Dental Clinic").
 
Like filters.py, this is a plain function, not an @tool - deciding
"are these the same business" has one correct answer, it's not something
the agent needs to reason about each time.
"""

from rapidfuzz import fuzz

def deduplicate_leads(leads: list[dict], name_threshold: int = 85) -> list[dict]:
    """
    Takes a list of leads and returns a new list with near-duplicates
    removed, based on how similar their names are.
 
    name_threshold: how similar two names must be (0-100) to be treated
    as the same business. 85 is a sensible default - close enough to catch
    "City Dental" vs "City Dental Clinic", but not so loose that two
    genuinely different businesses get merged.
    """
    unique_leads = []
 
    for lead in leads:
        is_duplicate = False
 
        for existing in unique_leads:
            similarity = fuzz.token_set_ratio(lead["name"], existing["name"])
            if similarity >= name_threshold:
                is_duplicate = True
                break
 
        if not is_duplicate:
            unique_leads.append(lead)
 
    return unique_leads
 
 
# Quick manual test
if __name__ == "__main__":
    sample_leads = [
        {"name": "City Dental Clinic", "phone": "111"},
        {"name": "City Dental", "phone": "111"},          # near-duplicate of above
        {"name": "Smile Hub Clinics", "phone": "222"},     # genuinely different
        {"name": "Smile Hub Clinic", "phone": "222"},      # near-duplicate of above
    ]
 
    result = deduplicate_leads(sample_leads)
    print(f"Started with {len(sample_leads)} leads, kept {len(result)} after dedup:")
    for lead in result:
        print(lead)