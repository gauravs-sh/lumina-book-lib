from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LLM Mock")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float | None = None
    max_tokens: int | None = None


@app.post("/v1/chat/completions")
async def chat_completions(payload: ChatRequest) -> dict:
    user_message = next((m.content for m in payload.messages if m.role == "user"), "")
    system_message = next((m.content for m in payload.messages if m.role == "system"), "")
    content = f"Mock response. System: {system_message[:120]} User: {user_message[:220]}"
    return {
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ]
    }
