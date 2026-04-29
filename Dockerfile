FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/workspace/src \
    MPLBACKEND=Agg \
    WANDB_MODE=offline \
    OMPI_ALLOW_RUN_AS_ROOT=1 \
    OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    ca-certificates \
    git \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libopenmpi-dev \
    libsm6 \
    libxext6 \
    libxrender1 \
    openmpi-bin \
    python-is-python3 \
    python3 \
    python3-dev \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY docker/requirements.txt /tmp/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --index-url https://download.pytorch.org/whl/cu121 \
    torch==2.4.0 torchvision==0.19.0 && \
    python -m pip install --no-binary=mpi4py mpi4py==4.0.3 && \
    python -m pip install -r /tmp/requirements.txt

COPY docker/check-gpu.sh /usr/local/bin/check-gpu
COPY docker/run-mpi.sh /usr/local/bin/run-mpi
COPY docker/run-exp.sh /usr/local/bin/run-exp
RUN chmod +x /usr/local/bin/check-gpu /usr/local/bin/run-mpi /usr/local/bin/run-exp

COPY AGENTS.md /workspace/AGENTS.md
COPY docs /workspace/docs
COPY src /workspace/src

WORKDIR /workspace/src

CMD ["bash"]
