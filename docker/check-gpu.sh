#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import torch

print(f"cuda_available={torch.cuda.is_available()}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not available inside the container")

print(f"device_count={torch.cuda.device_count()}")
for idx in range(torch.cuda.device_count()):
    print(f"device_{idx}={torch.cuda.get_device_name(idx)}")
PY
