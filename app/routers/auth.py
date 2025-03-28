from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.database import get_db
from app.routers.schemas import UserIn, UserOut
from app.crud import user_crud as crud

router = APIRouter()
db_dependency: AsyncSession = Depends(get_db)


@router.patch(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: UserIn, db=db_dependency):
    return await crud.create_user(user, db)


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=db_dependency,
):
    user = await crud.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    access_token = crud.create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}
