# Backend (FastAPI)

## Overview
Async FastAPI backend for LuminaLib with JWT auth, book ingestion, borrow/return, reviews, and AI summaries. Designed for DI and provider swapping (LLM + storage).

## Features
- Async SQLAlchemy + asyncpg
- JWT signup/login/profile/logout
- Book upload (PDF/text), borrow/return, and CRUD
- Review analysis and AI summaries via background tasks
- Recommendation engine using user preferences
- Swappable LLM and storage providers
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
- `POST /api/v1/auth/login` to retrieve JWT.
- `GET /api/v1/auth/profile` to view profile.
- `PUT /api/v1/auth/profile` to update email/password.
- `POST /api/v1/auth/logout` to sign out.

## AWS Deployment Notes
- Use RDS for PostgreSQL, ECS or EC2 for API, and S3 for document storage (if needed).
- Set environment variables through your deployment config (ECS task definition or EC2 systemd service).
