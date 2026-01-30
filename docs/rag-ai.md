# RAG & AI

## Llama3 via OpenRouter
Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` in backend `.env`. The app uses OpenRouter for:
- Book summaries
- RAG answers

If the API key is not configured, the app returns truncated summaries and basic responses.

## Ingestion Pipeline
1. Documents are split into chunks (500 chars).
2. Each chunk is embedded using a deterministic hashing-based embedding (local fallback).
3. Embeddings are stored in `document_chunks`.

## Q&A
- The question is embedded.
- Similar chunks are selected via cosine similarity.
- The top chunks are sent to Llama3 to generate answers.

## Future Enhancements
- Replace local embeddings with a vector DB (pgvector, Pinecone, Weaviate).
- Introduce batched ingestion with background jobs and queues.
