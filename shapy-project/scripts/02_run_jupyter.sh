#!/usr/bin/env bash
set -euo pipefail

# Run this in WSL Ubuntu 20.04 from the root of this package.
# Jupyter will be exposed at:
#   http://127.0.0.1:8888/lab?token=shapy

docker compose up shapy
