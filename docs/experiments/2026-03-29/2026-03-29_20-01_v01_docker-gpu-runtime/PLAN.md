# 실험 계획

## 메타데이터

- 실험 id: `2026-03-29_20-01_v01_docker-gpu-runtime`
- 초안 일시: `2026-03-29 20:01 KST`
- 상태: `승인`
- 담당자: `Codex + 사용자`

## 목표

Docker 기반 실행 경로에서 `src/run_exp_main.py`가 실제로 GPU를 사용하도록 런타임을 정비한다.

성공 기준은 다음과 같다.

- 컨테이너 내부에서 `torch.cuda.is_available()`가 `True`여야 한다.
- 최소 smoke run에서 로그상 `device(type='cuda')`가 확인되어야 한다.
- MPI 기반 실행 래퍼(`run-exp`)가 GPU 환경에서도 동작해야 한다.

## 지금 하는 이유

- 현재 연구 하네스는 Docker 기반 실행은 가능하지만 CPU 경로만 검증되었다.
- 이 저장소의 실험은 학습 루프와 SNR 평가가 길기 때문에 실제 연구 생산성을 위해 GPU 실행 경로가 필요하다.
- 지금 상태로는 대규모 실험 설계 이전에 실행 인프라가 병목이다.

현재까지 확인된 사실:

- 호스트 머신에는 NVIDIA GPU가 존재한다.
- `nvidia-container-toolkit`와 `nvidia-container-runtime` 바이너리는 설치되어 있다.
- 현재 Docker 런타임에는 `nvidia` runtime이 보이지 않는다.
- `/etc/docker/daemon.json`이 비어 있어 toolkit이 Docker daemon에 등록되지 않은 상태로 보인다.
- 현재 이미지 빌드는 CPU용 PyTorch를 설치하고 있다.
- 현재 compose 설정에는 GPU device reservation이 없다.

## 제안 변경사항

- 대상 코드 경로:
  - `Dockerfile`
  - `docker-compose.yml`
  - `docker/run-exp.sh`
  - `docs/DOCKER.md`
- 의도한 동작 변화:
  - 컨테이너가 GPU를 인식하고 PyTorch CUDA 경로로 실행되도록 한다.
  - 실행 전에 GPU 가용성을 빠르게 확인할 수 있는 preflight 경로를 둔다.
  - 사용자에게 필요한 호스트 전제조건을 문서화한다.
- 유지할 조건:
  - `src/`의 학습 알고리즘 로직은 GPU 지원 자체와 무관한 한 최소 변경 원칙을 유지한다.
  - 보호된 데이터/결과/체크포인트 디렉터리는 수정하지 않는다.
  - 결과 저장은 필요 시 임시 경로 또는 새 artifact 경로를 사용한다.

## 후보 접근법

- 접근 A:
  - 현재 `python:3.9-slim` 기반 이미지를 유지하고 CUDA용 PyTorch wheel만 교체한다.
  - 장점: 변경 폭이 작다.
  - 단점: CUDA 런타임 라이브러리와 호환성 이슈가 날 가능성이 높고, 재현성이 약하다.

- 접근 B:
  - NVIDIA CUDA runtime 계열 베이스 이미지를 사용하고, 해당 환경에 맞는 GPU PyTorch를 설치한다.
  - `docker-compose.yml`에 GPU 예약을 추가하고, 실행 문서에 호스트 prerequisite를 명시한다.
  - 장점: 가장 표준적이고 디버깅이 쉽다.
  - 단점: 이미지가 커지고 빌드 시간이 늘어난다.

- 접근 C:
  - CPU 서비스와 GPU 서비스를 분리한 compose 구성을 만든다.
  - 장점: CPU fallback과 GPU path를 명확히 분리할 수 있다.
  - 단점: 지금 단계에서는 문서와 운영 복잡도가 커진다.

- 우선 접근법과 그 이유:
  - 접근 B를 우선한다.
  - 이유: 현재 문제는 “GPU가 전혀 안 보이는 상태”라서, 작은 패치보다 표준 CUDA 런타임 기반으로 명시적으로 정리하는 편이 신뢰성이 높다.
  - 단, CPU smoke 경로를 완전히 버리지는 않고, 필요 시 문서에서 CPU fallback을 별도로 안내한다.

## 계획된 검증

- 스모크 체크:
  - `docker compose config`
  - 컨테이너 내부 `python -c "import torch; print(torch.cuda.is_available())"`
  - 컨테이너 내부 `python -c "import torch; print(torch.cuda.get_device_name(0))"` if CUDA available
  - 최소 MPI smoke run:
    - dataset: `mnist`
    - algorithm: `SSFLv6`
    - `n_clients=2`
    - `n_client_data=10`
    - `batch_size=10`
    - `n_epochs=1`
    - `n_rounds=1`
    - 결과 경로는 보호 영역 밖 임시 경로 사용
- 비교 대상:
  - 목표는 성능 비교가 아니라 GPU 실행 인프라 검증
- 예상 산출물 경로:
  - 문서: `docs/DOCKER.md`
  - 임시 실행 산출물: `/workspace/tmp/docker-gpu-smoke-results`

## 리스크와 열린 질문

- 기술적 리스크:
  - 호스트에 NVIDIA Container Toolkit이 없으면 컨테이너 수정만으로는 GPU가 보이지 않는다.
  - CUDA/PyTorch 버전 조합이 맞지 않으면 이미지 빌드 또는 import 단계에서 실패할 수 있다.
  - MPI 다중 프로세스와 GPU 장치 매핑이 엉키면 단일 GPU에서 비효율이 생길 수 있다.

- 평가상 리스크:
  - 이 작업은 하네스 정비이지 알고리즘 개선이 아니다.
  - GPU 동작 성공을 성능 개선으로 해석하면 안 된다.

- 검토가 필요한 질문:
  - 이 실험 범위에 호스트의 NVIDIA Container Toolkit 설치 가이드까지 포함할지?
  - 기본 compose를 GPU 전용으로 바꿀지, 아니면 GPU override/profile을 둘지?
  - 단일 GPU 기준에서 MPI 프로세스 전체가 `cuda:0`를 공유하는 현재 코드를 우선 허용할지, rank별 device policy까지 바로 손볼지?

## 사용자 검토 메모

- 피드백:
  - CPU와의 비교는 이번 범위에서 필요 없다.
  - 기본 방향은 GPU 전용 운영이다.
  - `sudo nvidia-ctk runtime configure --runtime=docker` 적용 후 daemon 재시작 완료.
- 합의된 결정:
  - Docker 경로는 GPU 기준으로 정리한다.
  - CPU fallback은 이번 작업의 우선순위가 아니다.
  - plan 승인이 되었으므로 `SPEC.md` 기준으로 실행한다.
- 남은 쟁점:
  - Docker daemon에 `nvidia` runtime을 어떤 방식으로 등록할지
  - 이 저장소에서 GPU 전용 compose를 기본으로 둘지, 문서상 prerequisite로만 둘지

## 실행 게이트

- 구현 시작 가능?: `예`
- 아니라면 먼저 명확히 할 점:
  - 없음. 다만 Docker daemon의 `nvidia` runtime 미등록은 실행 단계에서 해결이 필요하다.
