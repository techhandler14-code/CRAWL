"""
models.py
 
Defines the shape (schema) of our two database tables, as plain SQL
"CREATE TABLE" statements. We're using plain SQLite (no ORM library) to
keep things simple and match our locked tech stack - just Python's
built-in sqlite3, nothing extra to install or learn.
 
db.py (next file) will run these statements once, when the app first
starts, to make sure the tables exist.
"""

CREATE_LEADS_TABLE = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    has_website INTEGER NOT NULL DEFAULT 0,
    niche TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_USAGE_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    credits_used REAL NOT NULL,
    logged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""