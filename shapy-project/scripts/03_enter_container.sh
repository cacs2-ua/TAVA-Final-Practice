#!/usr/bin/env bash
set -euo pipefail

# SCRIPT 03: Open an interactive Bash shell inside the running SHAPY CPU Docker container.

CONTAINER_NAME="shapy-cpu"

if ! docker ps --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  echo "[ERROR] Container '${CONTAINER_NAME}' is not running."
  echo
  echo "Start it first with:"
  echo "  bash scripts/02_run_jupyter.sh"
  exit 1
fi

echo "[INFO] Entering container: ${CONTAINER_NAME}"
docker exec -it "${CONTAINER_NAME}" bash
