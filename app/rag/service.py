import hashlib
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from langsmith import traceable

from app.rag.query_rewriter import rewrite_query
from app.rag.retriever import retrieve_chunks
from app.rag.reranker import rerank_chunks
from app.rag.context import build_context
from app.rag.chain import generate_answer

from config.redis import redis_client


logger = logging.getLogger(__name__)


@traceable(name="RAG Query")
async def rag_query_service(
    question: str,
    db: AsyncSession,
    user_id: int
):

    logger.info(
        "RAG query started | user_id=%s",
        user_id
    )

    # ==================================================
    # Step 1: Create Redis cache key
    # ==================================================

    normalized_question = question.strip().lower()

    question_hash = hashlib.sha256(
        normalized_question.encode()
    ).hexdigest()

    cache_key = f"rag:{user_id}:{question_hash}"

    logger.info(
        "Cache key generated | user_id=%s",
        user_id
    )


    # ==================================================
    # Step 2: Check Redis
    # ==================================================

    cached_response = await redis_client.get(cache_key)

    if cached_response:

        logger.info(
            "Redis cache HIT | user_id=%s",
            user_id
        )

        return json.loads(cached_response)

    logger.info(
        "Redis cache MISS | user_id=%s",
        user_id
    )


    # ==================================================
    # Step 3: Rewrite user's query
    # ==================================================

    rewritten_query = await rewrite_query(question)

    logger.info(
        "Query rewriting completed | user_id=%s",
        user_id
    )


    # ==================================================
    # Step 4: Hybrid Search + RRF
    # ==================================================

    chunks = await retrieve_chunks(
        question=rewritten_query,
        db=db,
        user_id=user_id
    )

    logger.info(
        "Hybrid retrieval completed | user_id=%s | chunks=%s",
        user_id,
        len(chunks)
    )


    # ==================================================
    # Step 5: Stop if nothing was retrieved
    # ==================================================

    if not chunks:

        logger.warning(
            "No relevant chunks found | user_id=%s",
            user_id
        )

        return {
            "question": question,
            "answer": "The information was not found in the document.",
            "sources": []
        }


    # ==================================================
    # Step 6: Cross-Encoder Reranking
    # ==================================================

    chunks = rerank_chunks(
        question=question,
        chunks=chunks
    )

    logger.info(
        "Reranking completed | user_id=%s | chunks=%s",
        user_id,
        len(chunks)
    )


    # ==================================================
    # Step 7: Build Context
    # ==================================================

    context = build_context(chunks)

    logger.info(
        "RAG context built | user_id=%s",
        user_id
    )


    # ==================================================
    # Step 8: Generate final answer
    # ==================================================

    answer = await generate_answer(
        question=question,
        context=context
    )

    logger.info(
        "Answer generation completed | user_id=%s",
        user_id
    )


    # ==================================================
    # Step 9: Build Sources
    # ==================================================

    sources = [
        {
            "filename": chunk.filename,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index
        }
        for chunk in chunks
    ]


    # ==================================================
    # Step 10: Build final response
    # ==================================================

    response = {
        "question": question,
        "answer": answer,
        "sources": sources
    }


    # ==================================================
    # Step 11: Save response to Redis
    # ==================================================

    await redis_client.set(
        cache_key,
        json.dumps(response),
        ex=3600
    )

    logger.info(
        "RAG response saved to Redis | user_id=%s | ttl=%s",
        user_id,
        3600
    )


    # ==================================================
    # Step 12: Return response
    # ==================================================

    logger.info(
        "RAG query completed successfully | user_id=%s",
        user_id
    )

    return response