from typing import Any, cast

import litellm
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.config import Settings
from app.llm.aliases import resolve_alias
from app.llm.exceptions import LLMCallError, LLMStructuredOutputError

# NOTE: This is the ONLY module in the codebase permitted to import `litellm`.
# Everything else must go through chat_completion / chat_completion_structured.
# Enforced by tests/llm/test_guardrails.py.


def _completion(provider_model: str, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
    """Single funnel for every LiteLLM call. Wraps any call failure as LLMCallError.

    litellm's exception classes (RateLimitError, Timeout, AuthenticationError, ...)
    derive from the OpenAI SDK's exception tree, not from a single litellm base, so
    there is no reliable litellm-only base to catch. Since the only statement in the
    try is the provider call (alias resolution happens earlier, outside), catching
    Exception here cleanly normalizes every provider/network failure.
    """
    settings = Settings()
    try:
        return litellm.completion(
            model=provider_model,
            messages=messages,
            api_key=settings.OPENROUTER_API_KEY,
            api_base=settings.OPENROUTER_BASE_URL,
            timeout=settings.LLM_DEFAULT_TIMEOUT_SECONDS,
            num_retries=settings.LLM_MAX_RETRIES,
            extra_headers={
                "HTTP-Referer": settings.OPENROUTER_REFERER,
                "X-Title": settings.OPENROUTER_APP_TITLE,
            },
            **kwargs,
        )
    except Exception as exc:
        raise LLMCallError(
            f"LLM call failed for model {provider_model!r}: {exc}",
            model=provider_model,
        ) from exc


def chat_completion(
    db: Session, alias_name: str, messages: list[dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    """Resolve `alias_name` to a provider model and run a chat completion.

    Returns the raw LiteLLM response (supports dict-style access).
    """
    provider_model = resolve_alias(db, alias_name)
    return cast("dict[str, Any]", _completion(provider_model, messages, **kwargs))


def chat_completion_structured(
    db: Session,
    alias_name: str,
    messages: list[dict[str, Any]],
    response_model: type[BaseModel],
    **kwargs: Any,
) -> BaseModel:
    """Like chat_completion, but forwards `response_format` and parses the
    assistant message content into `response_model`.

    Raises LLMStructuredOutputError if the content can't be parsed.
    """
    provider_model = resolve_alias(db, alias_name)
    response = _completion(provider_model, messages, response_format=response_model, **kwargs)
    try:
        content = response["choices"][0]["message"]["content"]
        return response_model.model_validate_json(content)
    except (ValidationError, ValueError, TypeError, KeyError, IndexError) as exc:
        raise LLMStructuredOutputError(
            f"Failed to parse structured output into {response_model.__name__}: {exc}"
        ) from exc
