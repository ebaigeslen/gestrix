from __future__ import annotations
import json
import sys
from pathlib import Path

# add local src/ so Python can import gestrix
sys.path.insert(0, str(Path("src").resolve()))

from gestrix.utils.checksum import sha256_file

RAW = Path("data/raw")
META = Path("metadata")
OUT = META / "checksums.json"


def main():
    files = [p for p in RAW.rglob("*") if p.is_file()]
    data = [{"path": str(p.as_posix()), "sha256": sha256_file(p)} for p in files]
    META.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2))
    print(f"✅ wrote {OUT} with {len(data)} entries")


if __name__ == "__main__":
    sys.exit(main())
