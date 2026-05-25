"""Guard the tenacity runtime dependency.

litellm uses tenacity for its retry logic, which our LLM client exercises via
`num_retries` (LLM_MAX_RETRIES). litellm does not declare tenacity as a hard
dependency, so it must stay an explicit dependency of this project — otherwise
any retryable provider error (e.g. 429/5xx) raises ModuleNotFoundError instead
of being retried and then wrapped as LLMCallError.
"""


def test_tenacity_is_importable() -> None:
    import tenacity  # noqa: F401
