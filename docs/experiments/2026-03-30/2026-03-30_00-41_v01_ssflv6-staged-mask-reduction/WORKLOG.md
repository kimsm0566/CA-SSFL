# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `1차 검증 완료`
- 현재 blocker: `없음`
- 다음 구체 행동: `beta=0.00075`를 `seed 1,3,4`로 확장해 single-seed candidate improvement인지 확인

## 로그

### 항목 템플릿

- 일시: `YYYY-MM-DD HH:MM TZ`
- 수행 내용:
- 변경한 파일:
- 실행한 명령어:
- 생성된 산출물:
- 관찰:
- 결정:

- 일시: `2026-03-30 00:41 KST`
- 수행 내용: staged mask reduction 실험 폴더와 계획 문서 생성
- 변경한 파일:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/PLAN.md`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/SPEC.md`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/WORKLOG.md`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/RESULT.md`
- 실행한 명령어:
  - `date`
  - template 파일 조회
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/`
- 관찰:
  - step 1은 현재 server/decoder 제약 때문에 샘플별 indices 전체가 아니라 batch union indices 방식이 필요함
- 결정:
  - stage 1 구현을 union indices 방식으로 진행

- 일시: `2026-03-30 00:44 KST`
- 수행 내용: stage 1 samplewise-union mask 구현 및 서버 호환 patch 후 `20`라운드 검증
- 변경한 파일:
  - `src/utils/trainer.py`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=20 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage1-samplewise-union-rerun`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage1-samplewise-union-rerun/`
- 관찰:
  - stage 1 round `20`: `Acc 26.36%`, `Total comm 5374.99 MB`, `Total data comm 4435.52 MB`, `Data 197.38 MB/round`
  - baseline round `20`: `Acc 25.14%`, `Total comm 3606.33 MB`, `Total data comm 2666.86 MB`, `Data 118.46 MB/round`
  - client 로그의 `Active(avg)`는 줄었지만 `Union`이 대체로 `30~50%`까지 커졌고, server `avg_active_indices`도 `1462.48`로 baseline `573.61`보다 크게 증가
- 결정:
  - stage 1은 통신량 절감 실패
  - union indices 방식은 현재 batch size `100`에서 전송 폭을 오히려 키우므로 채택하지 않음
  - 다음은 stage 1을 되돌리고 stage 2 작은 FiLM gate로 진행

- 일시: `2026-03-30 00:49 KST`
- 수행 내용: stage 1 변경 revert 후 stage 2 작은 FiLM gate 적용 및 `20`라운드 검증
- 변경한 파일:
  - `src/utils/trainer.py`
  - `src/models/model.py`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py src/models/model.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=20 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage2-small-film-gate`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage2-small-film-gate/`
- 관찰:
  - stage 2 round `20`: `Acc 22.87%`, `Total comm 4061.61 MB`, `Total data comm 3484.96 MB`, `Total model comm 576.65 MB`
  - baseline round `20`: `Acc 25.14%`, `Total comm 3606.33 MB`, `Total data comm 2666.86 MB`, `Total model comm 939.46 MB`
  - `model comm`는 크게 감소했지만 `avg_active_indices 772.13`과 `Data 159.45 MB/round`가 여전히 baseline보다 큼
- 결정:
  - stage 2는 model comm 절감 효과는 있으나 overall trade-off는 baseline보다 나쁨
  - stage 2도 채택하지 않음
  - 다음은 stage 2를 되돌리고 baseline 위에서 `beta`만 상향

- 일시: `2026-03-30 01:09 KST`
- 수행 내용: 비교 기준 문서와 실험 스펙을 `20`라운드 trend가 아니라 `200`라운드 full 비교 기준으로 업데이트
- 변경한 파일:
  - `docs/evals/EVAL_PROTOCOL.md`
  - `docs/experiments/README.md`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/PLAN.md`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/SPEC.md`
- 실행한 명령어:
  - `sed -n ... docs/evals/EVAL_PROTOCOL.md`
  - `sed -n ... docs/experiments/README.md`
- 생성된 산출물:
  - `없음`
- 관찰:
  - 짧은 trend run은 smoke/debug에는 유용하지만 candidate promotion 또는 rejection 근거로 쓰기 어렵다
- 결정:
  - 이 시도의 stage 1, 2, 3 비교는 모두 `seed=2`, `200`라운드 full run으로 다시 수행

- 일시: `2026-03-30 01:11 KST`
- 수행 내용: stage 1 samplewise-union mask를 다시 적용해 full `200`라운드 재실행
- 변경한 파일:
  - `src/utils/trainer.py`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage1-samplewise-union-full200`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage1-samplewise-union-full200/`
- 관찰:
  - round `200`: `Acc 45.82%`, `Total comm 39875.66 MB`, `Total data comm 30481.03 MB`, `Total model comm 9394.63 MB`
  - baseline 대비 accuracy는 올랐지만 `data comm`가 크게 증가했다
  - round `200 Breakdown` 기준 `avg_active_indices 635.21`, `Data 91.85 MB/round`, `Model 46.97 MB/round`
- 결정:
  - stage 1은 full `200`에서도 communication-performance trade-off 기준 실패
  - union indices 방식은 accuracy 향상은 있지만 누적 통신량 증가가 너무 커 미채택
  - stage 1 변경은 다시 revert

- 일시: `2026-03-30 01:19 KST`
- 수행 내용: baseline client 로직으로 복귀 후 stage 2 작은 FiLM gate를 적용해 full `200`라운드 재실행
- 변경한 파일:
  - `src/utils/trainer.py`
  - `src/models/model.py`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py src/models/model.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage2-small-film-gate-full200`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage2-small-film-gate-full200/`
- 관찰:
  - round `200`: `Acc 42.54%`, `Total comm 33109.13 MB`, `Total data comm 27342.62 MB`, `Total model comm 5766.50 MB`
  - `model comm`는 baseline보다 크게 감소했지만 `data comm` 증가폭이 더 커서 total comm가 baseline보다 높았다
  - round `200 Breakdown` 기준 `avg_active_indices 626.49`, `Data 129.38 MB/round`, `Model 28.83 MB/round`
- 결정:
  - stage 2는 model comm reduction 후보로는 의미가 있으나 current trade-off 기준 미채택
  - stage 2 encoder 변경은 다시 revert

- 일시: `2026-03-30 01:28 KST`
- 수행 내용: baseline 구조를 유지하고 `beta=0.00075`만 올려 full `200`라운드 재실행
- 변경한 파일:
  - `src/models/model.py`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py src/models/model.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.00075 --pruning_threshold=1.0 --major_percent=0.7 --seed=2 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage3-beta-00075-full200`
- 생성된 산출물:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage3-beta-00075-full200/`
- 관찰:
  - round `200`: `Acc 42.71%`, `Total comm 28950.00 MB`, `Total data comm 19555.37 MB`, `Total model comm 9394.63 MB`
  - baseline 대비 total comm는 `-1591.49 MB`, accuracy는 `+0.52%p`, `Test SNR 12dB`는 `42.32% -> 44.19%`
  - round `200 Breakdown` 기준 `avg_active_indices 428.77`, `Data 88.55 MB/round`, `Model 46.97 MB/round`
- 결정:
  - stage 3 `beta=0.00075`는 single-seed matched run 기준 candidate improvement
  - 다만 seed `2` 단일 결과이므로 default promotion은 보류하고 `seed 1,3,4` 확장이 필요함

## 열린 질문

- `beta=0.00075`의 통신량 이득과 accuracy 유지가 `seed 1,3,4`에서도 유지되는가
- `beta=0.00075`가 다른 training SNR 또는 channel setting에서도 같은 방향으로 동작하는가

## 남은 다음 단계

- `SSFLv6 beta=0.00075`를 `seed 1,3,4`로 확장
- 기존 baseline `beta=0.0005`와 seed-matched 비교표 정리
- 필요 시 `beta=0.000625`, `0.001` 사이 추가 sweep 검토
