from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def format_result(data: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output_format == "yaml":
        return _format_yaml(data)
    if output_format == "text":
        return _format_text(data)
    raise ValueError(f"unsupported output format: {output_format}")


def write_result(path: Path | None, content: str) -> None:
    if path is None:
        print(content, end="")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _format_yaml(data: dict[str, Any]) -> str:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("YAML output requires PyYAML to be installed") from exc
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def _format_text(data: dict[str, Any]) -> str:
    lines = [f"status={data['status']}"]
    if "reason" in data:
        lines.append(f"reason={data['reason']}")
    for name, value in data.get("model", {}).items():
        lines.append(f"{name}={_text_value(value)}")
    return "\n".join(lines) + "\n"


def _text_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
