#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install -U pip
python -m pip install "z3-solver>=4.12" "pytest>=8.0" "PyYAML>=6.0" "Jinja2>=3.1"
