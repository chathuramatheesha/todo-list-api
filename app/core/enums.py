from enum import Enum


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskSortBy(str, Enum):
    status = "status"
    priority = "priority"
    due_date = "due_date"
    title = "title"


class TaskOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    expired = "expired"
