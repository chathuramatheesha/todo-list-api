from fastapi import APIRouter, Depends, status
from fastapi.params import Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.crud import task_crud as crud
from app.db.database import get_db
from app.db.models import User
from app.core.enums import TaskPriority, TaskSortBy, TaskOrder, TaskStatus
from app.routers.schemas import TaskBase, TaskOut, TaskUpdate, TaskListOut
from app.crud.user_crud import get_current_user

db_dependency: Annotated[AsyncSession, Depends(get_db)]
user_dependency: Annotated[User, Depends(get_current_user)]

router = APIRouter()


# POST /tasks
# POST request to create a new task
@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskBase,  # The request body which contains the task details
    current_user: Annotated[
        User, Depends(get_current_user)
    ],  # The current authenticated user, fetched from the dependency
    db: Annotated[
        AsyncSession, Depends(get_db)
    ],  # The database session, fetched from the dependency
):
    # Calling the CRUD function to create the task in the database
    return await crud.create_task(request, current_user, db)


# GET /tasks
# GET request to retrieve a list of tasks
@router.get("", response_model=TaskListOut)
async def get_tasks(
    current_user: Annotated[
        User, Depends(get_current_user)
    ],  # The current authenticated user, fetched from the dependency
    db: Annotated[
        AsyncSession, Depends(get_db)
    ],  # The database session, fetched from the dependency
    search: (
        str | None
    ) = Query(  # Optional search query to filter tasks by title or description
        None,
        description="Search for tasks by matching keywords in the title or description.",
    ),
    filter_status: (
        TaskStatus | None
    ) = Query(  # Optional filter to get tasks by their status (pending, expired, completed)
        None,
        description="Filter by status (pending, expired, completed)",
    ),
    filter_priority: (
        TaskPriority | None
    ) = Query(  # Optional filter to get tasks by their priority (low, medium, high)
        None,
        description=f"Filter by priority ({', '.join(TaskPriority)})",
    ),
    sort_by: (
        TaskSortBy | None
    ) = Query(  # Optional filter to sort tasks by a specific field (status, priority, etc.)
        None,
        description=f"Sort by ({', '.join(TaskSortBy)})",
    ),
    order: (
        TaskOrder | None
    ) = Query(  # Optional parameter to specify the order (ascending or descending)
        None,
        description="Order by (asc, desc)",
    ),
    page_number: int = 1,  # The page number to return (default is 1) (Optional)
    page_size: int = 10,  # The number of tasks to return per page (default is 10) (Optional)
):
    # Calling the CRUD function to fetch the tasks with the applied filters and sorting options
    return await crud.get_tasks(
        search=search,  # Search term for filtering tasks by title or description
        filter_status=filter_status,  # Status filter for filtering tasks
        filter_priority=filter_priority,  # Priority filter for filtering tasks
        sort_by=sort_by,  # Sorting field
        order=order,  # Sorting order (asc or desc)
        page_number=page_number,  # Page number
        page_size=page_size,  # Page size (tasks limit)
        user=current_user,  # Current authenticated user
        db=db,  # Database session
    )


# GET /tasks/{task_id}
# GET request to retrieve a specific task by its ID
@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    current_user: Annotated[
        User, Depends(get_current_user)
    ],  # The current authenticated user, fetched from the dependency
    db: Annotated[
        AsyncSession, Depends(get_db)
    ],  # The database session, fetched from the dependency
    task_id: int = Path(Ellipsis),  # Task ID provided as part of the URL path
):
    # Calling the CRUD function to fetch the task by ID
    return await crud.get_task(task_id, current_user, db)


# PATCH /tasks/{task_id}
# PATCH request to update an existing task by its ID
@router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task(
    request: TaskUpdate,  # The task data to update, validated by the TaskUpdate model
    current_user: Annotated[
        User, Depends(get_current_user)
    ],  # The current authenticated user, fetched from the dependency
    db: Annotated[
        AsyncSession, Depends(get_db)
    ],  # The database session, fetched from the dependency
    task_id: int = Path(Ellipsis),  # Task ID provided as part of the URL path
):
    # Calling the CRUD function to update the task based on the task ID and input data
    return await crud.update_task(request, task_id, current_user, db)


# DELETE /tasks/{task_id}
# DELETE request to delete an existing task by its ID
@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    current_user: Annotated[
        User, Depends(get_current_user)
    ],  # The current authenticated user, fetched from the dependency
    db: Annotated[
        AsyncSession, Depends(get_db)
    ],  # The database session, fetched from the dependency
    task_id: int = Path(Ellipsis),  # Task ID provided as part of the URL path
):
    # Calling the CRUD function to delete the task based on the task ID
    return await crud.delete_task(task_id, current_user, db)
