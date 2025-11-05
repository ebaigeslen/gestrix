from __future__ import annotations
import json
import sys
from pathlib import Path

# paths
META = Path("metadata/checksums.json")


# lazy import so this script works even if src isn't on sys.path
def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not META.exists():
        print("NO METADATA: run scripts/gen_checksums.py first")
        return 2

    entries = json.loads(META.read_text())
    ok = 0
    problems: list[tuple[str, str]] = []

    for e in entries:
        p = Path(e["path"])
        if not p.exists():
            problems.append((str(p), "missing"))
            continue
        current = sha256_file(p)
        if current == e["sha256"]:
            ok += 1
        else:
            problems.append((str(p), "mismatch"))

    if problems:
        print("INTEGRITY FAIL:")
        for path, reason in problems:
            print(f" - {path}: {reason}")
        return 1

    print(f"INTEGRITY PASS: {ok} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
