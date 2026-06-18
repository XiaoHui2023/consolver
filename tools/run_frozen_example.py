from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "example"


def _binary_path() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    name = "consolver.exe" if sys.platform == "win32" else "consolver"
    return ROOT / "dist" / name


def _run(binary: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    cmd = [str(binary), *args]
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        print(f"command failed: {' '.join(cmd)}", file=sys.stderr)
        print(completed.stdout, file=sys.stderr)
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)
    return completed


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        print(f"unexpected {label}: {actual!r}", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    binary = _binary_path()
    if not binary.is_file():
        print(f"frozen executable not found: {binary}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="consolver-frozen-example-") as tmp:
        work = Path(tmp)
        shutil.copytree(EXAMPLE_DIR, work / "example")
        example = work / "example"
        output = example / "output"
        if output.exists():
            shutil.rmtree(output)
        output.mkdir()

        sat_json = output / "sat.json"
        _run(binary, ["solve", str(example / "sat.smt2"), "-o", str(sat_json)], work)
        _assert_equal(_read_json(sat_json), {"status": "sat", "model": {"a": 7, "b": 5}}, "sat JSON")

        unsat_json = output / "unsat.json"
        _run(binary, ["solve", str(example / "unsat.smt2"), "-o", str(unsat_json)], work)
        _assert_equal(_read_json(unsat_json), {"status": "unsat", "model": {}}, "unsat JSON")

        bv_json = output / "bv.json"
        _run(binary, ["solve", str(example / "bv.smt2"), "-o", str(bv_json)], work)
        _assert_equal(
            _read_json(bv_json),
            {"status": "sat", "model": {"x": {"value": 15, "hex": "0x0f", "width": 8}}},
            "bit-vector JSON",
        )

        sat_yaml = output / "sat.yaml"
        _run(binary, ["solve", str(example / "sat.smt2"), "--format", "yaml", "-o", str(sat_yaml)], work)
        yaml_text = sat_yaml.read_text(encoding="utf-8")
        for expected in ("status: sat", "a: 7", "b: 5"):
            if expected not in yaml_text:
                print(f"missing YAML fragment {expected!r} in:\n{yaml_text}", file=sys.stderr)
                return 1

        rendered = output / "from_template.txt"
        _run(
            binary,
            [
                "solve",
                str(example / "sat.smt2"),
                "--template",
                str(example / "model.txt.j2"),
                "-o",
                str(rendered),
            ],
            work,
        )
        _assert_equal(rendered.read_text(encoding="utf-8"), "status=sat\na=7\nb=5\n", "template output")

    print("frozen example passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
