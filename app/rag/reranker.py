from sentence_transformers import CrossEncoder

from app.ingestion.model import DocumentChunk


reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_chunks(
    question: str,
    chunks: list[DocumentChunk]
):
    # Step 1: If RRF returned nothing, return empty list
    if not chunks:
        return []

    # Step 2: Create question + chunk pairs
    pairs = [
        [question, chunk.content]
        for chunk in chunks
    ]

    # Step 3: Cross-Encoder gives relevance score to every pair
    scores = reranker_model.predict(pairs)

    # Combine each chunk with its reranker score
    scored_chunks = list(zip(chunks, scores))

    # Sort by score: highest score first
    scored_chunks.sort(
        key=lambda item: item[1],
        reverse=True
    )

    print("\n========== RERANKER RESULTS ==========")

    for chunk, score in scored_chunks:
        print(
            f"Chunk ID: {chunk.id} | "
            f"Reranker Score: {score}"
        )

    # Return chunks only, in the new reranked order
    reranked_chunks = [
        chunk
        for chunk, score in scored_chunks
    ]

    return reranked_chunks