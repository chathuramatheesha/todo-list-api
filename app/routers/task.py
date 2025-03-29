from fastapi import APIRouter, Depends, status
from fastapi.params import Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.crud import task_crud as crud
from app.db.database import get_db
from app.db.models import User
from app.core.enums import TaskPriority, TaskSortBy, TaskOrder
from app.routers.schemas import TaskBase, TaskOut, TaskUpdate
from app.crud.user_crud import get_current_user

router = APIRouter()

# db_dependency: Annotated[AsyncSession, Depends(get_db)]
# user_dependency: Annotated[User, Depends(get_current_user)]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskBase,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_task(request, current_user, db)


@router.get("", response_model=list[TaskOut])
async def get_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(
        None,
        description="Search for tasks by matching keywords in the title or description.",
    ),
    filter_status: bool | None = Query(
        None,
        description="Filter by status (true, false)",
    ),
    filter_priority: TaskPriority | None = Query(
        None,
        description=f"Filter by priority ({', '.join(TaskPriority)})",
    ),
    sort_by: TaskSortBy | None = Query(
        None,
        description=f"Sort by ({', '.join(TaskSortBy)})",
    ),
    order: TaskOrder | None = Query(
        None,
        description="Order by (asc, desc)",
    ),
):
    return await crud.get_tasks(
        search=search,
        filter_status=filter_status,
        filter_priority=filter_priority,
        sort_by=sort_by,
        order=order,
        user=current_user,
        db=db,
    )


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    task_id: int = Path(Ellipsis),
):
    return await crud.get_task(task_id, current_user, db)


@router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task(
    request: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    task_id: int = Path(Ellipsis),
):
    return await crud.update_task(request, task_id, current_user, db)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    task_id: int = Path(Ellipsis),
):
    return await crud.delete_task(task_id, current_user, db)
