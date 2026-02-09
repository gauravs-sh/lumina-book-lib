from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from fastapi.testclient import TestClient


def load_llm_mock_app():
    main_path = Path(__file__).resolve().parents[1] / "app" / "main.py"
    spec = spec_from_file_location("llm_mock_main", main_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load llm-mock app module.")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app


def test_chat_completions_returns_mock_response():
    app = load_llm_mock_app()
    client = TestClient(app)
    payload = {
        "model": "mock",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello there!"},
        ],
        "temperature": 0.2,
        "max_tokens": 64,
    }

    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "choices" in body and body["choices"]
    message = body["choices"][0]["message"]
    assert message["role"] == "assistant"
    assert "Mock response." in message["content"]
    assert "System:" in message["content"]
    assert "User:" in message["content"]
