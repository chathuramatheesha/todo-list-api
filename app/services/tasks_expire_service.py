from sqlalchemy import select
from datetime import timezone, datetime

from app.db.database import AsyncSessionLocal
from app.db.models import Task
from app.core.enums import TaskStatus


# Function to expire tasks whose due date has passed
async def tasks_expire_due_date():
    # Use AsyncSessionLocal to interact with the database asynchronously
    async with AsyncSessionLocal() as db:
        # Get the current UTC time
        now = datetime.now(timezone.utc)

        # Query for tasks whose due_date has passed and are not already marked as expired
        query = select(Task).where(
            Task.due_date < now, Task.status != TaskStatus.expired
        )

        # Execute the query and fetch tasks that need to be expired
        result = await db.scalars(query)
        tasks_to_expire = result.all()

        # If no tasks are found that need to expire, return early
        if not tasks_to_expire:
            return

        # Loop through the tasks that need to be expired and update their status
        for task in tasks_to_expire:
            task.status = TaskStatus.expired  # Set the task's status to expired

        # Commit the changes to the database, updating the status of the tasks
        await db.commit()
