from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, asc, case, desc
from typing import Sequence
from datetime import datetime, timezone

from app.db.models import Task, User
from app.core.enums import TaskPriority, TaskSortBy, TaskOrder
from app.routers.schemas import TaskBase, TaskUpdate


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


async def get_tasks(
    search: str,
    filter_status: bool,
    filter_priority: TaskPriority,
    sort_by: TaskSortBy,
    order: TaskOrder,
    user: User,
    db: AsyncSession,
) -> Sequence[Task]:
    query = select(Task).where(Task.user_id == user.id)
    order_func = desc if order == TaskOrder.desc else asc

    if search:
        query = query.filter(
            (Task.title.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%"))
        )

    if filter_status is not None:
        query = query.filter(Task.is_complete == filter_status)

    if filter_priority:
        query = query.filter(Task.priority == filter_priority.value)

    if sort_by:
        match sort_by:
            case TaskSortBy.status:
                query = query.order_by(case((Task.is_complete == True, 1), else_=0))

            case TaskSortBy.priority:
                query = query.order_by(
                    case(
                        (Task.priority == TaskPriority.low.value, 0),
                        (Task.priority == TaskPriority.medium.value, 1),
                        (Task.priority == TaskPriority.high.value, 2),
                        else_=3,
                    )
                )

            case _:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Tasks sorting failed: accepted values are {', '.join(TaskSortBy)}",
                )

    query = query.order_by(
        order_func(
            getattr(Task, "is_complete" if sort_by == TaskSortBy.status else sort_by)
            if sort_by
            else Task.due_date
        )
    )

    tasks = await db.scalars(query)
    tasks = tasks.all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task selection failed: No tasks found",
        )

    return tasks


async def create_task(request: TaskBase, user: User, db: AsyncSession) -> Task:
    result = await db.execute(
        insert(Task).values(**request.model_dump(), user_id=user.id)
        # .returning(Task)  # Return inserted row
    )
    await db.commit()

    inserted_task = await get_task(result.inserted_primary_key[0], user, db)

    if not inserted_task:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task creation failed: Invalid input data",
        )

    return inserted_task


async def update_task(
    request: TaskUpdate, task_id: int, user: User, db: AsyncSession
) -> Task:
    await get_task(task_id, user, db)
    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(**request.model_dump(exclude_unset=True))
        # .returning(Task),  # Return updated task
    )
    await db.commit()

    result = await get_task(task_id, user, db)

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
