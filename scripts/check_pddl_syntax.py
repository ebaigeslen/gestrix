from __future__ import annotations
import sys
from pathlib import Path

RAW = Path("data/raw")


def is_probably_pddl(text: str) -> bool:
    t = text.lower()
    return "(define" in t and (
        ":domain" in t or ":predicates" in t or ":objects" in t or ":actions" in t
    )


def main() -> int:
    files = [p for p in RAW.rglob("*.pddl") if p.is_file()]
    bad = []
    for p in files:
        try:
            txt = p.read_text(errors="ignore")
        except Exception as e:
            bad.append(f"{p} (read error: {e})")
            continue
        if not is_probably_pddl(txt):
            bad.append(str(p))
    if bad:
        print("PDDL SYNTAX WARN (heuristic):")
        for b in bad:
            print(" -", b)
        return 1
    print(f"PDDL CHECK PASS: {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
