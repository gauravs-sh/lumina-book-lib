from __future__ import annotations

from app.models.document_chunk import DocumentChunk
from app.services.embedding import cosine_similarity, embed_text


def select_relevant_chunks(question: str, chunks: list[DocumentChunk], limit: int = 4) -> list[DocumentChunk]:
    query_vector = embed_text(question)
    scored = [(cosine_similarity(query_vector, chunk.embedding), chunk) for chunk in chunks]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:limit]]
