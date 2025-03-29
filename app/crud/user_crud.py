from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, ExpiredSignatureError, JWTError
from datetime import datetime, timezone, timedelta
from typing import Annotated

from app.db.database import get_db
from app.db.models import User
from app.routers.schemas import UserIn
from app.security import Hash
from app.config import config

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    return user


async def create_user(request: UserIn, db: AsyncSession) -> User:
    if await get_user_by_email(request.email, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User creation failed: User with {request.email} already exists",
        )

    new_user = {
        **request.model_dump(),
        "password": Hash.get_hash_password(request.password),
    }

    await db.execute(
        insert(User).values(new_user)
    )  # .returning(User)) # returning works on (sqlite, postgresql)
    await db.commit()

    inserted_user = await get_user_by_email(request.email, db)

    if not inserted_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User creation failed: Please ensure all required fields are provided",
        )

    return inserted_user


async def get_user(email: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User selection failed: User not found",
        )

    return user


def access_token_expire_minutes() -> int:
    return config.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=access_token_expire_minutes()
    )

    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(
        jwt_data,
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )

    return encoded_jwt


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)

    if not user:
        raise credentials_exception

    if not Hash.verify_password(password, user.password):
        raise credentials_exception

    return user


async def get_current_user(
    token: Annotated[str, Depends(oath2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        email = payload.get("sub")

        if not email:
            raise credentials_exception

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except JWTError as e:
        raise credentials_exception from e

    user = await get_user_by_email(email, db)

    if not user:
        raise credentials_exception

    return user
