# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `완료`
- 현재 blocker: `없음`
- 다음 구체 행동: 결과 요약 및 사용자 보고

## 로그

### 항목 템플릿

- 일시: `YYYY-MM-DD HH:MM TZ`
- 수행 내용:
- 변경한 파일:
- 실행한 명령어:
- 생성된 산출물:
- 관찰:
- 결정:

- 일시: `2026-03-30 00:18 KST`
- 수행 내용: `_run_clientv6`와 `FiLMChannelAwareEncoder` 현재 상태를 읽고 실험 폴더와 계획 문서를 생성
- 변경한 파일:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/PLAN.md`
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/SPEC.md`
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/WORKLOG.md`
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/RESULT.md`
- 실행한 명령어:
  - `rg -n "def _run_clientv6|class FiLMChannelAwareEncoder|dynamic_threshold|kl_mean_batch|vib_mask" src/utils/trainer.py src/models/model.py`
  - `sed -n '760,980p' src/utils/trainer.py`
  - `sed -n '340,700p' src/models/model.py`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/`
- 관찰:
  - `_run_clientv6`는 현재 샘플별 sparse 전송, adaptive beta, dynamic scale 보상을 사용하는 경로
  - `FiLMChannelAwareEncoder`는 현재 `2x2` 경량형이 아니라 `8x8/4096` active 구현이 남아 있음
- 결정:
  - 코드 차이를 먼저 사용자에게 설명하고 같은 작업트리 상태로 seed `2` full rerun 진행

- 일시: `2026-03-30 00:20 KST`
- 수행 내용: Docker GPU 경로에서 `SSFLv6 seed=2` full `200`라운드 재실행
- 변경한 파일:
  - 없음
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/full`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/full/`
- 관찰:
  - round `200` 결과는 `Acc 42.19%`, `Total comm 30541.49 MB`, `Total data comm 21146.86 MB`, `Total model comm 9394.63 MB`
  - round `200` 수치가 직전 canonical rerun과 동일함
  - late-round active ratio도 old raw `seed_2`보다 훨씬 높음
- 결정:
  - `_run_clientv6` 변경만으로는 old raw `seed_2` 재현 실패
  - 현재 active `FiLMChannelAwareEncoder`가 여전히 `8x8/4096` 구조라 encoder 쪽이 주된 차이로 남음

## 열린 질문

- `FiLMChannelAwareEncoder`를 실제 old `2x2` 경량형으로 바꾸면 old raw와 가까워지는지

## 남은 다음 단계

- active encoder를 old `2x2` 경량형으로 실제 교체한 뒤 동일 조건 재실행
- `_run_clientv6`와 encoder 영향을 분리한 진단 실행
