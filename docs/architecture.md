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

## Security
- JWT bearer authentication.
- Admin-only routes for user management.
- CORS and environment-based configuration.
