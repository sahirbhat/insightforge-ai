from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.sessions import get_db
from app.rag.service import rag_query_service
from app.auth.dependencies import get_current_user
from app.user.models import User


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)




@router.get("/query")
async def query_rag(
    question: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await rag_query_service(
        question=question,
        db=db,
        user_id=current_user.id
    )