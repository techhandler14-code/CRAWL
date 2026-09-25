"""
apify_maps_tool.py
 
This is the agent's "search Google Maps" tool. Given a query like
"dentists in Lahore", it calls the Apify Google Maps Scraper actor and
returns a clean list of businesses (name, address, phone, website).
 
We deliberately do NOT use Apify's paid filter add-ons (like their built-in
"only businesses without a website" filter) because those cost extra on top
of the base scrape price. Instead, we pull the raw results at base price
and filter/clean them ourselves in Python later (free).
"""

import os
from apify_client import ApifyClient
from langchain.tools import tool
from dotenv import load_dotenv

from tools.filters import filter_no_website
from tools.phone_cleanup_tool import clean_phone_number
from tools.fuzzy_dedup_tool import deduplicate_leads
from database.crud import insert_leads_bulk, log_usage

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
ACTOR_ID = "compass/crawler-google-places"  # the standard Google Maps Scraper actor

def _run_apify_search(query: str, max_results: int = 50) -> list[dict]:
    """
    Does the actual work: calls Apify, waits for the run to finish,
    and pulls the results out of the dataset it produced.
    """
    client = ApifyClient(APIFY_API_KEY)
 
    # This is the input Apify's actor expects - see input schema docs
    run_input = {
        "searchStringsArray": [query],
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
    }
 
     # .call() runs the actor AND waits until it's done (blocking)
    run = client.actor(ACTOR_ID).call(run_input=run_input)
 
    # Results land in a "dataset" - newer apify-client versions return `run`
    # as an object with named attributes (not a dictionary), so we access
    # the dataset ID as run.default_dataset_id, not run["defaultDatasetId"]
    raw_results = []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        raw_results.append({
            "name": item.get("title"),
            "address": item.get("address"),
            "phone": item.get("phone") or item.get("phoneUnformatted"),
            "website": item.get("website"),
            "has_website": bool(item.get("website")),
            "category": item.get("categoryName"),
            "rating": item.get("totalScore"),
        })
 
    return raw_results

@tool
def apify_maps_tool(query: str, max_results: int = 50) -> list[dict]:
    """Search Google Maps for businesses matching a niche and location,
    e.g. "dentists in Lahore" or "electricians in Karachi".
    Returns a list of businesses, each with name, address, phone, website,
    and whether they have a website. Use this whenever you need to find
    new local business leads for a given niche and city."""
    return _run_apify_search(query, max_results)

@tool
def extract_leads_tool(query: str, niche: str, max_results: int = 50) -> dict:
    """Search Google Maps for businesses matching a query (e.g. "dentists
    in Lahore"), then automatically clean, filter to only businesses
    WITHOUT a website, remove duplicates, and save the results into the
    database under the given niche. This is the main tool to use when the
    user asks you to find/extract new leads. Call this once per query
    variation if you need broader coverage (e.g. try "dental clinic
    Lahore" too, not just "dentists in Lahore"). Returns a summary of how
    many leads were found, kept, and newly saved."""
 
    raw_results = _run_apify_search(query, max_results)
    # rough cost tracking: base actor price is ~$1.50 per 1,000 results
    log_usage(action=f"search: {query}", credits_used=len(raw_results) * 0.0015)
 
    no_website_only = filter_no_website(raw_results)
 
    for lead in no_website_only:
        lead["phone"] = clean_phone_number(lead.get("phone")) if lead.get("phone") else None
 
    deduped = deduplicate_leads(no_website_only)
    newly_inserted = insert_leads_bulk(deduped, niche=niche)
 
    return {
        "query": query,
        "raw_results_found": len(raw_results),
        "no_website_leads": len(no_website_only),
        "after_dedup": len(deduped),
        "newly_saved_to_db": newly_inserted,
    }


# Quick manual test - only runs if you execute this file directly
if __name__ == "__main__":
    results = _run_apify_search("dentists in Lahore", max_results=5)
    for r in results:
        print(r)