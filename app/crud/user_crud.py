from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.routers.schemas import UserBase


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    return user


async def create_user(request: UserBase, db: AsyncSession) -> User:
    if await get_user_by_email(request.email, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User creation failed: User with {request.email} already exists",
        )

    inserted_user = await db.scalar(
        insert(User)
        .values(**request.model_dump())
        .returning(User)  # Returning created user (new user)
    )
    await db.commit()

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
