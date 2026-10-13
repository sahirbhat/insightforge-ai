from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.sessions import get_db
from app.ingestion.service import (
    process_document,
    get_documents_service,
    delete_document_service
)
from app.auth.dependencies import get_current_user
from app.user.models import User


router = APIRouter(prefix="/documents",tags=["Documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...),db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    return await process_document(
        file=file,
        db=db,
        user_id=current_user.id  # type: ignore
    )


@router.get("/")
async def get_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_documents_service(
        db=db,
        user_id=current_user.id  # type: ignore
    )




@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await delete_document_service(
        document_id=document_id,
        db=db,
        user_id=current_user.id  # type: ignore
    )