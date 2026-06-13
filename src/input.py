from __future__ import annotations

from pathlib import Path


def read_smt2_file(path: Path) -> str:
    if path.suffix.lower() != ".smt2":
        raise ValueError(f"input file must use .smt2 extension: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"input file does not exist: {path}")
    return path.read_text(encoding="utf-8")


def validate_smt2_text(text: str) -> str:
    if not text.strip():
        raise ValueError("SMT-LIB input text must not be empty")
    return text
