#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[INFO] Starting SHAPY Jupyter server in CPU mode..."
echo "[INFO] URL: http://127.0.0.1:8888/lab?token=shapy"

docker compose up shapy
