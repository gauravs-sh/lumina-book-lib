from __future__ import annotations

from collections import Counter

from app.models.book import Book
from app.services.embedding import cosine_similarity, embed_text


def recommend_books(books: list[Book], preferred_genres: list[str] | None = None, limit: int = 5) -> list[Book]:
    if not books:
        return []

    preferred_genres = [genre.lower() for genre in (preferred_genres or [])]

    genre_scores = Counter()
    for book in books:
        genre_scores[book.genre.lower()] += 1

    def score(book: Book) -> float:
        base = genre_scores[book.genre.lower()]
        if preferred_genres and book.genre.lower() in preferred_genres:
            base += 5
        return float(base)

    ranked = sorted(books, key=score, reverse=True)
    return ranked[:limit]


def recommend_similar_books(target: Book, books: list[Book], limit: int = 5) -> list[Book]:
    target_vector = embed_text(target.summary or target.title)
    scored = []
    for book in books:
        if book.id == target.id:
            continue
        score = cosine_similarity(target_vector, embed_text(book.summary or book.title))
        scored.append((score, book))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [book for _, book in scored[:limit]]
