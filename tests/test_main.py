from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_help_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "consolver" in proc.stdout.lower()


def test_solve_sat_prints_json_to_stdout(tmp_path: Path) -> None:
    smt2 = tmp_path / "sat.smt2"
    smt2.write_text(
        """
(set-logic QF_LIA)
(declare-const a Int)
(declare-const b Int)
(assert (= (+ a b) 12))
(assert (> a b))
(assert (= b 5))
(check-sat)
(get-model)
""".strip(),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "solve", str(smt2)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == {"status": "sat", "model": {"a": 7, "b": 5}}


def test_solve_accepts_smt2_text_without_input_file() -> None:
    smt2_text = """
(set-logic QF_LIA)
(declare-const a Int)
(assert (= a 4))
(check-sat)
(get-model)
""".strip()

    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "solve", "--input-text", smt2_text],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == {"status": "sat", "model": {"a": 4}}


def test_solve_unsat_writes_json_file(tmp_path: Path) -> None:
    smt2 = tmp_path / "unsat.smt2"
    output = tmp_path / "model.json"
    smt2.write_text(
        """
(set-logic QF_LIA)
(declare-const a Int)
(assert (= a 1))
(assert (= a 2))
(check-sat)
""".strip(),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "solve", str(smt2), "-o", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("unsat: wrote ")
    assert json.loads(output.read_text(encoding="utf-8")) == {"status": "unsat", "model": {}}


def test_solve_bitvec_preserves_width_and_hex(tmp_path: Path) -> None:
    smt2 = tmp_path / "bv.smt2"
    smt2.write_text(
        """
(set-logic QF_BV)
(declare-const x (_ BitVec 8))
(assert (= x #x0f))
(check-sat)
(get-model)
""".strip(),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "solve", str(smt2)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["model"]["x"] == {"value": 15, "hex": "0x0f", "width": 8}


def test_template_output_reads_unified_model(tmp_path: Path) -> None:
    smt2 = tmp_path / "sat.smt2"
    template = tmp_path / "model.txt.j2"
    smt2.write_text(
        """
(set-logic QF_LIA)
(declare-const a Int)
(assert (= a 3))
(check-sat)
(get-model)
""".strip(),
        encoding="utf-8",
    )
    template.write_text("a={{ model.a }} status={{ status }}\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "solve", str(smt2), "--template", str(template)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "a=3 status=sat\n"


def test_cli_argument_error_returns_nonzero() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "src"), "solve"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode != 0


def test_cli_rejects_file_and_input_text_together(tmp_path: Path) -> None:
    smt2 = tmp_path / "sat.smt2"
    smt2.write_text("(check-sat)\n", encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "src"),
            "solve",
            str(smt2),
            "--input-text",
            "(check-sat)",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode != 0
    assert "either input file or --input-text" in proc.stderr


def test_example_runs_linear_demo() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "example" / "__main__.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=ROOT,
    )

    assert proc.returncode == 0, proc.stderr
    assert '"status": "sat"' in proc.stdout
    assert '"status": "unsat"' in proc.stdout
    assert "status=sat" in proc.stdout
    assert (ROOT / "example" / "output" / "unsat.json").is_file()
