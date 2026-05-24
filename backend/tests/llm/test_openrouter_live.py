import os

import pytest
from sqlalchemy.orm import Session

from app.llm.client import chat_completion

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("OPENROUTER_API_KEY"),
        reason="needs OPENROUTER_API_KEY for a live OpenRouter call",
    ),
]


def test_live_chat_completion_against_openrouter(db_session: Session) -> None:
    response = chat_completion(
        db_session,
        "writer-default",
        [{"role": "user", "content": "Reply with exactly the word: pong"}],
    )
    content = response["choices"][0]["message"]["content"]
    assert "pong" in content.lower()
