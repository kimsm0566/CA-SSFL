# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-29_20-01_v01_docker-gpu-runtime`
- 시작 일시: `2026-03-29 20:15 KST`
- 상태: `완료`
- 담당자: `Codex + 사용자`

## 요약

이 시도는 연구 알고리즘을 바꾸는 작업이 아니라, Docker 기반 실행 하네스를 GPU 전용으로 정비하는 작업이다. 호스트의 NVIDIA runtime이 Docker에서 사용 가능해진 상태를 전제로, 저장소의 이미지 빌드, compose 실행, 문서, 검증 절차를 GPU 기준으로 맞춘다.

## 질문

이 저장소의 Docker 실행 경로가 실제로 GPU를 인식하고, `run_exp_main.py`의 MPI 기반 smoke run을 CUDA 경로로 통과할 수 있는가?

## 가설

Docker 이미지와 compose 설정을 GPU 기준으로 정리하면, 컨테이너 내부에서 `torch.cuda.is_available()`가 `True`가 되고 최소 MPI smoke run에서 `device(type='cuda')`를 확인할 수 있다.

## 기준선

- 기준선 알고리즘: 해당 없음. 이 작업은 인프라 정비다.
- 기준선 설정: 현재 저장소의 CPU-only Docker runtime
- 기준선 산출물 경로: 없음
- 이 비교가 적절한 이유:
  - 이번 작업의 비교 대상은 모델 성능이 아니라 실행 가능성이다.
  - 따라서 canonical accuracy/communication 비교가 아니라 GPU visibility와 smoke success를 본다.

## 고정 조건

- dataset: `mnist`
- partition_type: `iid`
- n_clients: `2`
- n_client_data: `10`
- batch_size: `10`
- n_epochs: `1`
- n_rounds: `1`
- channel_type: `awgn`
- seed_set: `0`
- evaluation_path:
  - `torch.cuda.is_available()` 확인
  - 컨테이너 내부 device 확인
  - `run-exp` 기반 최소 MPI smoke run

## 변경 변수

- 대상 코드 경로:
  - `Dockerfile`
  - `docker-compose.yml`
  - `docker/run-exp.sh`
  - `docs/DOCKER.md`
- 바꾸는 변수:
  - 베이스 이미지와 PyTorch 설치 경로
  - compose GPU reservation
  - GPU preflight 실행 경로
  - 문서화된 실행 방법
- 탐색 범위:
  - GPU 전용 compose 경로
  - 가능한 한 `src/` 알고리즘 로직은 비변경

## 지표

### 주요 지표

- 컨테이너 내부 `torch.cuda.is_available()` 값
- 컨테이너 내부 GPU 장치 식별 성공 여부
- MPI smoke run 성공 여부

### 보조 지표

- 로그상 `device(type='cuda')` 확인
- `docker compose build` 성공 여부
- `docker compose config` 유효성

## 검증 계획

### 스모크 체크

- 명령어:
  - `docker compose config`
  - `docker compose build`
  - `docker compose run --rm sfl-semantic python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"`
  - `docker compose run --rm sfl-semantic run-exp --dataset=mnist --algorithm=SSFLv6 --channel_type=awgn --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --compressed_dim=4096 --result_path=/workspace/tmp/docker-gpu-smoke-results --seed=0`
- 성공 신호:
  - `torch.cuda.is_available()`가 `True`
  - GPU 이름 출력 성공
  - smoke run 로그에서 `device(type='cuda')` 확인
  - 비정상 MPI 종료 없이 종료 코드 `0`

### 매칭 비교

- 명령어:
  - 해당 없음. 이번 작업은 claim-making 비교 실험이 아니다.
- 예상 산출물 경로:
  - `/workspace/tmp/docker-gpu-smoke-results`

### 강건성 후속 검증

- 추가 seed:
  - 이번 범위 밖
- 추가 SNR:
  - 이번 범위 밖
- 추가 channel 설정:
  - 이번 범위 밖

## 승격 기준

다음이 모두 충족되면 GPU Docker runtime 정비를 성공으로 본다.

- Docker가 GPU를 인식한다.
- 컨테이너 내부 PyTorch가 CUDA를 인식한다.
- 최소 MPI smoke run이 종료 코드 `0`으로 완료된다.
- 실행 문서가 실제 동작 경로와 일치한다.

## 중단 기준

다음 중 하나가 발생하면 이번 설계를 중단하고 대안을 검토한다.

- 현재 호스트 드라이버와 호환되는 GPU 이미지 조합을 만들지 못함
- Docker daemon은 GPU를 보지만 PyTorch CUDA import가 안정적으로 실패함
- GPU 지원을 위해 `src/` 알고리즘 로직을 과도하게 훼손해야 함

## 리스크와 교란 요인

- 가능한 교란 요인:
  - Docker image cache
  - 기존 CPU 이미지 잔존
  - MPI 다중 프로세스가 단일 GPU를 공유하는 구조
- 예상 실패 모드:
  - CUDA wheel/런타임 버전 mismatch
  - compose GPU reservation 누락
  - smoke run은 성공하지만 종료 루틴 때문에 non-zero exit
- 결과를 무효화할 수 있는 요소:
  - GPU visibility만 확인하고 실제 `run_exp_main.py`를 안 돌리는 경우
  - 문서와 실제 실행 명령이 어긋나는 경우
