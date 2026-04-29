# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `진행중`
- 현재 blocker: threshold-only 수정으로 data comm는 거의 복구됐지만 model comm 회귀가 남아 있어 총량 목표를 아직 못 맞춤
- 다음 구체 행동: threshold-only 수정 결과를 기준선으로 고정하고, model comm 상승분의 직접 원인을 더 분해

## 로그

- 일시: `2026-03-29 21:04 KST`
- 수행 내용:
  - 현재 baseline `SSFLv6` 200라운드 로그 확인
  - 과거 참고 로그와 현재 로그의 comm 수치 차이 분해
  - 현재 client state_dict 크기와 round당 model comm의 일치 여부 확인
  - 상위 파라미터 크기 항목 확인
- 변경한 파일:
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/PLAN.md`
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/SPEC.md`
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/WORKLOG.md`
- 실행한 명령어:
  - `tail -n 80 docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/full/.../seed_1_server.log`
  - `rg -n "Round 200\\] Acc: .*Total comm" src/output.log ...`
  - `docker compose run --rm sfl-semantic bash -lc ... state_dict size diagnostic ...`
  - `docker compose run --rm sfl-semantic bash -lc ... top parameter size diagnostic ...`
- 생성된 산출물:
  - 없음
- 관찰:
  - 현재 200라운드 기준:
    - `Total comm 28386.97 MB`
    - `Total data comm 18992.34 MB`
    - `Total model comm 9394.63 MB`
  - 참고 과거 로그 기준:
    - `Total comm 24613.84 MB`
    - `Total data comm 16263.06 MB`
    - `Total model comm 8350.78 MB`
  - 현재 `SSFLv6` client model 한 번 전송 크기는 `2.6096 MB`, round당 `18`회 기준 `46.9731 MB`로 서버 로그와 정확히 맞는다.
  - 가장 큰 단일 state entry는 `semantic_encoder.snr_to_film.2.weight`로 `1.0000 MB`다.
  - `SSFLv6_w_o_film`의 round당 model comm는 `28.6831 MB`로 크게 줄어든다.
- 결정:
  - model comm 증가는 먼저 `FiLM 관련 파라미터 포함 여부/크기`에서 설명 가능성이 높다.
  - 다음 단계는 data comm 상승분을 active ratio와 index overhead 기준으로 분해하는 것이다.

- 일시: `2026-03-29 21:10 KST`
- 수행 내용:
  - 현재 `SSFLv6`에 round별 comm breakdown 로그 추가
  - 5라운드 진단 run 실행
  - 동일 설정의 과거 baseline artifact를 `src/results/`에서 확인
  - 과거/현재 client active ratio 차이 확인
- 변경한 파일:
  - `src/utils/trainer.py`
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=5 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r`
  - `tail -n 60 src/results/.../seed_1_server.log`
  - `sed -n '1,40p' src/results/.../seed_1_client_0.log`
  - `sed -n '1,40p' docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/.../seed_1_client_0.log`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r/...`
- 관찰:
  - 현재 5라운드 진단에서 round당 model comm는 고정 `46.97 MB`다.
  - 현재 5라운드 진단에서 round당 data comm는 `119~123 MB` 수준이다.
  - breakdown 로그 기준 평균 active index는 client-batch당 약 `580~600`이다.
  - 동일 설정의 과거 baseline artifact는 실제로 존재하며 round당 model comm `41.75 MB`, data comm `55~69 MB` 수준이다.
  - 과거 client log에서는 low SNR 구간에서 `Active: 2/4096`, `28/4096`, `57/4096` 같은 매우 희소한 마스크가 보인다.
  - 현재 client log에서는 같은 설정에서도 대체로 `Active: 440~620/4096` 수준으로 유지되어 훨씬 덜 sparse하다.
- 결정:
  - data comm 상승의 1차 원인은 현재 `SSFLv6` 마스크가 과거보다 훨씬 덜 sparse해진 데 있다.
  - model comm 상승도 별도 회귀 항목이며, 두 문제를 분리해서 다뤄야 한다.

- 일시: `2026-03-29 21:14 KST`
- 수행 내용:
  - threshold-only 최소 수정 적용
  - 수정 후 `python -m py_compile src/utils/trainer.py` 검증
  - 수정 후 5라운드 진단 run 재실행
- 변경한 파일:
  - `src/utils/trainer.py`
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/WORKLOG.md`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=5 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r_thresh1_fix`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r_thresh1_fix/...`
- 관찰:
  - threshold-only 수정 후 round당 data comm는 `61.63~68.10 MB`로 내려왔다.
  - 수정 후 breakdown 로그 기준 평균 active index는 client-batch당 약 `298~330`으로 감소했다.
  - round당 model comm는 여전히 `46.97 MB`로 변하지 않았다.
  - 수정 후 round 1 총 통신량은 `114.86 MB`이며, 과거 matched baseline의 총량 범위에는 근접했지만 model comm 차이만큼 여전히 높다.
  - low-SNR client log에서 `Active: 1/4096`, `11/4096`, `42/4096`처럼 과거와 유사한 sparse 패턴이 다시 나타난다.
- 결정:
  - 1번 접근은 data comm 회귀 복구에는 유효하다.
  - 하지만 `<21000 MB @ 200 rounds` 목표는 model comm 회귀가 그대로 남아 있어 threshold-only 수정만으로는 달성 가능성이 낮다.
  - 다음 디버깅 우선순위는 `semantic_encoder.snr_to_film.*`를 중심으로 한 model comm 축소 원인 규명이다.

- 일시: `2026-03-29 21:18 KST`
- 수행 내용:
  - `semantic_encoder.snr_to_film` hidden width를 `64 -> 32`로 줄이는 최소 model comm 후보 적용
  - 수정 후 client `state_dict()` 크기 재계산
  - `model32` 후보 5라운드 진단 run 실행
  - `model32 + stronger threshold` 조합 5라운드 진단 run 추가 실행
  - 두 후보 모두 비승격 판단 후 코드 상태를 threshold-only 기준으로 복원
- 변경한 파일:
  - `src/models/model.py`
  - `src/utils/trainer.py`
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/WORKLOG.md`
- 실행한 명령어:
  - `python -m py_compile src/models/model.py src/utils/trainer.py`
  - `docker compose run --rm sfl-semantic bash -lc ... state_dict size diagnostic ...`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=5 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r_thresh1_model32`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=5 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r_thresh2_model32`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r_thresh1_model32/...`
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/diag_ssflv6_5r_thresh2_model32/...`
- 관찰:
  - `model32` 후보에서 client model 한 번 전송 크기는 `2.109375 MB`, round당 model comm는 `37.96875 MB`로 감소했다.
  - 하지만 `model32 + threshold1` 조합에서는 round당 data comm가 `77.05~83.32 MB`로 다시 상승했다.
  - `model32 + threshold2` 조합에서는 round당 data comm가 `70.00~76.74 MB`까지 내려왔고 round 1 총 통신량은 `108.55 MB`였다.
  - 다만 `model32 + threshold2`의 5라운드 결과는 `round 5 acc 11.40%`, multi-SNR `12dB acc 11.50%`로 같은 길이의 기존 후보보다 성능이 더 약했다.
  - 즉 hidden width 축소는 model comm 자체는 줄였지만, mask 분포를 바꿔 data comm와 초기 정확도를 같이 흔들었다.
- 결정:
  - `model32 + threshold1`은 총 통신량 면에서 threshold-only 기준보다 낫지 않아 비승격한다.
  - `model32 + threshold2`는 통신량은 더 좋아 보이지만 5라운드 기준 정확도 열화가 커서 즉시 승격하지 않는다.
  - 현재 코드 기준선은 `threshold-only` 수정 상태로 유지하고, 다음은 FiLM 파라미터 축소보다 덜 공격적인 model comm 후보를 설계한다.

## 열린 질문

- 과거 matched baseline의 `41.75 MB/round model comm`를 만든 정확한 모델 파라미터 구성이 현재 코드와 어떻게 다른가?
- model comm 목표를 줄이기 위해 FiLM 경로를 축소할 수 있는가, 아니면 baseline 정의가 이미 달라진 것인가?

## 남은 다음 단계

- 현재 `SSFLv6` client state_dict에서 `semantic_encoder.snr_to_film.*` 항목의 기여도를 기준으로 model comm 회귀를 더 분해
- 과거 matched baseline과 현재 코드의 FiLM 관련 구조 차이를 확인
- hidden width 축소보다 덜 공격적인 model comm 후보를 1개 더 설계해 짧은 진단 run으로 검증
