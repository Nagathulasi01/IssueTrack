import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Any
from app.models import IssueCreate, IssueUpdate


def get_current_utc_timestamp() -> str:
    """Returns the current ISO-8601 formatted UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def create_issue(conn: sqlite3.Connection, issue: IssueCreate) -> dict:
    """
    Inserts a new issue into the database using parameterized queries.
    Prevents SQL injection vulnerabilities.
    """
    now = get_current_utc_timestamp()
    query = """
        INSERT INTO issues (title, description, status, priority, assigned_to, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    params = (
        issue.title,
        issue.description or "",
        issue.status.value,
        issue.priority.value,
        issue.assigned_to or "Unassigned",
        now,
        now
    )

    with conn:
        cursor = conn.execute(query, params)
        new_id = cursor.lastrowid

    return get_issue_by_id(conn, new_id)


def get_issue_by_id(conn: sqlite3.Connection, issue_id: int) -> Optional[dict]:
    """
    Retrieves a single issue by its primary key ID using a parameterized query.
    """
    query = "SELECT * FROM issues WHERE id = ?;"
    cursor = conn.execute(query, (issue_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_issues(
    conn: sqlite3.Connection,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[dict]:
    """
    Retrieves a list of issues with optional parameterized filters:
    - search: substring search against the issue title
    - status: exact match for status (Open, In Progress, Resolved)
    - priority: exact match for priority (Low, Medium, High)
    - limit & offset: pagination
    """
    clauses = ["1=1"]
    params: List[Any] = []

    if search and search.strip():
        clauses.append("title LIKE ?")
        params.append(f"%{search.strip()}%")

    if status and status.strip():
        clauses.append("status = ?")
        params.append(status.strip())

    if priority and priority.strip():
        clauses.append("priority = ?")
        params.append(priority.strip())

    where_sql = " AND ".join(clauses)
    query = f"""
        SELECT * FROM issues
        WHERE {where_sql}
        ORDER BY id DESC
        LIMIT ? OFFSET ?;
    """
    params.extend([max(1, min(limit, 500)), max(0, offset)])

    cursor = conn.execute(query, tuple(params))
    return [dict(row) for row in cursor.fetchall()]


def update_issue(
    conn: sqlite3.Connection,
    issue_id: int,
    issue_update: IssueUpdate
) -> Optional[dict]:
    """
    Updates an issue with partially or fully provided fields.
    Updates the updated_at timestamp upon modification.
    """
    existing = get_issue_by_id(conn, issue_id)
    if not existing:
        return None

    update_data = issue_update.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    # Handle enum conversions if needed
    for key in ("status", "priority"):
        if key in update_data and hasattr(update_data[key], "value"):
            update_data[key] = update_data[key].value

    now = get_current_utc_timestamp()
    update_data["updated_at"] = now

    set_clauses = [f"{col} = ?" for col in update_data.keys()]
    values = list(update_data.values())
    values.append(issue_id)

    query = f"UPDATE issues SET {', '.join(set_clauses)} WHERE id = ?;"

    with conn:
        conn.execute(query, tuple(values))

    return get_issue_by_id(conn, issue_id)


def delete_issue(conn: sqlite3.Connection, issue_id: int) -> bool:
    """
    Deletes an issue by its primary key ID using a parameterized query.
    Returns True if an issue was deleted, False if no issue matched the ID.
    """
    query = "DELETE FROM issues WHERE id = ?;"
    with conn:
        cursor = conn.execute(query, (issue_id,))
        return cursor.rowcount > 0


def get_stats(conn: sqlite3.Connection) -> dict:
    """
    Aggregates issue metrics across statuses and priorities in a single efficient query.
    Used for live dashboard summary metrics.
    """
    query = """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END), 0) AS open,
            COALESCE(SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END), 0) AS in_progress,
            COALESCE(SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END), 0) AS resolved,
            COALESCE(SUM(CASE WHEN priority = 'Low' THEN 1 ELSE 0 END), 0) AS low_priority,
            COALESCE(SUM(CASE WHEN priority = 'Medium' THEN 1 ELSE 0 END), 0) AS medium_priority,
            COALESCE(SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END), 0) AS high_priority
        FROM issues;
    """
    cursor = conn.execute(query)
    row = cursor.fetchone()
    if row:
        return {
            "total": row["total"],
            "open": row["open"],
            "in_progress": row["in_progress"],
            "resolved": row["resolved"],
            "low_priority": row["low_priority"],
            "medium_priority": row["medium_priority"],
            "high_priority": row["high_priority"]
        }
    return {
        "total": 0, "open": 0, "in_progress": 0, "resolved": 0,
        "low_priority": 0, "medium_priority": 0, "high_priority": 0
    }

