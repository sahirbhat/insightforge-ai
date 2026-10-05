from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.user.schemas import UserCreate
from app.user.models import User
from config.security import hash_password


async def create_user_service(
    user: UserCreate,
    db: AsyncSession
):
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user.email)
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user

async def get_user_service(
    user_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def get_all_users_service(
    db: AsyncSession
):
    result = await db.execute(
        select(User)
    )

    users = result.scalars().all()

    return users