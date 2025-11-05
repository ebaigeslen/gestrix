from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Dict

CHUNK_SIZE = 1024 * 1024  # 1MB chunks (memory-safe for large files)


def sha256_file(path: str | Path) -> str:
    """Return hex SHA-256 checksum for a file, reading in chunks."""
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_dir(root: str | Path, patterns: tuple[str, ...] = ("*",)) -> Dict[str, str]:
    """
    Return {relative_path: sha256} for all files under root matching patterns.
    Ignores directories.
    """
    r = Path(root)
    results: Dict[str, str] = {}
    for pat in patterns:
        for fp in r.rglob(pat):
            if fp.is_file():
                rel = fp.relative_to(r).as_posix()
                results[rel] = sha256_file(fp)
    return results
