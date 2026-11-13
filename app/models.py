from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class IssueStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class IssuePriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class IssueBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Concise title summarizing the bug or task",
        examples=["Fix 500 error on user payment webhook"]
    )
    description: Optional[str] = Field(
        default="",
        max_length=2000,
        description="Detailed steps to reproduce or acceptance criteria"
    )
    status: IssueStatus = Field(
        default=IssueStatus.OPEN,
        description="Current lifecycle status of the issue"
    )
    priority: IssuePriority = Field(
        default=IssuePriority.MEDIUM,
        description="Business and technical urgency"
    )
    assigned_to: Optional[str] = Field(
        default="Unassigned",
        max_length=60,
        description="Name or handle of assigned software engineer"
    )

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) < 3:
            raise ValueError("Title must be at least 3 characters after trimming whitespace")
        return trimmed

    @field_validator("assigned_to")
    @classmethod
    def normalize_assigned_to(cls, value: Optional[str]) -> str:
        if not value or not value.strip():
            return "Unassigned"
        return value.strip()


class IssueCreate(IssueBase):
    """Schema used when submitting a new issue."""
    pass


class IssueUpdate(BaseModel):
    """Schema used when updating an existing issue (supports partial updates)."""
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assigned_to: Optional[str] = Field(None, max_length=60)

    @field_validator("title")
    @classmethod
    def validate_title_if_present(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if len(trimmed) < 3:
                raise ValueError("Title must be at least 3 characters after trimming whitespace")
            return trimmed
        return value

    @field_validator("assigned_to")
    @classmethod
    def normalize_assigned_if_present(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            return trimmed if trimmed else "Unassigned"
        return value


class IssueResponse(IssueBase):
    """Schema for issues returned from API endpoints."""
    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class StatsResponse(BaseModel):
    """Metrics for the dashboard summary cards."""
    total: int
    open: int
    in_progress: int
    resolved: int
    low_priority: int
    medium_priority: int
    high_priority: int


class MessageResponse(BaseModel):
    """Standard message response for actions such as deletion."""
    message: str
    id: Optional[int] = None

