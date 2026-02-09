# Testing

## Backend
- `pytest`
- Uses SQLite for testing via `DATABASE_URL=sqlite+aiosqlite:///./test.db`.

## Frontend
- `npm test`

## LLM Testing
- `pytest tests/test_llm.py -v`
- Requires valid API keys in `.env` file
- Tests OpenAI and Anthropic integrations
- Uses mock responses when API keys are not available
- Validates prompt engineering and response parsing
- Tests error handling and retry logic
