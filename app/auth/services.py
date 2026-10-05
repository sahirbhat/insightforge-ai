from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User
from config.security import verify_password, create_access_token, create_refresh_token


async def user_login_service(
    username: str,
    password: str,
    db: AsyncSession
):

    result = await db.execute(
        select(User).where(User.email == username)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        password,
        user.hashed_password 
        
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email
    }

    access_token = create_access_token(
        data=token_data
    )

    refresh_token = create_refresh_token(
        data=token_data
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }






