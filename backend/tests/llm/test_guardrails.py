"""Architecture-enforcing scans over app/.

These guard the two hard rules from CLAUDE.md / GES-5:
  1. Only app/llm/client.py may import `litellm`.
  2. No raw `openrouter/...` model strings outside the DB layer (use aliases).
"""

import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[2] / "app"

_LITELLM_IMPORT = re.compile(r"^\s*(from|import)\s+litellm\b", re.MULTILINE)
_RAW_MODEL = re.compile(r"openrouter/[\w.-]+/[\w.-]+")


def _py_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def test_only_client_imports_litellm() -> None:
    offenders = [
        p.relative_to(APP_DIR).as_posix()
        for p in _py_files(APP_DIR)
        if _LITELLM_IMPORT.search(p.read_text(encoding="utf-8"))
    ]
    assert offenders == ["llm/client.py"], (
        f"Only app/llm/client.py may import litellm; found: {offenders}"
    )


def test_no_raw_openrouter_model_strings_outside_db_layer() -> None:
    # app/llm/ legitimately deals in provider_model strings; everything else
    # must reference models by alias only.
    llm_dir = APP_DIR / "llm"
    offenders = [
        p.relative_to(APP_DIR).as_posix()
        for p in _py_files(APP_DIR)
        if llm_dir not in p.parents and _RAW_MODEL.search(p.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"Raw openrouter/* model strings found outside app/llm/: {offenders}"
