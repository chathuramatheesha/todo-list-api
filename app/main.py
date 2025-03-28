from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import init_db
from app.routers import task


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await init_db()
    yield
    print("App is shutting dow...")


app = FastAPI(lifespan=lifespan)

app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
