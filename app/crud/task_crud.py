from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, asc, case

from app.db.models import Task, User
from app.routers.schemas import TaskBase, TaskUpdate


async def create_task(request: TaskBase, user: User, db: AsyncSession) -> Task:
    inserted_task = await db.scalar(
        insert(Task)
        .values(**request.model_dump(), user_id=user.id)
        .returning(Task)  # Return inserted row
    )
    await db.commit()

    if not inserted_task:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task creation failed: Invalid input data",
        )

    return inserted_task


async def get_task(task_id: int, user: User, db: AsyncSession) -> Task:
    task = await db.scalar(select(Task).where(Task.id == task_id))

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task selection failed: Task with id {task_id} not found",
        )

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task selection failed: Permission to access this task denied",
        )

    return task


async def get_tasks(user: User, db: AsyncSession) -> Sequence[Task]:
    results = await db.scalars(
        select(Task)
        .where(Task.user_id == user.id)
        .order_by(
            case((Task.is_complete == True, 1), else_=0),
            asc(Task.due_date),  # Order by due_date in ascending order
        )
    )
    tasks = results.all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task selection failed: No tasks found",
        )

    return tasks


async def update_task(
    request: TaskUpdate, task_id: int, user: User, db: AsyncSession
) -> Task:
    await get_task(task_id, user, db)
    result = await db.scalar(
        update(Task)
        .where(Task.id == task_id)
        .values(**request.model_dump(exclude_unset=True))
        .returning(Task),  # Return updated task
    )
    await db.commit()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task update failed: Task not found or not updated",
        )

    return result


async def delete_task(task_id: int, user: User, db: AsyncSession) -> dict:
    await get_task(task_id, user, db)
    result = await db.execute(delete(Task).where(Task.id == task_id))
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task deletion failed: Task with id {task_id} not found",
        )

    return {"status": "ok", "message": "Task deleted successfully"}
