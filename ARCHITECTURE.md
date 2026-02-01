# LuminaLib Architecture

## Overview
LuminaLib uses a layered, interface-driven architecture:

- **API Layer**: FastAPI routers with dependency injection.
- **Service Layer**: LLM, storage, recommendations, review analysis.
- **Data Layer**: SQLAlchemy models with async sessions.
- **Frontend**: Next.js (SSR-ready) with a typed service layer and reusable components.

## Storage Abstraction
Storage is abstracted behind `StorageProvider` in [backend/app/services/storage.py](backend/app/services/storage.py). The provider is selected via configuration:

- `STORAGE_PROVIDER=local` → `LocalStorage`
- `STORAGE_PROVIDER=s3` → `S3Storage`

Switching providers only requires environment changes.

## LLM Abstraction
LLM access is abstracted behind `LLMProvider` in [backend/app/services/llm.py](backend/app/services/llm.py). Providers:

- `LLM_PROVIDER=mock` → `MockLLM`
- `LLM_PROVIDER=openrouter` → OpenRouter
- `LLM_PROVIDER=http` → Any OpenAI-compatible HTTP endpoint

All prompts are deterministic, scoped, and reusable across features.

## Async Strategy
- Book summaries and review consensus run in background tasks.
- File IO uses `asyncio.to_thread` for non-blocking local disk operations.
- LLM calls use `httpx.AsyncClient`.

## User Preferences Schema
User preferences are stored in `user_preferences` with a JSON payload:

```
{
  "genres": ["Mystery", "Sci-Fi"],
  "authors": ["Ursula Le Guin"],
  "keywords": ["time travel", "ethics"]
}
```

This enables flexible ranking in the recommendation engine and can be extended without migrations.

## Recommendation Strategy
The recommendation engine combines:
- **Content-based scoring** from user preferences (genres/authors/keywords).
- **Similarity-based ranking** as a fallback using embeddings.

This balances deterministic preferences with semantic similarity.

## Frontend Design Choices
- **Next.js** for SSR and routing.
- **Typed API layer** in [frontend/lib/api.ts](frontend/lib/api.ts) to avoid direct fetch usage in components.
- **Reusable components** (header, forms) for clean composition.
- **Jest + RTL** for critical UI tests in [frontend/__tests__](frontend/__tests__).

## Extensibility
All providers can be swapped with config-only changes. The API layer is thin and delegates to services, enabling new storage or LLM implementations without touching endpoints.
