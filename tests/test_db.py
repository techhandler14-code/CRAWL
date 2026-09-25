"""
test_db.py

Manually tests the CRUD functions: insert a fake lead, fetch it back,
update its status, and check the niche/usage helper functions too.

Run from project root with:
    python -m tests.test_db
"""

from database.crud import (
    delete_lead,
    insert_lead,
    get_leads,
    update_status,
    get_all_niches,
    log_usage,
    get_total_usage,
)

print("=" * 50)
print("TEST 1: Insert a fake lead")
print("=" * 50)

fake_lead = {
    "name": "Test Dental Clinic",
    "address": "123 Test Street, Lahore",
    "phone": "+923001234567",
    "has_website": False,
}

was_inserted = insert_lead(fake_lead, niche="dentists")
print(f"Inserted: {was_inserted}")  # should be True the first time

# try inserting the exact same lead again - should be skipped as a duplicate
was_inserted_again = insert_lead(fake_lead, niche="dentists")
print(f"Inserted again (should be False): {was_inserted_again}")

print()
print("=" * 50)
print("TEST 2: Fetch leads back")
print("=" * 50)

leads = get_leads(niche="dentists")
print(f"Found {len(leads)} lead(s) in 'dentists' niche:")
for lead in leads:
    print(lead)

print()
print("=" * 50)
print("TEST 3: Update status")
print("=" * 50)

if leads:
    lead_id = leads[0]["id"]
    update_status(lead_id, "Conversion")
    updated = get_leads(niche="dentists", status="Conversion")
    print(f"Leads now marked 'Conversion': {len(updated)}")
    for lead in updated:
        print(lead)

print()
print("=" * 50)
print("TEST 4: Get all niches")
print("=" * 50)

print(get_all_niches())

print()
print("=" * 50)
print("TEST 5: Usage logging")
print("=" * 50)

log_usage(action="test_search", credits_used=0.05)
print(f"Total credits used so far: {get_total_usage()}")

print()
print("=" * 50)
print("TEST 6: Delete lead")
print("=" * 50)

if leads:
    lead_id = leads[0]["id"]
    was_deleted = delete_lead(lead_id)
    print(f"Deleted lead id={lead_id}: {was_deleted}")
    remaining = get_leads(niche="dentists")
    print(f"Leads left in 'dentists' niche: {len(remaining)}")

print()
print("Done. Check output above for any unexpected results.")