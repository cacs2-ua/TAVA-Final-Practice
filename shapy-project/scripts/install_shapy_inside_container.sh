#!/usr/bin/env bash
set -euo pipefail

# Run inside the container.
# Installs SHAPY Python dependencies and compiles its local CUDA/C++ extensions.

export SHAPY_DIR="${SHAPY_DIR:-/workspace/shapy}"
export PYTHONPATH="${SHAPY_DIR}:${SHAPY_DIR}/attributes:${PYTHONPATH:-}"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
export FORCE_CUDA=1
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export PYOPENGL_PLATFORM="${PYOPENGL_PLATFORM:-egl}"

if [ ! -d "${SHAPY_DIR}/.git" ]; then
  echo "[ERROR] SHAPY repository not found at ${SHAPY_DIR}"
  echo "Run scripts/00_prepare_workspace.sh on the WSL host first."
  exit 1
fi

cd "${SHAPY_DIR}"

python -m pip install --upgrade "pip<24" "setuptools<60" wheel ninja cython

# Install all official requirements except torch/torchvision/sklearn/open3d.
# torch/torchvision are installed in the Dockerfile with CUDA 10.2 wheels.
# sklearn==0.0 is deprecated.
# open3d is pinned manually to avoid pip resolving to an incompatible future version.
grep -vE '^(torch|torchvision)([<=>].*)?$|^sklearn([<=>].*)?$|^open3d([<=>].*)?$' requirements.txt > /tmp/shapy_requirements_filtered.txt

python -m pip install -r /tmp/shapy_requirements_filtered.txt
python -m pip install "open3d==0.17.0"

# SHAPY FAQ recommends pyrender==0.1.43 for headless rendering issues.
python -m pip install "pyrender==0.1.43"

# Install the attributes package.
cd "${SHAPY_DIR}/attributes"
python setup.py install

# Install mesh-mesh-intersection CUDA/C++ extension.
cd "${SHAPY_DIR}/mesh-mesh-intersection"
export CUDA_SAMPLES_INC="$(pwd)/include"
python -m pip install -r requirements.txt
python setup.py install

echo
echo "[OK] SHAPY dependencies and local extensions installed."

python - <<'PY'
import os, sys, torch
print("Python:", sys.version)
print("Torch:", torch.__version__)
print("Torch CUDA:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NO GPU")
print("CUDA_HOME:", os.environ.get("CUDA_HOME"))
print("FORCE_CUDA:", os.environ.get("FORCE_CUDA"))
print("CUDA_VISIBLE_DEVICES:", os.environ.get("CUDA_VISIBLE_DEVICES"))
print("PYOPENGL_PLATFORM:", os.environ.get("PYOPENGL_PLATFORM"))
PY