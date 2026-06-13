from __future__ import annotations

from pathlib import Path
from typing import Any


def render_template(path: Path, data: dict[str, Any]) -> str:
    try:
        from jinja2 import Environment
    except ImportError as exc:
        raise RuntimeError("template output requires Jinja2 to be installed") from exc

    template = Environment(keep_trailing_newline=True).from_string(path.read_text(encoding="utf-8"))
    return template.render(**data)
