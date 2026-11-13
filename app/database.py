import os
import sqlite3
from typing import Generator

# Database file location (can be overridden by environment variable for testing)
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "issuetrack.db")
DATABASE_PATH = os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)


def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Creates and returns a SQLite database connection.
    - check_same_thread=False: Allows connection to be used across FastAPI async worker threads.
    - sqlite3.Row: Enables accessing query results by column name as dictionaries.
    - journal_mode=WAL: Write-Ahead Logging allows concurrent readers alongside a writer.
    """
    path = db_path or DATABASE_PATH
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    # WAL mode improves SQLite concurrency for web apps
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def seed_initial_data_if_empty(conn: sqlite3.Connection) -> None:
    """
    Populates sample real-world issues if the database is newly initialized.
    Demonstrates realistic issue tracking data for portfolio showcases and interviews.
    """
    cursor = conn.execute("SELECT COUNT(*) AS count FROM issues;")
    count = cursor.fetchone()["count"]
    if count == 0:
        sample_issues = [
            (
                "Car policy PDF download returns 404 for newly issued policies",
                "Users attempting to download policy documents immediately after payment receive 404. S3 upload async worker delay needs queue retry logic.",
                "Open",
                "High",
                "Priya Sharma",
                "2026-11-12 10:15:00",
                "2026-11-12 10:15:00"
            ),
            (
                "Implement exponential backoff retry for claim settlement webhook",
                "Downstream banking partner occasionally encounters 503 throttling. Need 3 retries with jittered exponential backoff.",
                "In Progress",
                "High",
                "Aman Gupta",
                "2026-11-12 14:30:00",
                "2026-11-13 09:00:00"
            ),
            (
                "Vehicle registration number validator fails on commercial plates",
                "Regex for state vehicle registration numbers rejects valid commercial vehicle formats (e.g. DL 1C AA 1234).",
                "In Progress",
                "Medium",
                "Sneha Roy",
                "2026-11-13 08:20:00",
                "2026-11-13 11:45:00"
            ),
            (
                "Optimize premium calculation quote API response latency",
                "Quotation API response p95 latency reached 620ms during peak marketing campaign. Added Redis caching for static vehicle make/model risk matrices.",
                "Resolved",
                "Medium",
                "Vikram Patel",
                "2026-11-10 11:00:00",
                "2026-11-12 16:30:00"
            ),
            (
                "Update FAQ link on insurance renewal landing page",
                "Help button on renewal dashboard redirects to outdated 2024 terms document. Update target URL to current knowledge base article.",
                "Resolved",
                "Low",
                "Rohan Verma",
                "2026-11-09 15:40:00",
                "2026-11-11 12:10:00"
            )
        ]

        query = """
            INSERT INTO issues (title, description, status, priority, assigned_to, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        with conn:
            conn.executemany(query, sample_issues)


def init_db(db_path: str = None) -> None:
    """
    Initializes the database schema if not already present.
    Creates tables and performance indexes using safe, parameterized/DDL queries.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                    description TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open', 'In Progress', 'Resolved')),
                    priority TEXT NOT NULL DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High')),
                    assigned_to TEXT DEFAULT 'Unassigned',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # Performance indexes for search, status, and priority filtering
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_issues_priority ON issues(priority);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_issues_created_at ON issues(created_at DESC);
            """)

        # Seed sample issues only for development database (skip if in test mode)
        if not (db_path and "test" in db_path):
            seed_initial_data_if_empty(conn)
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    FastAPI dependency that yields a database connection per request
    and ensures it is cleanly closed after request execution.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
