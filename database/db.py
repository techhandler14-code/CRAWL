"""
db.py
 
Handles connecting to the SQLite database file, and creating the tables
(from models.py) the first time the app runs.
"""
 
import sqlite3
from pathlib import Path
 
from database.models import CREATE_LEADS_TABLE, CREATE_USAGE_LOG_TABLE
 
# Build an absolute path to data/leads.db, based on this file's own location,
# not on "wherever the terminal happens to be" - this avoids bugs where the
# database gets created in the wrong folder depending on how you run the script.
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "leads.db"
 
 
def get_connection() -> sqlite3.Connection:
    """
    Opens (or creates, if it doesn't exist yet) a connection to our
    database file. Every other file that needs to read/write leads will
    call this function to get a connection.
    """
    conn = sqlite3.connect(DB_PATH)
    # row_factory lets us access columns by name later (row["name"])
    # instead of only by position (row[0]) - much easier to read
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_db() -> None:
    """
    Creates the leads and usage_log tables if they don't already exist.
    Safe to call every time the app starts - won't wipe existing data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_LEADS_TABLE)
    cursor.execute(CREATE_USAGE_LOG_TABLE)
    conn.commit()
    conn.close()
    print(f"Database ready at: {DB_PATH}")
 
 
if __name__ == "__main__":
    init_db()