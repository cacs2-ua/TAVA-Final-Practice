# Dockerfile for SHAPY runtime
# Runtime target requested by the project:
#   Ubuntu 18.04 + CUDA 10.2 + cuDNN 7 + Python 3.8 + PyTorch 1.7.1/cu102
#
# Build from WSL Ubuntu 20.04, but execute SHAPY inside this container.

FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

SHELL ["/bin/bash", "-lc"]

RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Python 3.8 via Miniconda avoids relying on Ubuntu 18.04 system Python packages.
ENV CONDA_DIR=/opt/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-py38_4.12.0-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p ${CONDA_DIR} \
    && rm /tmp/miniconda.sh

ENV PATH=${CONDA_DIR}/bin:${PATH}

RUN conda config --set always_yes yes --set changeps1 no \
    && conda create -n shapy python=3.8 pip \
    && conda clean -afy

ENV PATH=${CONDA_DIR}/envs/shapy/bin:${CONDA_DIR}/bin:${PATH}
ENV CONDA_DEFAULT_ENV=shapy

# Keep pip/setuptools conservative because SHAPY is an older research repo.
RUN python -m pip install --upgrade "pip<24" "setuptools<60" wheel ninja cython

# Install the CUDA 10.2 PyTorch wheel explicitly.
# Do not rely on requirements.txt for torch/torchvision, because the official
# requirements omit the +cu102 local wheel suffix.
RUN python -m pip install \
    torch==1.7.1+cu102 \
    torchvision==0.8.2+cu102 \
    -f https://download.pytorch.org/whl/torch_stable.html

# Jupyter kernel for VS Code notebooks.
RUN python -m pip install ipykernel jupyterlab notebook ipywidgets \
    && python -m ipykernel install --name shapy --display-name "Python 3.8 (SHAPY Docker)"

WORKDIR /workspace

ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6"
ENV PYOPENGL_PLATFORM=egl
ENV SHAPY_DIR=/workspace/shapy
ENV PYTHONPATH=/workspace/shapy:/workspace/shapy/attributes

EXPOSE 8888

CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=shapy --NotebookApp.password=''"]
