# Architecture

## Overview
LuminaLib uses a modular, layered architecture:
- **API layer**: FastAPI routers (auth, users, books, reviews, recommendations).
- **Service layer**: LLM, storage, review analysis, recommendations.
- **Data layer**: SQLAlchemy ORM with async sessions, PostgreSQL database.
- **Frontend**: Next.js (SSR) with a typed API service layer.

## Data Flow
1. User signs up/logs in and receives a JWT.
2. User uploads a book file; storage is abstracted (local/S3).
3. Background tasks generate AI summaries and review consensus.
4. Recommendations are computed from user preferences.

## Scalability
- Stateless API server; scale horizontally behind a load balancer.
- Use AWS RDS for PostgreSQL and S3 for storage.
- Consider a queue (SQS) for background tasks.

## Recommendation Model
- Optional TF-IDF model using scikit-learn. Train via `POST /recommendations/train`.
- Model artifacts stored in `storage/` and used for similarity-based recommendations.

## User Preferences Schema Rationale
- **Single-row per user**: `user_preferences.user_id` is unique, enforcing a one-to-one relationship with `users` and keeping preference lookup simple and fast.
- **Flexible structure**: JSON storage supports evolving preference shapes (genres, authors, weights) without migrations for every new field.
- **Fast personalization**: preferences are read once per recommendation request and passed directly into the recommender service.

## Async LLM Generation
- **Async HTTP**: LLM calls are made using async clients so request handling remains non-blocking under load.
- **Timeouts and fallback**: requests are bounded and can fall back to mock/provider selection via configuration, keeping the API responsive.
- **Isolation from core API**: LLM access is abstracted behind a provider interface, letting us swap providers without changing route logic.

## Recommendation Strategy
- **Hybrid approach**: if a trained TF-IDF model exists, use similarity from the model; otherwise fall back to lightweight in-memory similarity and preference-based ranking.
- **Admin-controlled training**: model artifacts are generated on demand via `POST /api/v1/recommendations/train`.
- **Deterministic output**: book ordering is based on similarity scores and capped by `limit` for predictable responses.

## Frontend Design Choices
- **State management**: minimal global state via React context providers for auth and toasts; server-driven data is fetched per page to avoid stale client caches.
- **Styling**: global styles are centralized in `styles/globals.css`, keeping typography and layout consistent and easy to maintain.
- **SSR-friendly structure**: Next.js routing and layout keep critical pages fast while preserving a typed API layer for requests.

## Security
- JWT bearer authentication.
- Admin-only routes for user management.
- CORS and environment-based configuration.
