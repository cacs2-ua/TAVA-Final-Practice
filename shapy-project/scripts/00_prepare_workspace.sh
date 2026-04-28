#!/usr/bin/env bash
set -euo pipefail

# Run this in WSL Ubuntu 20.04 from the root of this package.
# It creates the mounted workspace and clones SHAPY if it is not already there.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="${ROOT_DIR}/workspace"
SHAPY_DIR="${WORKSPACE_DIR}/shapy"

mkdir -p "${WORKSPACE_DIR}"

if [ ! -d "${SHAPY_DIR}/.git" ]; then
  git clone https://github.com/muelea/shapy.git "${SHAPY_DIR}"
else
  echo "[OK] SHAPY repository already exists: ${SHAPY_DIR}"
fi

mkdir -p "${SHAPY_DIR}/data/body_models/smpl"
mkdir -p "${SHAPY_DIR}/data/body_models/smplx"
mkdir -p "${SHAPY_DIR}/samples/images"
mkdir -p "${SHAPY_DIR}/samples/openpose"

echo
echo "[OK] Workspace prepared at: ${WORKSPACE_DIR}"
echo
echo "Manual files still required because of license restrictions:"
echo "  1) SHAPY data: ${SHAPY_DIR}/data/shapy_data.zip or run ${SHAPY_DIR}/data/download_data.sh inside the container."
echo "  2) SMPL-X model files:"
echo "     ${SHAPY_DIR}/data/body_models/smplx/SMPLX_NEUTRAL.npz"
echo "     ${SHAPY_DIR}/data/body_models/smplx/SMPLX_FEMALE.npz"
echo "     ${SHAPY_DIR}/data/body_models/smplx/SMPLX_MALE.npz"
echo "  3) Optional SMPL model files if you need SMPL-topology measurements:"
echo "     ${SHAPY_DIR}/data/body_models/smpl/SMPL_NEUTRAL.pkl"
echo "     ${SHAPY_DIR}/data/body_models/smpl/SMPL_FEMALE.pkl"
echo "     ${SHAPY_DIR}/data/body_models/smpl/SMPL_MALE.pkl"
