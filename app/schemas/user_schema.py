import re
from typing import Any, Self
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field

from app.schemas.task_schema import TaskOut


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
