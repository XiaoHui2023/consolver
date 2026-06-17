#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

rm -rf .venv build dist

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates wget bzip2 binutils

MINICONDA=Miniconda3-py310_23.5.2-0-Linux-x86_64.sh
MINICONDA_URL="https://repo.anaconda.com/miniconda/${MINICONDA}"
for attempt in 1 2 3; do
  wget -q "$MINICONDA_URL" -O "/tmp/${MINICONDA}" && break
  if [[ "$attempt" == "3" ]]; then
    echo "ERROR: failed to download Miniconda" >&2
    exit 1
  fi
  sleep 5
done

bash "/tmp/${MINICONDA}" -b -p /opt/conda
export PATH="/opt/conda/bin:$PATH"

python -m venv .venv
export PACK_LINUX_SKIP_STATICX=1
bash tools/pack.sh src
