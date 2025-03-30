from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.services.background_tasks import schedular
from app.db.database import init_db
from app.routers import task, auth


# Async context manager to manage the lifespan of the FastAPI application
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await init_db()  # Initialize the database connection on startup
    schedular.start()
    yield  # Continue with the app's normal lifecycle
    print("App is shutting down...")  # Print a message when the app is shutting down


# FastAPI app instance with custom lifespan management
app = FastAPI(lifespan=lifespan)  # Assign the custom lifespan to the app

# Include routers for user authentication and task management
# Register the auth router with the "User" tag
app.include_router(auth.router, tags=["User"])
# Register the task router with the "Task" tag and a "/tasks" prefix
app.include_router(task.router, prefix="/tasks", tags=["Task"])


# TODO - due date reminder
