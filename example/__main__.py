from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from model import SolveResult, model_to_python
from output import format_result, write_result
from solve import solve_smt2_file
from template import render_template

EXAMPLE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = EXAMPLE_DIR / "output"


def example_step(message: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{stamp}] {message}", file=sys.stderr, flush=True)


def _section(title: str) -> None:
    print(f"=== {title} ===", flush=True)


def _solve(path: Path) -> SolveResult:
    status, z3_model, reason = solve_smt2_file(path)
    return SolveResult(status=status, model=model_to_python(z3_model), reason=reason)


def phase_sat_json() -> int:
    """求解 sat.smt2 并打印 JSON。"""
    result = _solve(EXAMPLE_DIR / "sat.smt2")
    expected = {"status": "sat", "model": {"a": 7, "b": 5}}
    data = result.to_dict()
    if data != expected:
        print(f"unexpected sat result: {data}", file=sys.stderr)
        return 1

    _section("sat（JSON 到控制台）")
    print(format_result(data, "json"), end="")
    return 0


def phase_unsat_file() -> int:
    """求解 unsat.smt2 并写入 output/unsat.json。"""
    result = _solve(EXAMPLE_DIR / "unsat.smt2")
    expected = {"status": "unsat", "model": {}}
    data = result.to_dict()
    if data != expected:
        print(f"unexpected unsat result: {data}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "unsat.json"
    write_result(output_path, format_result(data, "json"))

    _section("unsat（写入文件）")
    rel = output_path.relative_to(EXAMPLE_DIR)
    print(f"{rel}")
    print(output_path.read_text(encoding="utf-8"), end="")
    return 0


def phase_bitvec() -> int:
    """求解 bv.smt2 并校验位向量模型。"""
    result = _solve(EXAMPLE_DIR / "bv.smt2")
    x_model = result.model.get("x")
    expected_x = {"value": 15, "hex": "0x0f", "width": 8}
    if result.status != "sat" or x_model != expected_x:
        print(f"unexpected bitvec result: {result.to_dict()}", file=sys.stderr)
        return 1

    _section("位向量（JSON）")
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


def phase_yaml() -> int:
    """将 sat 结果写成 YAML。"""
    result = _solve(EXAMPLE_DIR / "sat.smt2")
    try:
        content = format_result(result.to_dict(), "yaml")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_path = OUTPUT_DIR / "sat.yaml"
    write_result(output_path, content)

    _section("YAML 输出")
    rel = output_path.relative_to(EXAMPLE_DIR)
    print(f"{rel}")
    print(content, end="")
    return 0


def phase_template() -> int:
    """用 Jinja2 模板渲染 sat 模型。"""
    result = _solve(EXAMPLE_DIR / "sat.smt2")
    template_path = EXAMPLE_DIR / "model.txt.j2"
    try:
        content = render_template(template_path, result.to_dict())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    expected = "status=sat\na=7\nb=5\n"
    if content != expected:
        print(f"unexpected template output:\n{content!r}", file=sys.stderr)
        return 1

    output_path = OUTPUT_DIR / "from_template.txt"
    write_result(output_path, content)

    _section("Jinja2 模板")
    rel = output_path.relative_to(EXAMPLE_DIR)
    print(f"{rel}")
    print(content, end="")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    example_step("步骤 1/5：sat 整数约束 → JSON")
    if phase_sat_json() != 0:
        return 1

    example_step("步骤 2/5：unsat → output/unsat.json")
    if phase_unsat_file() != 0:
        return 1

    example_step("步骤 3/5：8 位向量")
    if phase_bitvec() != 0:
        return 1

    example_step("步骤 4/5：YAML 输出")
    if phase_yaml() != 0:
        return 1

    example_step("步骤 5/5：Jinja2 模板")
    if phase_template() != 0:
        return 1

    example_step("完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
