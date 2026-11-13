import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_db
from app.models import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueStatus,
    IssuePriority,
    StatsResponse,
    MessageResponse
)
from app import crud

router = APIRouter(
    prefix="/api/issues",
    tags=["Issues"]
)


@router.post(
    "",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new issue",
    description="Registers a new issue in the system with validated title, priority, status, and assignee."
)
def create_issue(
    issue: IssueCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Creates a new issue in the database."""
    created = crud.create_issue(conn, issue)
    return created


@router.get(
    "",
    response_model=List[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="List issues with search and filter",
    description="Fetch issues filtered by title substring, status, priority, and pagination options."
)
def list_issues(
    search: Optional[str] = Query(None, description="Search keyword in issue title"),
    status: Optional[IssueStatus] = Query(None, description="Filter by status (Open, In Progress, Resolved)"),
    priority: Optional[IssuePriority] = Query(None, description="Filter by priority (Low, Medium, High)"),
    limit: int = Query(100, ge=1, le=500, description="Max issues to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Lists issues matching optional search, status, and priority parameters."""
    status_val = status.value if status else None
    priority_val = priority.value if priority else None
    issues = crud.get_issues(
        conn,
        search=search,
        status=status_val,
        priority=priority_val,
        limit=limit,
        offset=offset
    )
    return issues


@router.get(
    "/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get issue metrics and dashboard counts",
    description="Calculates summary counts for total, open, in-progress, and resolved issues."
)
def get_issue_statistics(conn: sqlite3.Connection = Depends(get_db)):
    """Computes aggregate issue metrics for the dashboard cards."""
    return crud.get_stats(conn)


@router.get(
    "/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get issue by ID",
    description="Retrieves full details of a specific issue."
)
def get_issue(
    issue_id: int,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Retrieves an issue by ID or raises 404 if not found."""
    issue = crud.get_issue_by_id(conn, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found."
        )
    return issue


@router.put(
    "/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an issue",
    description="Updates issue fields (title, description, status, priority, assignee)."
)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Updates an existing issue or raises 404 if not found."""
    updated = crud.update_issue(conn, issue_id, issue_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found."
        )
    return updated


@router.delete(
    "/{issue_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an issue",
    description="Permanently deletes an issue by its ID."
)
def delete_issue(
    issue_id: int,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Deletes an issue or raises 404 if not found."""
    deleted = crud.delete_issue(conn, issue_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found."
        )
    return MessageResponse(
        message=f"Issue #{issue_id} has been successfully deleted.",
        id=issue_id
    )

