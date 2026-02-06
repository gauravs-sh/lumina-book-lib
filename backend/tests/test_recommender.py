from app.models.book import Book
from app.services.recommender import recommend_books


def test_recommend_books_prefers_genre():
    books = [
        Book(id=1, title="A", author="X", genre="Sci-Fi", year_published=2020),
        Book(id=2, title="B", author="X", genre="Drama", year_published=2021),
    ]
    result = recommend_books(books, preferences={"genres": ["Drama"]}, limit=1)
    assert result[0].genre == "Drama"
