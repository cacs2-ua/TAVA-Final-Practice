#!/usr/bin/env bash
set -euo pipefail

echo "[1/2] Testing Docker GPU visibility with nvidia/cuda..."
docker run --rm --gpus all nvidia/cuda:10.2-base-ubuntu18.04 nvidia-smi

echo
echo "[2/2] Testing PyTorch CUDA inside the built SHAPY image..."
docker run --rm --gpus all shapy-cu102-ubuntu18:latest bash -lc \
'python - <<PY
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("cuda runtime from torch:", torch.version.cuda)
print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE")
PY'
