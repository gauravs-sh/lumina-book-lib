# Architecture

## Overview
The system uses a modular, layered architecture:
- **API layer**: FastAPI routers (auth, users, books, reviews, documents, ingestion, QA, recommendations).
- **Service layer**: Embeddings, summarization, ingestion, recommendations, and RAG selection.
- **Data layer**: SQLAlchemy ORM with async sessions, PostgreSQL database.
- **Frontend**: React + Vite SPA using a lightweight API client.

## Data Flow
1. User logs in via HTTP Basic and receives a JWT.
2. Authenticated users upload documents and create books.
3. Ingestion splits documents into chunks, generates embeddings, and stores them.
4. Q&A uses vector similarity to retrieve relevant chunks and generates an answer.

## Scalability
- Stateless API server; scale horizontally behind a load balancer.
- Use AWS RDS for PostgreSQL, ElastiCache for recommendation caching, and S3 for document storage.
- Consider a queue (SQS) for ingestion tasks.

## Recommendation Model
- Optional TF-IDF model using scikit-learn. Train via `POST /recommendations/train`.
- Model artifacts stored in `storage/` and used for similarity-based recommendations.

## Security
- JWT bearer authentication.
- Admin-only routes for user management.
- CORS and environment-based configuration.
