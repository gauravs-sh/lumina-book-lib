# LuminaLib

Production-ready, modular full-stack application with FastAPI backend and Next.js frontend. Includes book ingestion, borrowing, reviews, AI summaries, and personalized recommendations. Designed for clean architecture, DI, and extensibility.

## Contents
- [Architecture](ARCHITECTURE.md)
- [Backend Guide](backend/README.md)
- [Frontend Guide](frontend/README.md)
- [API Reference](docs/api.md)
- [Deployment Guide (AWS)](docs/deployment-aws.md)
- [Testing Guide](docs/testing.md)

## Quick Start (Local)
1. Backend:
   - Go to backend directory.
   - Create a venv and install deps.
   - Copy backend/.env.example to backend/.env and update `DATABASE_URL`.
   - Run: `uvicorn app.main:app --reload`.
2. Frontend:
   - Go to frontend directory.
   - Install deps and run `npm run dev`.
3. Open http://localhost:5173.

## Docker (Local)
- Build and run everything:
   - `docker compose up --build`
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs
- LLM Mock: http://localhost:9000/v1/chat/completions

## Core Features
- JWT auth with signup/login/profile/logout.
- Book ingestion with file storage abstraction (local/S3).
- Borrow/return enforcement and review gating.
- Async AI book summaries and review consensus.
- Personalized recommendations via user preferences.
- Swappable LLM provider (mock/OpenRouter/HTTP).
- Async SQLAlchemy and PostgreSQL.
- Unit tests for critical backend and frontend components.

## Project Structure
- backend/ - FastAPI backend (async)
- frontend/ - Next.js frontend (SSR)
- llm-mock/ - Local mock LLM service
- docs/ - API, deployment, and testing documentation

## Minimum Requirements
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## License
MIT
