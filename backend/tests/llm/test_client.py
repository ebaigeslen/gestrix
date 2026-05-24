from typing import Any
from unittest.mock import MagicMock

import pytest
from litellm.exceptions import APIError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import Settings
from app.llm.client import chat_completion, chat_completion_structured
from app.llm.exceptions import AliasNotFoundError, LLMCallError, LLMStructuredOutputError

MESSAGES = [{"role": "user", "content": "hi"}]


def _response(content: str) -> dict[str, Any]:
    return {"choices": [{"message": {"content": content}}]}


class Demo(BaseModel):
    answer: str
    score: int


def test_chat_completion_resolves_alias_before_call(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    mock_litellm.return_value = _response("ok")
    chat_completion(db_session, "writer-default", MESSAGES)
    assert mock_litellm.call_args.kwargs["model"] == "openrouter/openai/gpt-4o"


def test_chat_completion_passes_api_key_and_base_url(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    mock_litellm.return_value = _response("ok")
    chat_completion(db_session, "writer-default", MESSAGES)
    settings = Settings()
    kwargs = mock_litellm.call_args.kwargs
    assert kwargs["api_key"] == settings.OPENROUTER_API_KEY
    assert kwargs["api_base"] == settings.OPENROUTER_BASE_URL


def test_chat_completion_passes_openrouter_headers(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    mock_litellm.return_value = _response("ok")
    chat_completion(db_session, "writer-default", MESSAGES)
    headers = mock_litellm.call_args.kwargs["extra_headers"]
    assert "HTTP-Referer" in headers
    assert "X-Title" in headers


def test_chat_completion_unknown_alias_raises_before_http(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    with pytest.raises(AliasNotFoundError):
        chat_completion(db_session, "no-such-alias", MESSAGES)
    mock_litellm.assert_not_called()


def test_chat_completion_wraps_litellm_error_as_llmcallerror(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    original = APIError(
        status_code=500, message="boom", llm_provider="openrouter", model="x"
    )
    mock_litellm.side_effect = original
    with pytest.raises(LLMCallError) as exc:
        chat_completion(db_session, "writer-default", MESSAGES)
    assert exc.value.__cause__ is original
    assert exc.value.model == "openrouter/openai/gpt-4o"


def test_chat_completion_structured_passes_response_format(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    mock_litellm.return_value = _response('{"answer": "x", "score": 1}')
    chat_completion_structured(db_session, "writer-default", MESSAGES, Demo)
    assert mock_litellm.call_args.kwargs["response_format"] is Demo


def test_chat_completion_structured_parses_into_model(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    mock_litellm.return_value = _response('{"answer": "hello", "score": 7}')
    result = chat_completion_structured(db_session, "writer-default", MESSAGES, Demo)
    assert isinstance(result, Demo)
    assert result.answer == "hello"
    assert result.score == 7


def test_chat_completion_structured_bad_json_raises(
    db_session: Session, mock_litellm: MagicMock
) -> None:
    mock_litellm.return_value = _response("this is not json")
    with pytest.raises(LLMStructuredOutputError):
        chat_completion_structured(db_session, "writer-default", MESSAGES, Demo)
