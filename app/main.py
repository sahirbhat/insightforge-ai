from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
import uvicorn

from app.user.router import router as user_router
from app.auth.routers import router as auth_router
from app.ingestion.router import router as ingestion_router
from app.rag.router import router as rag_router
from app.database.sessions import engine, Base

import logging


from config.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)




@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:

        # Enable pgvector extension
        await conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        # Create database tables
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(
    title="InsightForge AI",
    lifespan=lifespan,
    description="An AI-powered platform for generating deep insights and analytics"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(rag_router)


@app.get("/")
def root():
    return {
        "message": "InsightForge AI is running"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )