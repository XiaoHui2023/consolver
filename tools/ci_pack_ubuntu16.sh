#!/usr/bin/env bash
# CI helper: pack consolver inside Ubuntu 16.04 (glibc 2.23 baseline).
# Invoked from .github/workflows/release.yml via docker run; also runnable locally:
#   docker run --rm -v "$PWD:/work" -w /work ubuntu:16.04 bash tools/ci_pack_ubuntu16.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf .venv build dist

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl wget patchelf bzip2 binutils

MINICONDA_SH="Miniconda3-py310_23.5.2-0-Linux-x86_64.sh"
for attempt in 1 2 3 4 5; do
  if wget --tries=1 -O /tmp/miniconda.sh "https://repo.anaconda.com/miniconda/${MINICONDA_SH}"; then
    break
  fi
  if [ "$attempt" -eq 5 ]; then
    echo "ERROR: failed to download Miniconda after 5 attempts" >&2
    exit 1
  fi
  sleep 5
done
bash /tmp/miniconda.sh -b -p /opt/miniconda
/opt/miniconda/bin/python -m venv .venv

bash tools/pack.sh src
