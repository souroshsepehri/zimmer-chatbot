"""
One-off migration script to add the tracked_site_id column to the faqs table.

This script is safe to run multiple times because it checks for the column
existence before attempting to add it.
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import core.config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import settings


def main():
    """Add tracked_site_id column to faqs table if it doesn't exist."""
    # Ensure we only run this if the URL starts with "sqlite"
    if not settings.database_url.startswith("sqlite"):
        print(f"Database URL is not SQLite: {settings.database_url}")
        print("This migration script only works with SQLite databases.")
        sys.exit(1)

    # Derive the DB path from the URL in the same way as core/db.py
    # For example, for "sqlite:///./app.db" the path should be "./app.db"
    db_path = settings.database_url.replace("sqlite:///", "")

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(faqs)")
        columns = cursor.fetchall()
        
        # Check if tracked_site_id column exists
        # PRAGMA table_info returns tuples: (cid, name, type, notnull, default_value, pk)
        column_exists = any(col[1] == "tracked_site_id" for col in columns)

        if column_exists:
            print("tracked_site_id already exists on faqs, nothing to do.")
            return

        # Column does not exist, add it
        cursor.execute("ALTER TABLE faqs ADD COLUMN tracked_site_id INTEGER")
        conn.commit()
        print("Added tracked_site_id column to faqs.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

