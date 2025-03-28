from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_crud import get_user_by_email
from app.db.models import User
from app.security import Hash

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)

    if not user:
        raise credentials_exception

    if not Hash.verify_password(password, user.password):
        raise credentials_exception

    return user
