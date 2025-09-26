from __future__ import annotations
import argparse
from typing import Optional


def hello(name: str = "world") -> str:
    return f"Hello, {name}!"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gestrix", description="Gestrix CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_hello = sub.add_parser("hello", help="print a friendly greeting")
    p_hello.add_argument("name", nargs="?", default="world")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "hello":
        print(hello(args.name))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
