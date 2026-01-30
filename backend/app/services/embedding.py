from __future__ import annotations

import math
import re
from hashlib import blake2b

EMBEDDING_SIZE = 128


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_SIZE
    tokens = _tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        digest = blake2b(token.encode("utf-8"), digest_size=4).hexdigest()
        idx = int(digest, 16) % EMBEDDING_SIZE
        vector[idx] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))
