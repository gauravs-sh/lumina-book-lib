from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.models.book import Book

try:
    from joblib import dump, load
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    SKLEARN_AVAILABLE = False

MODEL_PATH = Path(settings.storage_path) / "recommender.joblib"
VECTORIZER_PATH = Path(settings.storage_path) / "recommender_vectorizer.joblib"


def _ensure_storage() -> None:
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)


def train_recommender(books: list[Book]) -> dict[str, str]:
    if not SKLEARN_AVAILABLE:
        return {"status": "skipped", "detail": "scikit-learn not installed"}

    _ensure_storage()
    corpus = [book.summary or book.title for book in books]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(corpus)

    dump(vectors, MODEL_PATH)
    dump(vectorizer, VECTORIZER_PATH)

    mapping = {str(book.id): idx for idx, book in enumerate(books)}
    (Path(settings.storage_path) / "recommender_mapping.json").write_text(json.dumps(mapping))
    return {"status": "trained", "documents": str(len(books))}


def recommend_from_model(target: Book, books: list[Book], limit: int = 5) -> list[Book]:
    if not SKLEARN_AVAILABLE:
        return []
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        return []

    mapping_path = Path(settings.storage_path) / "recommender_mapping.json"
    if not mapping_path.exists():
        return []

    mapping = json.loads(mapping_path.read_text())
    if str(target.id) not in mapping:
        return []

    vectors = load(MODEL_PATH)
    vectorizer = load(VECTORIZER_PATH)
    target_vector = vectorizer.transform([target.summary or target.title])
    similarities = cosine_similarity(target_vector, vectors).flatten()

    ranked = sorted(enumerate(similarities), key=lambda item: item[1], reverse=True)
    reverse_mapping = {idx: book_id for book_id, idx in mapping.items()}

    results = []
    for idx, _score in ranked:
        book_id = int(reverse_mapping.get(idx, -1))
        if book_id == target.id:
            continue
        book = next((b for b in books if b.id == book_id), None)
        if book:
            results.append(book)
        if len(results) >= limit:
            break

    return results
