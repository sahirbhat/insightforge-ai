from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.schemas import UserCreate, userResponse
from app.user.models import User
from app.database.sessions import get_db
from app.user.service import (
    create_user_service,
    get_user_service,
    get_all_users_service,
)
from app.auth.dependencies import get_current_user
from config.rate_limmiter import rate_limiter


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=userResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(rate_limiter(limit=3, window=60))
    ]
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_user_service(user, db)


@router.get(
    "/{user_id}",
    response_model=userResponse,
    dependencies=[
        Depends(rate_limiter(limit=10, window=60))
    ]
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_service(user_id, db)


@router.get(
    "/",
    response_model=list[userResponse],
    dependencies=[
        Depends(rate_limiter(limit=5, window=60))
    ]
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_all_users_service(db)