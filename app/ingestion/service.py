import hashlib

from fastapi import UploadFile, HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ingestion.loaders import load_pdf
from app.ingestion.model import Document, DocumentChunk
from .embeddings import embedding_model


async def process_document(
    file: UploadFile,
    db: AsyncSession,
    user_id: int
):

    # Step 0: Validate file
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported"
        )

    # Step 1: Read PDF bytes
    content = await file.read()

    # Step 2: Generate SHA-256 hash
    file_hash = hashlib.sha256(content).hexdigest()

    # Step 3: Reset file pointer
    # load_pdf() needs to read the file again
    await file.seek(0)

    # Step 4: Check if same document already exists
    # for the current user
    result = await db.execute(
        select(Document).where(
            Document.user_id == user_id,
            Document.file_hash == file_hash
        )
    )

    existing_document = result.scalars().first()

    if existing_document:
        raise HTTPException(
            status_code=409,
            detail="Document already uploaded"
        )

    # Step 5: Load PDF
    documents = await load_pdf(file)

    # Step 6: Split PDF into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    # Step 7: Add metadata
    for index, chunk in enumerate(chunks):
        chunk.metadata["filename"] = file.filename
        chunk.metadata["chunk_index"] = index

    # Step 8: Extract text from chunks
    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    # Step 9: Generate embeddings
    embeddings = embedding_model.embed_documents(texts)

    # Step 10: Create parent Document
    document = Document(
        user_id=user_id,
        filename=file.filename,
        file_hash=file_hash
    )

    db.add(document)

    # Get document.id before commit
    await db.flush()

    # Step 11: Create DocumentChunk objects
    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        document_chunk = DocumentChunk(
            document_id=document.id,
            filename=file.filename,
            page_number=chunk.metadata.get("page"),
            chunk_index=index,
            content=chunk.page_content,
            embedding=embedding
        )

        db.add(document_chunk)

    # Step 12: Store Document + chunks
    await db.commit()

    return {
        "document_id": document.id,
        "filename": file.filename,
        "pages": len(documents),
        "chunks": len(chunks),
        "embeddings_created": len(embeddings),
        "embeddings_stored": len(embeddings),
        "embedding_dimension": (
            len(embeddings[0])
            if embeddings
            else 0
        )
    }


async def get_documents_service(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(Document).where(
            Document.user_id == user_id
        )
    )

    documents = result.scalars().all()

    return documents



async def delete_document_service(
    document_id: int,
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id
        )
    )

    document = result.scalars().first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    await db.delete(document)

    await db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }