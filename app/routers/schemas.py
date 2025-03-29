from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: str
    priority: str
    due_date: datetime


class TaskOut(TaskBase):
    id: int
    is_complete: bool
    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_complete: bool | None = None
    due_date: datetime | None = None


class UserBase(BaseModel):
    fullname: str
    email: str


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    is_active: bool
    first_name: str
    model_config = ConfigDict(from_attributes=True)


class UserWithTasks(UserOut):
    tasks: list[TaskOut]
