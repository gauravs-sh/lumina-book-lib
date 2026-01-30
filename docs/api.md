# API Reference

Base URL: `http://localhost:8000/api/v1`

## Auth
- `POST /auth/signup` - Create user
- `POST /auth/token` - Basic auth login, returns JWT

## Users (Admin)
- `GET /users` - List users
- `PUT /users/{user_id}/role` - Update role

## Books
- `POST /books` - Create book (optional content for summary)
- `GET /books` - List books
- `GET /books/{id}` - Get book
- `PUT /books/{id}` - Update book
- `DELETE /books/{id}` - Delete book
- `GET /books/{id}/summary` - Summary + aggregated rating

## Reviews
- `POST /books/{id}/reviews` - Add review
- `GET /books/{id}/reviews` - List reviews

## Documents
- `POST /documents` - Create document
- `POST /documents/upload` - Upload file
- `GET /documents` - List user documents
- `GET /documents/{id}` - Get document

## Ingestion
- `POST /ingestion/{document_id}` - Start ingestion
- `GET /ingestion/jobs` - List jobs
- `GET /ingestion/jobs/{job_id}` - Job status

## Q&A
- `POST /qa` - Ask question

## Recommendations
- `GET /recommendations?genres=Drama,Fantasy` - Recommend books
- `GET /recommendations?book_id=1` - Similar book recommendations
- `POST /recommendations/train` - Train ML recommender (admin)

## AI
- `POST /generate-summary` - Generate summary (requires auth). Body: `{ "content": "..." }`
