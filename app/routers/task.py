from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import task_crud as crud
from app.db.database import get_db
from app.db.models import User
from app.routers.schemas import TaskBase, TaskOut, TaskUpdate
from app.crud.user_crud import get_current_user

router = APIRouter()

# db_dependency: AsyncSession =
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
):
    return await crud.get_tasks(current_user, db)


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
