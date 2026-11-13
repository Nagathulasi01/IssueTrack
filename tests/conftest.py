import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, get_db

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_issues.db")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure clean test environment before tests run, clean up after session."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    # Initialize schema in test database
    init_db(TEST_DB_PATH)

    yield

    # Teardown test database file after all tests finish
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


@pytest.fixture
def db_conn():
    """Provides a fresh database connection to the test database for direct test queries."""
    conn = sqlite3.connect(TEST_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def client():
    """
    TestClient fixture that overrides get_db dependency
    to use the isolated test database.
    """
    def override_get_db():
        conn = sqlite3.connect(TEST_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_tables_between_tests(db_conn):
    """Cleans table rows between individual test executions to prevent test contamination."""
    with db_conn:
        db_conn.execute("DELETE FROM issues;")
        try:
            db_conn.execute("DELETE FROM sqlite_sequence WHERE name='issues';")
        except sqlite3.OperationalError:
            pass
    yield

