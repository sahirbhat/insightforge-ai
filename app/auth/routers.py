from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.sessions import get_db
from app.auth.schemas import loginResponse,RefreshTokenRequest,RefreshTokenResponse

from app.auth.services import  user_login_service,create_access_token,create_refresh_token
from config.security import refresh_access_token_service
from config.rate_limmiter import rate_limiter



router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=loginResponse,   dependencies=[
        Depends(rate_limiter(limit=3, window=60))
    ])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await user_login_service(form_data.username,form_data.password, db)



from app.auth.schemas import RefreshTokenRequest


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    dependencies=[
        Depends(rate_limiter(limit=3, window=60))
    ]
)
async def refresh_token(
    request: RefreshTokenRequest
):
    return await refresh_access_token_service(
        request.refresh_token
    )

