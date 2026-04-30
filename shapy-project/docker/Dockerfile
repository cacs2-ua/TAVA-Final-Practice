FROM pytorch/pytorch:1.8.1-cuda10.2-cudnn7-devel

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

SHELL ["/bin/bash", "-lc"]

# ---------------------------------------------------------------------
# 1. Robust pip settings
# ---------------------------------------------------------------------
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=20
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# ---------------------------------------------------------------------
# 2. System packages required by SHAPY, OpenCV, rendering and compilation
# ---------------------------------------------------------------------
RUN rm -f /etc/apt/sources.list.d/cuda.list \
    && rm -f /etc/apt/sources.list.d/nvidia-ml.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        git \
        wget \
        curl \
        ca-certificates \
        unzip \
        vim \
        nano \
        pkg-config \
        ffmpeg \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libegl1-mesa \
        libgles2-mesa-dev \
        libosmesa6-dev \
        libopenblas-dev \
        liblapack-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------
# 3. Create isolated Python 3.8 environment
# ---------------------------------------------------------------------
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:${PATH}

RUN conda config --set always_yes yes \
    && conda config --set changeps1 no \
    && conda create -n shapy python=3.8 pip -y \
    && conda clean -afy

ENV PATH=${CONDA_DIR}/envs/shapy/bin:${CONDA_DIR}/bin:${PATH}
ENV CONDA_DEFAULT_ENV=shapy

# ---------------------------------------------------------------------
# 4. Install build tools with pip
# ---------------------------------------------------------------------
RUN python -m pip install \
    --timeout 1000 \
    --retries 20 \
    --upgrade \
    "pip<24" \
    "setuptools<60" \
    wheel \
    ninja \
    cython

# ---------------------------------------------------------------------
# 5. Install PyTorch 1.8.1 + CUDA 10.2 using official pip wheels
# This avoids the Conda dependency solver stall.
# ---------------------------------------------------------------------
RUN python -m pip install \
    --timeout 1000 \
    --retries 20 \
    torch==1.8.1+cu102 \
    torchvision==0.9.1+cu102 \
    torchaudio==0.8.1 \
    -f https://download.pytorch.org/whl/torch_stable.html

# ---------------------------------------------------------------------
# 6. Install Jupyter tools
# ---------------------------------------------------------------------
RUN python -m pip install \
    --timeout 1000 \
    --retries 20 \
    ipykernel \
    notebook \
    jupyterlab \
    ipywidgets

RUN python -m ipykernel install \
    --name shapy \
    --display-name "Python 3.8 (SHAPY Docker)"

# ---------------------------------------------------------------------
# 7. Verify Python and PyTorch at build time
# GPU may be unavailable during build. That is normal.
# Runtime GPU is tested later with docker --gpus all.
# ---------------------------------------------------------------------
RUN python - <<'PY'
import sys
import torch

print("Python:", sys.version)
print("Torch version:", torch.__version__)
print("Torch CUDA runtime:", torch.version.cuda)
print("CUDA available during build:", torch.cuda.is_available())

assert sys.version_info.major == 3
assert sys.version_info.minor == 8
assert torch.__version__.startswith("1.8.1"), torch.__version__
assert torch.version.cuda == "10.2", torch.version.cuda
PY

# ---------------------------------------------------------------------
# 8. SHAPY runtime environment
# ---------------------------------------------------------------------
WORKDIR /workspace

ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV FORCE_CUDA=1
ENV CUDA_VISIBLE_DEVICES=0
ENV TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6"
ENV PYOPENGL_PLATFORM=egl
ENV SHAPY_DIR=/workspace/shapy
ENV PYTHONPATH=/workspace/shapy:/workspace/shapy/attributes

EXPOSE 8888

CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=shapy --NotebookApp.password=''"]
