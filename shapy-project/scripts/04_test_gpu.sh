#!/usr/bin/env bash
set -euo pipefail

# SCRIPT 04: Test the SHAPY Docker image in CPU mode.
# This intentionally does NOT use --gpus all.

cd "$(dirname "$0")/.."

IMAGE_NAME="shapy-cu102-ubuntu18:latest"

echo "[1/3] Checking that the SHAPY Docker image exists..."
if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
  echo "[ERROR] Docker image '${IMAGE_NAME}' does not exist."
  echo
  echo "Build it first with:"
  echo "  docker compose build shapy"
  exit 1
fi

echo "[OK] Found image: ${IMAGE_NAME}"

echo
echo "[2/3] Testing Python + PyTorch in CPU-only mode..."
docker run --rm \
  -e CUDA_VISIBLE_DEVICES="" \
  -e NVIDIA_VISIBLE_DEVICES=none \
  -e FORCE_CUDA=0 \
  "${IMAGE_NAME}" bash -lc '
set -e

python - <<PY
import os
import sys
import torch

print("python executable:", sys.executable)
print("python version:", sys.version)
print("torch version:", torch.__version__)
print("torch CUDA runtime:", torch.version.cuda)
print("CUDA_VISIBLE_DEVICES:", repr(os.environ.get("CUDA_VISIBLE_DEVICES")))
print("NVIDIA_VISIBLE_DEVICES:", repr(os.environ.get("NVIDIA_VISIBLE_DEVICES")))
print("cuda available:", torch.cuda.is_available())

assert sys.version_info.major == 3, sys.version
assert sys.version_info.minor == 8, sys.version
assert torch.__version__.startswith("1.8.1"), torch.__version__
assert torch.cuda.is_available() is False, "ERROR: CUDA should be disabled in CPU mode"

device = torch.device("cpu")
x = torch.ones((2048, 2048), device=device)
y = x @ x

print("CPU tensor test OK:", y.shape, y.device)
print("STATUS: SHAPY Docker CPU test passed.")
PY
'

echo
echo "[3/3] CPU mode is ready."
