# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `완료`
- 현재 blocker: 없음
- 다음 구체 행동: GPU Docker runtime을 baseline 재현 및 후속 연구 실험의 기본 실행 경로로 사용

## 로그

- 일시: `2026-03-29 20:01 KST`
- 수행 내용:
  - `PLAN.md` 작성 및 사용자 승인 반영
  - 호스트 GPU 및 Docker runtime 상태 점검
  - `nvidia-container-toolkit` 설치 여부와 Docker daemon 반영 상태 확인
  - 표준 CUDA 컨테이너로 `nvidia-smi` 성공 확인
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-01_v01_docker-gpu-runtime/PLAN.md`
  - `docs/experiments/2026-03-29_20-01_v01_docker-gpu-runtime/SPEC.md`
  - `docs/experiments/2026-03-29_20-01_v01_docker-gpu-runtime/WORKLOG.md`
- 실행한 명령어:
  - `docker info | rg -i "runtimes|default runtime|nvidia"`
  - `docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu20.04 nvidia-smi`
- 생성된 산출물:
  - 없음
- 관찰:
  - `nvidia` runtime이 Docker에 등록됨
  - CUDA 테스트 컨테이너에서 GPU 접근 성공
- 결정:
  - GPU 전용 runtime 정비를 계속 진행

- 일시: `2026-03-29 20:15 KST`
- 수행 내용:
  - `Dockerfile`을 CUDA 베이스 이미지 + cu121 PyTorch 기준으로 변경
  - `docker-compose.yml`에 GPU access 기본 설정 추가
  - `check-gpu` preflight 스크립트 추가
  - `docs/DOCKER.md`를 GPU 전용 실행 기준으로 갱신
  - GPU 이미지 빌드 수행
  - `check-gpu` 통과 확인
  - 최소 MPI smoke run 수행
- 변경한 파일:
  - `Dockerfile`
  - `docker-compose.yml`
  - `docker/check-gpu.sh`
  - `docs/DOCKER.md`
- 실행한 명령어:
  - `docker compose build`
  - `docker compose run --rm sfl-semantic check-gpu`
  - `docker compose run --rm sfl-semantic run-exp --dataset=mnist --algorithm=SSFLv6 --channel_type=awgn --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --compressed_dim=4096 --result_path=/workspace/tmp/docker-gpu-smoke-results --seed=0`
- 생성된 산출물:
  - `tmp/docker-gpu-smoke-results/.../seed_0.npz`
  - `tmp/docker-gpu-smoke-results/.../seed_0_server.log`
  - `tmp/docker-gpu-smoke-results/.../seed_0_client_*.log`
- 관찰:
  - 컨테이너 내부 `torch.cuda.is_available()`가 `True`
  - GPU 이름이 `NVIDIA GeForce RTX 4070 SUPER`로 출력됨
  - smoke run 로그에 `device=device(type='cuda', index=0)` 확인
  - MPI 실행이 종료 코드 `0`으로 완료됨
- 결정:
  - GPU Docker runtime 정비를 성공으로 기록

## 열린 질문

- 단일 GPU에서 여러 MPI rank가 `cuda:0`를 공유하는 구조를 언제까지 허용할지
- 멀티 GPU 또는 rank별 device policy를 후속 하네스 개선 대상으로 둘지

## 남은 다음 단계

- baseline reproduction 실험에서 이 GPU runtime을 실제 기본 실행 경로로 사용
- 필요 시 rank별 device policy와 추가 smoke case를 후속 시도로 분리
