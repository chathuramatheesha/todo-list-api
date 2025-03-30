import re
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from datetime import datetime

from app.core.enums import TaskStatus
from app.db.models import TaskPriority


# PAGINATION MODEL
class PaginationBase(BaseModel):
    page_number: int  # The current page number in the pagination.
    page_size: int  # The number of items displayed per page.
    total_items: int  # The total number of items available.
    total_pages: (
        int  # The total number of pages calculated based on total_items and page_size.
    )


# TASK-BASED SCHEMAS
# Basic task model with title, description, priority, and due date
class TaskBase(BaseModel):
    title: str = Field(min_length=5)  # Title must be at least 5 characters.
    description: str  # Description of the task.
    priority: (
        TaskPriority  # Priority of the task (Enum with values 'Low', 'Medium', 'High')
    )
    due_date: datetime  # Due date for the task (DateTime format).


# Task output model, includes ID and status
class TaskOut(TaskBase):
    id: int  # Task ID
    status: TaskStatus  # Task status (Enum)
    model_config = ConfigDict(from_attributes=True)  # Configure how the model works


# Task list model, includes task counts
class TaskListOut(PaginationBase):
    tasks: list[TaskOut]


# Task update model, allows for optional updates to title, description, status, and due date
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None

    # Validate that status is either "pending" or "completed"
    @field_validator("status")
    def validate_status(cls, value: Any) -> Self:
        if value not in [TaskStatus.pending, TaskStatus.completed]:
            raise ValueError("Status must be 'pending' or 'completed'")
        return value
