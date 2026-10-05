from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.embeddings import embedding_model
from app.ingestion.model import Document, DocumentChunk


async def retrieve_chunks(
    question: str,
    db: AsyncSession,
    user_id: int
):
    """
    Hybrid Search:
    1. Vector search
    2. Keyword search
    3. RRF fusion
    4. Return top 5 chunks
    """

    # ==================================================
    # 1. VECTOR SEARCH
    # ==================================================

    query_embedding = embedding_model.embed_query(question)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    vector_result = await db.execute(
        select(
            DocumentChunk,
            distance.label("distance")
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id
        )
        .where(
            Document.user_id == user_id,
            distance <= 0.65
        )
        .order_by(distance)
        .limit(5)
    )

    vector_results = vector_result.all()

    vector_chunks = [
        chunk
        for chunk, score in vector_results
    ]

    print("\n========== VECTOR SEARCH ==========")

    for chunk, score in vector_results:
        print(
            f"Chunk ID: {chunk.id} | "
            f"Distance: {score} | "
            f"Text: {chunk.content[:100]}"
        )

    # ==================================================
    # 2. KEYWORD SEARCH
    # ==================================================

  

    search_vector = func.to_tsvector(
        "english",
        DocumentChunk.content
    )

    search_query = func.plainto_tsquery(
        "english",
        question
    )

    # Calculate keyword relevance score
    keyword_rank = func.ts_rank(
        search_vector,
        search_query
    )

    keyword_result = await db.execute(
        select(
            DocumentChunk,
            keyword_rank.label("keyword_rank")
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id
        )
        .where(
            Document.user_id == user_id,
            search_vector.op("@@")(search_query)
        )
        .order_by(keyword_rank.desc())
        .limit(5)
    )

    keyword_results = keyword_result.all()

    keyword_chunks = [
        chunk
        for chunk, score in keyword_results
    ]


    print("\n========== KEYWORD SEARCH ==========")

    for chunk, score in keyword_results:
        print(
            f"Chunk ID: {chunk.id} | "
            f"Keyword Rank: {score} | "
            f"Text: {chunk.content[:100]}"
        )
    # ==================================================
    # 3. RRF - RECIPROCAL RANK FUSION
    # ==================================================

    rrf_scores = {}
    chunk_map = {}

    k = 60

    # Add vector ranking scores
    for rank, chunk in enumerate(vector_chunks, start=1):

        rrf_scores[chunk.id] = (
            rrf_scores.get(chunk.id, 0)
            + 1 / (k + rank)
        )

        chunk_map[chunk.id] = chunk

    # Add keyword ranking scores
    for rank, chunk in enumerate(keyword_chunks, start=1):

        rrf_scores[chunk.id] = (
            rrf_scores.get(chunk.id, 0)
            + 1 / (k + rank)
        )

        chunk_map[chunk.id] = chunk

    # ==================================================
    # 4. SORT BY RRF SCORE
    # ==================================================

    ranked_chunk_ids = sorted(
        rrf_scores,
        key=lambda chunk_id: rrf_scores[chunk_id],
        reverse=True
    )

    # ==================================================
    # 5. RETURN TOP 5
    # ==================================================

    chunks = [
        chunk_map[chunk_id]
        for chunk_id in ranked_chunk_ids[:5]
    ]

    print("\n========== RRF FINAL RANKING ==========")

    for chunk_id in ranked_chunk_ids[:5]:
        print(
            f"Chunk ID: {chunk_id} | "
            f"RRF Score: {rrf_scores[chunk_id]}"
        )

    return chunks