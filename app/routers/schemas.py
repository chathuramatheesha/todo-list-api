import re
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from datetime import datetime

from app.core.enums import TaskStatus
from app.db.models import TaskPriority


class PaginationBase(BaseModel):
    page_number: int
    page_size: int
    total_items: int
    total_pages: int


# TASK-BASED SCHEMAS
# Basic task model with title, description, priority, and due date
class TaskBase(BaseModel):
    title: str = Field(min_length=5)  # Title must be at least 5 characters
    description: str  # Description of the task
    priority: TaskPriority  # Priority of the task (Enum)
    due_date: datetime  # Due date for the task


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


# USER-RELATED SCHEMAS
# Basic user model with fullname and email
class UserBase(BaseModel):
    fullname: str = Field(min_length=8)  # Fullname must be at least 8 characters
    email: EmailStr  # Valid email address


# User input model with password validation
class UserIn(UserBase):
    password: str  # User password

    # Password validation (min length, uppercase, number, special char)
    @field_validator("password")
    def validate_password(cls, value: Any) -> Self:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value


# User output model with is_active status
class UserOut(UserBase):
    is_active: bool  # Whether the user is active or not
    model_config = ConfigDict(from_attributes=True)  # Configure how the model works


# User model with tasks, includes task details
class UserWithTasks(UserOut):
    tasks: list[TaskOut]  # List of tasks associated with the user
