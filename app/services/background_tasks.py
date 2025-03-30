from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.database import AsyncSessionLocal
from app.db.models import Task
from app.core.enums import TaskStatus


# Function to expire tasks
async def tasks_expire_due_date():
    async with AsyncSessionLocal() as db:
        # Get the current time
        now = datetime.now(timezone.utc)

        # Query for tasks whose due_date has passed and aren't expired yet
        query = select(Task).where(
            Task.due_date < now, Task.status != TaskStatus.expired
        )

        # Execute the query and fetch tasks that need to be expired
        result = await db.scalars(query)
        tasks_to_expire = result.all()

        if not tasks_to_expire:
            return

        # Loop through tasks and update the status to expired
        for task in tasks_to_expire:
            task.status = TaskStatus.expired

        # Commit changes to the database
        await db.commit()


schedular = AsyncIOScheduler()

schedular.add_job(
    tasks_expire_due_date,
    IntervalTrigger(minutes=1),
    id="expire_task_job",
    replace_existing=True,
)
