"""
crud.py

The actual read/write functions everything else in the project will use
to talk to the database. CRUD = Create, Read, Update, Delete (we don't
need Delete for this project, so just the first three).
"""

from database.db import get_connection


def insert_lead(lead: dict, niche: str) -> bool:
    """
    Inserts one lead into the database, tagged with the given niche.
    Skips inserting if a lead with the same phone number already exists
    for this niche - this is our cross-run duplicate protection (the
    fuzzy_dedup_tool only catches duplicates WITHIN one extraction run;
    this catches duplicates ACROSS separate runs done on different days).

    Returns True if it was actually inserted, False if it was skipped
    as a duplicate.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM leads WHERE phone = ? AND niche = ?",
        (lead.get("phone"), niche),
    )
    if cursor.fetchone() is not None:
        conn.close()
        return False  # already exists, skip it

    cursor.execute(
        """
        INSERT INTO leads (name, address, phone, has_website, niche)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            lead.get("name"),
            lead.get("address"),
            lead.get("phone"),
            int(bool(lead.get("has_website"))),
            niche,
        ),
    )
    conn.commit()
    conn.close()
    return True


def insert_leads_bulk(leads: list[dict], niche: str) -> int:
    """
    Inserts a list of leads under one niche. Returns how many were
    actually new (not counting skipped duplicates).
    """
    inserted_count = 0
    for lead in leads:
        if insert_lead(lead, niche):
            inserted_count += 1
    return inserted_count


def get_leads(niche: str = None, status: str = None) -> list[dict]:
    """
    Fetches leads, optionally filtered by niche and/or status.
    Passing None for either means "don't filter by that field".

    Niche matching is intentionally PARTIAL, not exact - e.g. searching
    "dentist" will match a stored niche of "dentists". This is a
    deliberate robustness fix: exact matching is brittle when a human (or
    the agent) doesn't type the niche identically to how it was saved.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM leads WHERE 1=1"
    params = []

    if niche:
        # LIKE with % wildcards on both sides = "contains this text
        # anywhere" instead of "matches exactly". SQLite's LIKE is
        # case-insensitive for standard ASCII text by default.
        query += " AND niche LIKE ?"
        params.append(f"%{niche}%")

    if status:
        query += " AND status = ?"
        params.append(status)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # convert sqlite3.Row objects into plain dictionaries
    return [dict(row) for row in rows]


def update_status(lead_id: int, new_status: str) -> None:
    """Updates the status (Pending / No Reply / Conversion) of one lead."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE leads SET status = ? WHERE id = ?",
        (new_status, lead_id),
    )
    conn.commit()
    conn.close()


def get_all_niches() -> list[str]:
    """Returns every distinct niche currently in the database - powers
    the dropdown selector on the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT niche FROM leads ORDER BY niche")
    rows = cursor.fetchall()
    conn.close()
    return [row["niche"] for row in rows]


def log_usage(action: str, credits_used: float) -> None:
    """Records one usage event, so we can track spend against the
    $5/month free Apify credit."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usage_log (action, credits_used) VALUES (?, ?)",
        (action, credits_used),
    )
    conn.commit()
    conn.close()


def get_total_usage() -> float:
    """Returns total credits used so far (all time)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(credits_used) as total FROM usage_log")
    row = cursor.fetchone()
    conn.close()
    return row["total"] or 0.0


def get_monthly_usage() -> float:
    """
    Returns credits used so far THIS calendar month only. This is the
    number that actually matters for tracking against Apify's $5/month
    free credit, since it resets every month - an all-time total would
    keep growing forever and eventually look scarier than reality.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT SUM(credits_used) as total FROM usage_log
        WHERE strftime('%Y-%m', logged_at) = strftime('%Y-%m', 'now')
        """
    )
    row = cursor.fetchone()
    conn.close()
    return row["total"] or 0.0