from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.crud import user_crud as crud
from app.db.database import get_db
from app.db.models import User
from app.security import Hash, credentials_exception, get_decode_jwt_token

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    user = await crud.get_user_by_email(email, db)

    if not user:
        raise credentials_exception

    if not Hash.verify_password(password, user.password):
        raise credentials_exception

    return user


async def get_current_user(
    token: Annotated[str, Depends(oath2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    data = get_decode_jwt_token(token)
    email = data.get("email")

    if not email:
        raise credentials_exception

    user = await crud.get_user_by_email(email, db)

    if not user:
        raise credentials_exception

    return user
