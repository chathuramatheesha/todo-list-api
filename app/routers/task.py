from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.db.database import get_db
from app.routers.schemas import TaskBase, TaskOut, TaskUpdate

router = APIRouter()
db_dependency = Depends(get_db)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskBase, db: AsyncSession = db_dependency):
    return await crud.create_task(request, db)


@router.get("", response_model=list[TaskOut])
async def get_tasks(db: AsyncSession = db_dependency):
    return await crud.get_tasks(db)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(db: AsyncSession = db_dependency, task_id: int = Path(Ellipsis)):
    return await crud.get_task(task_id, db)


@router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task(
    request: TaskUpdate,
    db: AsyncSession = db_dependency,
    task_id: int = Path(Ellipsis),
):
    return await crud.update_task(request, task_id, db)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(db: AsyncSession = db_dependency, task_id: int = Path(Ellipsis)):
    return await crud.delete_task(task_id, db)
