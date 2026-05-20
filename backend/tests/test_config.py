import pytest

from app.config import Settings


def test_settings_load_defaults() -> None:
    settings = Settings()
    assert settings.APP_NAME
    assert settings.APP_VERSION
    assert settings.ENV


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    settings = Settings()
    assert settings.APP_VERSION == "9.9.9"
