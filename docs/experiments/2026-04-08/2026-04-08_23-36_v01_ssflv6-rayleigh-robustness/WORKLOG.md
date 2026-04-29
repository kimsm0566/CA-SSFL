# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `SPEC` 고정 후 1차 구현 진행중
- 현재 blocker: 현재 세션은 Docker daemon 권한이 없어 컨테이너 실행 검증 불가
- 다음 구체 행동: spreading 구현 반영 후 Docker GPU 경로 기준 문서와 스크립트 정리

## 로그

- 일시: `2026-04-08 23:36 KST`
- 수행 내용:
  - `Rayleigh robustness` 개선 시도에 대한 `PLAN.md` 작성
  - 사용자 승인에 따라 `접근 A 단독`으로 범위 축소
  - 실험 파라미터를 `beta=0.01`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`로 고정
  - 모든 실험을 Docker GPU 경로에서 수행하도록 정책 업데이트 시작
- 변경한 파일:
  - `docs/experiments/2026-04-08_23-36_v01_ssflv6-rayleigh-robustness/PLAN.md`
  - `docs/experiments/ACTIVE_PLAN.md`
  - `docs/experiments/2026-04-08_23-36_v01_ssflv6-rayleigh-robustness/SPEC.md`
- 실행한 명령어:
  - `which mpiexec || true`
  - Python import checks for `mpi4py`, `torch`
- 생성된 산출물:
  - 새 실험 폴더 및 계획/스펙 문서
- 관찰:
  - `docker compose` 클라이언트는 있으나 Docker daemon socket 접근 권한이 현재 세션에 없음
- 결정:
  - `K` 선택 정책은 유지하고, 선택된 활성 feature에만 spreading을 적용
  - 실험 명령은 이후 Docker form으로만 기록

- 일시: `2026-04-08 23:51 KST`
- 수행 내용:
  - Docker image build 완료
  - 컨테이너 내부 `check-gpu` 통과 확인
  - `semantic_spreading_enable=1` 설정으로 1-round Rayleigh smoke 실행
  - 평가 경로의 `indices` 처리와 Rayleigh 채널 입력 shape 문제를 수정
- 변경한 파일:
  - `src/utils/eval.py`
  - `src/models/model.py`
  - `src/utils/trainer.py`
  - `src/utils/option.py`
  - `src/run_exp_main.py`
- 실행한 명령어:
  - `sudo docker compose build`
  - `sudo docker compose run --rm sfl-semantic check-gpu`
  - `sudo docker compose run --rm sfl-semantic run-exp --dataset cifar10 --algorithm SSFLv6 --model_type resnetv2 --channel_type rayleigh --n_clients 2 --n_client_data 10 --batch_size 10 --n_epochs 1 --n_rounds 1 --compressed_dim 4096 --beta 0.01 --pruning_threshold 1.0 --film_max_t 0.7 --film_min_t 0.4 --semantic_spreading_enable 1 --result_path /workspace/tmp/2026-04-08-rayleigh-spreading-smoke --seed 0`
- 생성된 산출물:
  - `/workspace/tmp/2026-04-08-rayleigh-spreading-smoke`
- 관찰:
  - `check-gpu` 결과 `cuda_available=True`, `device_0=NVIDIA GeForce RTX 4070 SUPER`
  - smoke는 학습 1 round와 multi-SNR 평가까지 종료됨
- 결정:
  - Docker GPU 경로는 현재 머신에서 실사용 가능
  - 이후 baseline/candidate 비교도 동일 경로로 진행

- 일시: `2026-04-09 00:41 KST`
- 수행 내용:
  - exploratory single-seed `seed=0` 비교 3종 완료
  - 조건:
    - `baseline`: `semantic_spreading_enable=0`, `snr_adaptive_beta_enable=0`
    - `A 단독`: `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=0`
    - `A + SNR-adaptive beta`: `semantic_spreading_enable=1`, `snr_adaptive_beta_enable=1`
  - 결과를 바탕으로 후속 matched 비교 범위를 `baseline vs A+SNR-adaptive beta`의 `3-seed` 비교로 재고정
- 실행한 명령어:
  - `sudo docker compose run --rm sfl-semantic ... --semantic_spreading_enable 1 --snr_adaptive_beta_enable 0 --seed 0`
  - `sudo docker compose run --rm sfl-semantic ... --semantic_spreading_enable 1 --snr_adaptive_beta_enable 1 --seed 0`
- 생성된 산출물:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-seq-full/.../semantic_spreading_0/snr_adaptive_beta_0/.../seed_0.npz`
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-seq-full/.../semantic_spreading_1/snr_adaptive_beta_0/.../seed_0.npz`
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-rayleigh-seq-full/.../semantic_spreading_1/snr_adaptive_beta_1/.../seed_0.npz`
- 관찰:
  - `A 단독`은 `seed=0`에서 baseline보다 약화
  - `A + SNR-adaptive beta`는 `seed=0`에서 baseline과 `A 단독` 모두를 상회
- 결정:
  - 후속 matched 비교는 `baseline vs A+SNR-adaptive beta`, `seed in {0,1,2}`
  - 기존 `seed=0` 결과는 재사용하고 `seed=1,2`만 추가 실행

## 열린 질문

- DCT spreading만으로 충분한지, 이후 power weighting 결합이 필요한지

## 남은 다음 단계

- `seed=1,2`에 대해 baseline vs candidate 추가 실행
- `seed=0,1,2` 기준 평균/분산 비교
- 결과를 ledger와 최종 요약에 반영
