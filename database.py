"""
database.py
------------
Handles all SQLite storage: creating the table, inserting articles,
and — most importantly — preventing duplicate rows when the scraper
re-runs and re-finds articles it already saved.

Basic concept for anyone new to SQL:
  A "table" is like an Excel sheet. Each row = one article.
  Each column = one piece of info about that article (title, url, etc).
"""

import sqlite3
from config import DATABASE_PATH


def get_connection():
    """Opens a connection to the SQLite database file.
    If the file doesn't exist yet, SQLite creates it automatically."""
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    """Creates the articles table if it doesn't already exist.
    Run this once when the project starts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,      -- UNIQUE = database itself blocks duplicate URLs
            summary TEXT,
            category TEXT,
            sentiment TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def article_exists(url: str) -> bool:
    """Checks if we've already stored this exact URL.
    This is our dedup check BEFORE we even try to insert."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def insert_article(source: str, title: str, url: str) -> bool:
    """Inserts a new article. Returns True if inserted, False if it
    was a duplicate (already existed) or something went wrong.

    We check article_exists() first (cheap, clear, explainable),
    AND we rely on the UNIQUE constraint on the url column as a
    safety net (belt-and-suspenders — this matters if the pipeline
    ever runs two scrapers in parallel and both check at the same time)."""
    if article_exists(url):
        return False

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO articles (source, title, url) VALUES (?, ?, ?)",
            (source, title, url),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This fires if the UNIQUE constraint catches a duplicate
        # that slipped past our article_exists() check.
        return False
    finally:
        conn.close()


def get_all_articles():
    """Fetches every stored article — useful for the dashboard and Excel export."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles ORDER BY scraped_at DESC")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


if __name__ == "__main__":
    # Running "python database.py" directly sets up the table
    # and shows you it works, with no scraping involved yet.
    init_db()
    print(f"Database ready at: {DATABASE_PATH}")
    print(f"Current article count: {len(get_all_articles())}")
