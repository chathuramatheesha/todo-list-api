from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import init_db
from app.routers import task, auth


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await init_db()
    yield
    print("App is shutting dow...")


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, tags=["User"])
app.include_router(task.router, prefix="/tasks", tags=["Task"])
