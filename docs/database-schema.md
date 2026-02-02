# Database Schema

This document reflects the current database schema defined in the backend SQLAlchemy models.

## ER Diagram

```mermaid
erDiagram
    USERS {
        INT id PK
        VARCHAR email
        VARCHAR hashed_password
        VARCHAR role
        DATETIME created_at
    }

    BOOKS {
        INT id PK
        VARCHAR title
        VARCHAR author
        VARCHAR genre
        INT year_published
        VARCHAR file_key
        VARCHAR file_name
        VARCHAR content_type
        INT file_size
        TEXT content_text
        TEXT summary
        TEXT review_summary
        DATETIME created_at
    }

    BOOK_BORROWS {
        INT id PK
        INT book_id FK
        INT user_id FK
        DATETIME borrowed_at
        DATETIME returned_at
    }

    DOCUMENTS {
        INT id PK
        VARCHAR filename
        TEXT content
        INT owner_id FK
        DATETIME created_at
    }

    DOCUMENT_CHUNKS {
        INT id PK
        INT document_id FK
        TEXT content
        JSON embedding
        DATETIME created_at
    }

    INGESTION_JOBS {
        INT id PK
        INT document_id FK
        VARCHAR status
        VARCHAR error
        DATETIME created_at
        DATETIME updated_at
    }

    REVIEWS {
        INT id PK
        INT book_id FK
        INT user_id FK
        TEXT review_text
        INT rating
        DATETIME created_at
    }

    USER_PREFERENCES {
        INT id PK
        INT user_id FK
        JSON preferences
    }

    USERS ||--o{ BOOK_BORROWS : "borrows"
    BOOKS ||--o{ BOOK_BORROWS : "is borrowed"

    USERS ||--o{ DOCUMENTS : "owns"
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "has"
    DOCUMENTS ||--o{ INGESTION_JOBS : "ingests"

    USERS ||--o{ REVIEWS : "writes"
    BOOKS ||--o{ REVIEWS : "receives"

    USERS ||--|| USER_PREFERENCES : "has"
```

## Primary Key to Foreign Key Links

- `book_borrows.book_id` → `books.id`
- `book_borrows.user_id` → `users.id`
- `documents.owner_id` → `users.id`
- `document_chunks.document_id` → `documents.id`
- `ingestion_jobs.document_id` → `documents.id`
- `reviews.book_id` → `books.id`
- `reviews.user_id` → `users.id`
- `user_preferences.user_id` → `users.id` (unique 1:1)
