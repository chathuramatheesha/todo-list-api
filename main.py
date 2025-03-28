from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.database import init_db
from routers import task


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await init_db()
    yield
    print("App is shutting dow...")


app = FastAPI(lifespan=lifespan)

app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
