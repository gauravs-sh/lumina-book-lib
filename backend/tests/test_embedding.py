from app.services.embedding import cosine_similarity, embed_text


def test_embed_text_returns_vector():
    vector = embed_text("Hello world")
    assert len(vector) == 128


def test_cosine_similarity():
    a = embed_text("test")
    b = embed_text("test")
    assert cosine_similarity(a, b) > 0.9
