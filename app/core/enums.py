from enum import Enum


# Enum representing the priority levels of a task
class TaskPriority(str, Enum):
    low = "low"  # Low priority
    medium = "medium"  # Medium priority
    high = "high"  # High priority


# Enum representing the possible fields by which tasks can be sorted
class TaskSortBy(str, Enum):
    status = "status"  # Sort by task status
    priority = "priority"  # Sort by task priority
    due_date = "due_date"  # Sort by task due date
    title = "title"  # Sort by task title


# Enum representing the order in which tasks are sorted
class TaskOrder(str, Enum):
    asc = "asc"  # Ascending order
    desc = "desc"  # Descending order


# Enum representing the possible statuses of a task
class TaskStatus(str, Enum):
    pending = "pending"  # Task is still pending
    completed = "completed"  # Task has been completed
    expired = "expired"  # Task has expired
