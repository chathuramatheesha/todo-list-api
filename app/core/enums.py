from enum import Enum


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskSortBy(str, Enum):
    status = "status"
    priority = "priority"


class TaskOrder(str, Enum):
    asc = "asc"
    desc = "desc"
