class LLMError(Exception):
    """Base class for all LLM-gateway errors."""


class AliasNotFoundError(LLMError):
    """No active model_aliases row exists for the requested alias_name."""


class LLMCallError(LLMError):
    """Wraps a provider/network failure from the underlying LiteLLM call."""

    def __init__(self, message: str, *, model: str | None = None) -> None:
        super().__init__(message)
        self.model = model


class LLMStructuredOutputError(LLMError):
    """The model response could not be parsed into the requested schema."""
