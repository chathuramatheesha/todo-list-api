from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: str
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


class UserOut(UserBase):
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

    @property
    def first_name(self) -> str:
        return self.fullname.split(" ")[0]


class UserWithTasks(UserOut):
    tasks: list[TaskOut]
