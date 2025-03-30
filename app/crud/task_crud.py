from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, asc, case, desc, func

from app.db.models import Task, User
from app.core.enums import TaskPriority, TaskSortBy, TaskOrder, TaskStatus
from app.routers.schemas import (
    TaskBase,
    TaskUpdate,
    PaginationBase,
    TaskOut,
    TaskListOut,
)


# * GET A TASK by task.id
# Define an asynchronous function to get a specific task by its ID
async def get_task(task_id: int, user: User, db: AsyncSession) -> Task:
    # Query the database for a task that matches the given task_id
    task = await db.scalar(select(Task).where(Task.id == task_id))

    # Check if the task was found in the database
    if not task:
        # If task not found, raise a 404 HTTP exception with a custom error message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task selection failed: Task with id {task_id} not found",
        )

    # Ensure the task belongs to the requesting user by comparing user_id
    if task.user_id != user.id:
        # If the task doesn't belong to the user, raise a 403 HTTP exception (Permission Denied)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task selection failed: Permission to access this task denied",
        )

    # Return the task if it passes the above checks
    return task


# * GET TASKS (search, filter, sort, order)
# Define an asynchronous function to retrieve tasks with filters and sorting options
async def get_tasks(
    search: str,  # Search term to filter tasks by title or description
    filter_status: TaskStatus,  # Filter tasks by status (e.g., pending, completed)
    filter_priority: TaskPriority,  # Filter tasks by priority (e.g., low, medium, high)
    sort_by: TaskSortBy,  # Sorting field (e.g., by status, priority)
    order: TaskOrder,  # Sorting order (ascending or descending)
    user: User,  # User object to filter tasks by the requesting user's ID
    db: AsyncSession,  # Database session for querying tasks
    page_number: int = 1,  # Page number for pagination (default to 1)
    page_size: int = 10,  # Page size for pagination (default to 10)
) -> TaskListOut:
    # Initialize the query, selecting tasks where the user_id matches the requesting user's ID
    query = select(Task).where(Task.user_id == user.id)

    # Define the order function (asc or desc) based on the passed order parameter
    order_func = desc if order == TaskOrder.desc else asc

    # List to hold fields for sorting
    sort_fields = []

    # If a search term is provided, filter tasks by title or description
    if search:
        query = query.filter(
            (Task.title.ilike(f"%{search}%")) | (Task.description.ilike(f"%{search}%"))
        )

    # If a specific status filter is provided, filter tasks by status
    if filter_status:
        query = query.filter(Task.status == filter_status)

    # If a specific priority filter is provided, filter tasks by priority
    if filter_priority:
        query = query.filter(Task.priority == filter_priority)

    # If sorting is required, determine the sorting field and append it to the sort_fields list
    if sort_by:
        match sort_by:
            case TaskSortBy.status:
                # Sort tasks by status (pending, expired, completed)
                sort_fields.append(
                    case(
                        (Task.status == TaskStatus.pending, 0),
                        (Task.status == TaskStatus.expired, 1),
                        (Task.status == TaskStatus.completed, 2),
                        else_=3,
                    )
                )

            case TaskSortBy.priority:
                # Sort tasks by priority (low, medium, high)
                sort_fields.append(
                    case(
                        (Task.priority == TaskPriority.low, 0),
                        (Task.priority == TaskPriority.medium, 1),
                        (Task.priority == TaskPriority.high, 2),
                        else_=3,
                    )
                )

            case _:
                # Sort tasks by the chosen field in the sort_by parameter
                sort_fields.append(getattr(Task, sort_by.value))
    else:
        # If no sorting field is specified, default to sorting by due date
        sort_fields.append(Task.due_date)

    # Apply the sorting to the query, passing multiple fields if necessary
    query = query.order_by(order_func(*sort_fields))

    # Calculate the offset based on the page_number and page_size
    # The offset determines how many tasks to skip before returning the results
    # For example, if page_number = 2 and page_size = 10, the offset will be (2-1) * 10 = 10
    offset = (page_number - 1) * page_size

    # Apply the offset and limit to the query
    # The offset skips the specified number of tasks, and the limit restricts the number of tasks returned
    query = query.offset(offset).limit(page_size)

    # Execute the query and fetch the results
    result = await db.scalars(query)
    tasks = result.all()

    # If no tasks are found, raise a 404 HTTP exception with a custom error message
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task selection failed: No tasks found",
        )

    # Count the total number of tasks for pagination
    total_tasks_query = select(func.count(Task.id)).where(Task.user_id == user.id)
    total_tasks = await db.scalar(total_tasks_query)

    # Calculate total pages
    total_pages = (total_tasks // page_size) + (1 if total_tasks % page_size > 0 else 0)

    # Convert ORM objects to Pydantic models using the dictionary unpacking method
    task_out_list = [TaskOut(**task.__dict__) for task in tasks]

    # Return the tasks along with the pagination info
    return TaskListOut(
        page_number=page_number,
        page_size=page_size,
        total_items=total_tasks,
        total_pages=total_pages,
        tasks=task_out_list,
    )


# * CREATE A TASK
# Define an asynchronous function to create a new task for a user
async def create_task(request: TaskBase, user: User, db: AsyncSession) -> Task:
    # Execute the insert statement to add the new task to the database
    result = await db.execute(
        insert(Task).values(**request.model_dump(), user_id=user.id)
        # .returning(Task)  # Optionally, you can return the inserted row if needed
    )

    # Commit the transaction to save the task in the database
    await db.commit()

    # Retrieve the inserted task using the task ID from the result
    inserted_task = await get_task(result.inserted_primary_key[0], user, db)

    # If the task could not be retrieved or inserted correctly, raise an error
    if not inserted_task:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task creation failed: Invalid input data",
        )

    # Return the inserted task
    return inserted_task


# * UPDATE A TASK by task.id
# Define an asynchronous function to update an existing task
async def update_task(
    request: TaskUpdate, task_id: int, user: User, db: AsyncSession
) -> Task:
    # First, ensure the task exists and belongs to the user
    await get_task(task_id, user, db)

    # Execute the update query on the Task table where the task ID matches the provided task_id
    # Use the data from the request, excluding unset fields (so only updated fields are included)
    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(**request.model_dump(exclude_unset=True))
        # .returning(Task),  # Optionally, return the updated task if needed
    )

    # Commit the changes to the database
    await db.commit()

    # Retrieve the updated task to confirm the update
    result = await get_task(task_id, user, db)

    # If the result is not found or the task wasn't updated, raise an error
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task update failed: Task not found or not updated",
        )

    # Return the updated task
    return result


# * DELETE A TASK by task.id
# Define an asynchronous function to delete a task
async def delete_task(task_id: int, user: User, db: AsyncSession) -> dict:
    # First, ensure the task exists and belongs to the user
    await get_task(task_id, user, db)

    # Execute the delete query on the Task table where the task ID matches the provided task_id
    result = await db.execute(delete(Task).where(Task.id == task_id))

    # Commit the transaction to make the changes persistent in the database
    await db.commit()

    # If no rows were affected (meaning no task was deleted), raise a 404 error
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task deletion failed: Task with id {task_id} not found",
        )

    # Return a success message if the task was successfully deleted
    return {"status": "ok", "message": "Task deleted successfully"}
