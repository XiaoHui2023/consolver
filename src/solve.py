from __future__ import annotations

from pathlib import Path


def solve_smt2_file(path: Path, timeout_ms: int | None = None) -> tuple[str, object | None, str | None]:
    return solve_smt2_text(path.read_text(encoding="utf-8"), timeout_ms)


def solve_smt2_text(text: str, timeout_ms: int | None = None) -> tuple[str, object | None, str | None]:
    import z3

    solver = z3.Solver()
    if timeout_ms is not None:
        if timeout_ms <= 0:
            raise ValueError("--timeout-ms must be a positive integer")
        solver.set(timeout=timeout_ms)

    solver.add(z3.parse_smt2_string(text))
    result = solver.check()

    if result == z3.sat:
        return "sat", solver.model(), None
    if result == z3.unsat:
        return "unsat", None, None
    return "unknown", None, solver.reason_unknown() or None
