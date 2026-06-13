from __future__ import annotations

import argparse
import sys
from pathlib import Path

from input import read_smt2_file, validate_smt2_text
from model import SolveResult, model_to_python
from output import format_result, write_result
from solve import solve_smt2_text
from template import render_template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="consolver",
        description="Solve SMT-LIB files with Z3 and write stable model output.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser(
        "solve",
        help="solve one .smt2 file",
        description="Solve one .smt2 file.",
    )
    solve_parser.add_argument("input", nargs="?", type=Path, help=".smt2 input file")
    solve_parser.add_argument("--input-text", help="SMT-LIB input text")
    solve_parser.add_argument("-o", "--output", type=Path, help="output file")
    solve_parser.add_argument(
        "--format",
        choices=("json", "yaml", "text"),
        default="json",
        help="output format",
    )
    solve_parser.add_argument("--timeout-ms", type=int, help="Z3 timeout in milliseconds")
    solve_parser.add_argument("--template", type=Path, help="Jinja2 text template file")
    solve_parser.set_defaults(func=_run_solve)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"consolver: error: {exc}", file=sys.stderr)
        return 1


def _run_solve(args: argparse.Namespace) -> int:
    smt2_text = _read_smt2_input(args)
    if args.template is not None and not args.template.is_file():
        raise FileNotFoundError(f"template file does not exist: {args.template}")

    status, z3_model, reason = solve_smt2_text(smt2_text, args.timeout_ms)
    result = SolveResult(status=status, model=model_to_python(z3_model), reason=reason)
    data = result.to_dict()

    if args.template is not None:
        content = render_template(args.template, data)
    else:
        content = format_result(data, args.format)

    write_result(args.output, content)
    if args.output is not None:
        print(f"{status}: wrote {args.output}")
    return 0


def _read_smt2_input(args: argparse.Namespace) -> str:
    if args.input is not None and args.input_text is not None:
        raise ValueError("provide either input file or --input-text, not both")
    if args.input_text is not None:
        return validate_smt2_text(args.input_text)
    if args.input is not None:
        return read_smt2_file(args.input)
    raise ValueError("provide input file or --input-text")


if __name__ == "__main__":
    raise SystemExit(main())
