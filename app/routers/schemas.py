import re
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from datetime import datetime

from app.core.enums import TaskStatus
from app.db.models import TaskPriority


class TaskBase(BaseModel):
    title: str = Field(min_length=5)
    description: str
    priority: TaskPriority
    due_date: datetime


class TaskOut(TaskBase):
    id: int
    status: TaskStatus
    model_config = ConfigDict(from_attributes=True)


class TaskListOut(TaskOut):
    tasks_length: int
    completed_task_length: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None

    @field_validator("status")
    def validate_status(cls, value: Any) -> Self:
        if not (
            value and (value == TaskStatus.pending or value == TaskStatus.completed)
        ):
            raise ValueError("Task status must be (pending, completed)")

        return value


class UserBase(BaseModel):
    fullname: str = Field(min_length=8)
    email: EmailStr


class UserIn(UserBase):
    password: str

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


class UserOut(UserBase):
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserWithTasks(UserOut):
    tasks: list[TaskOut]
