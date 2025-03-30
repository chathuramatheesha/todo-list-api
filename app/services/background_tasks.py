from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.tasks_expire_service import tasks_expire_due_date
from app.core.config import config

# Create a scheduler instance for periodic task execution
schedular = AsyncIOScheduler()

# Add the 'tasks_expire_due_date' function to the scheduler to run at regular intervals
# The job will run every minute (IntervalTrigger(1 hour))
schedular.add_job(
    tasks_expire_due_date,  # Function to execute
    IntervalTrigger(hours=config.TASKS_EXPIRE_INTERVAL_HOURS),  # Set interval to 1 hour
    id="expire_task_job",  # Unique job ID for identification
    replace_existing=True,  # Replace any existing job with the same ID
)
