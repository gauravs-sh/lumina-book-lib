# Smart QA Platform

Production-ready, modular full-stack application with FastAPI backend and React frontend. Includes RAG-based Q&A, document ingestion, user management, book management, and reviews. Designed for quality, testability, and deployment.

## Contents
- [Architecture](docs/architecture.md)
- [Backend Guide](backend/README.md)
- [Frontend Guide](frontend/README.md)
- [RAG & AI Guide](docs/rag-ai.md)
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

## Core Features
- Authentication with HTTP Basic login -> JWT bearer tokens.
- Admin-only user management.
- Book CRUD, reviews, summaries, and recommendations.
- Document upload + ingestion with embeddings.
- RAG Q&A with OpenRouter (Llama3).
- Async SQLAlchemy and asyncpg.
- Comprehensive unit tests for backend and frontend.

## Project Structure
- backend/ - FastAPI backend (async)
- frontend/ - React frontend (Vite)
- docs/ - Architecture, API, deployment, and RAG documentation

## Minimum Requirements
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## License
MIT
