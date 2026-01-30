# Backend (FastAPI)

## Overview
Async FastAPI backend supporting user management, book management, reviews, document ingestion, and RAG-based Q&A. Includes JWT authentication obtained via HTTP Basic login.

## Features
- Async SQLAlchemy + asyncpg
- HTTP Basic login -> JWT bearer auth
- Book CRUD, reviews, summary, recommendations
- Document upload and ingestion with embeddings
- RAG Q&A powered by OpenRouter (Llama3)
- Structured logging and error handling

## Quick Start
1. Create a virtual environment and install deps:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
   - `pip install -e .[test]`
   - Optional ML: `pip install -e .[ml]`
2. Copy environment file:
   - `copy .env.example .env`
3. Update `DATABASE_URL` for your PostgreSQL instance.
4. Run the API:
   - `uvicorn app.main:app --reload`
5. Open docs:
   - http://localhost:8000/docs

## Testing
- `pytest`

## Recommendation Model
- Optional TF-IDF model for recommendations.
- Train using `POST /api/v1/recommendations/train` (admin only).

## Auth Flow
- `POST /api/v1/auth/signup` to create a user.
- `POST /api/v1/auth/token` using HTTP Basic to retrieve JWT.
- Use `Authorization: Bearer <token>` for protected endpoints.

## AWS Deployment Notes
- Use RDS for PostgreSQL, ECS or EC2 for API, and S3 for document storage (if needed).
- Set environment variables through your deployment config (ECS task definition or EC2 systemd service).
