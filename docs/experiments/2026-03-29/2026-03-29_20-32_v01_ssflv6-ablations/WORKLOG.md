# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `진행중`
- 현재 blocker: 현재 사용자 `sunmin`이 `/var/run/docker.sock`에 접근할 수 없어 Docker GPU 실행 불가
- 다음 구체 행동: Docker socket 권한 해소 후 preflight와 smoke test 재개

## 로그

- 일시: `2026-03-29 20:32 KST`
- 수행 내용:
  - `PLAN.md` 작성 및 사용자 피드백 반영
  - Docker GPU 단일 실행기, baseline 포함, 실험별 smoke 선행 원칙 확정
  - `SPEC.md` 작성으로 실행 계약 고정
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/PLAN.md`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/SPEC.md`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - 없음
- 생성된 산출물:
  - 없음
- 관찰:
  - `SSFLv6` ablation 3개는 현재 코드와 스크립트에 이미 정의되어 있다.
- 결정:
  - baseline 포함 4개 설정 모두 Docker GPU 경로에서 smoke 후 full run을 진행한다.

- 일시: `2026-03-29 20:39 KST`
- 수행 내용:
  - Docker GPU preflight 실행 시도
  - Docker daemon 접근 권한 진단
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic check-gpu`
  - `whoami`
  - `id`
  - `ls -l /var/run/docker.sock`
  - `docker version`
  - `sudo -n docker version`
- 생성된 산출물:
  - 없음
- 관찰:
  - 현재 사용자 `sunmin`은 `docker` 그룹에 속해 있지 않다.
  - `/var/run/docker.sock` 권한은 `root:docker` `0660`이다.
  - `docker version`과 `docker compose run` 모두 `permission denied`로 실패했다.
  - `sudo -n` 경로도 비밀번호 요구로 실패했다.
- 결정:
  - Docker socket 권한이 해소되기 전까지 smoke/full run을 진행할 수 없다.

- 일시: `2026-03-29 20:49 KST`
- 수행 내용:
  - Docker GPU preflight 재실행 및 성공 확인
  - baseline `SSFLv6` smoke 1회 실행
  - 실행 후 실제 인자값 검토 중 `snr_db`와 `use_private_SGD`가 스펙과 불일치함을 발견
  - `SPEC.md`를 올바른 고정 조건 기준으로 수정
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/SPEC.md`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic check-gpu`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/smoke`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/smoke/...`
- 관찰:
  - GPU preflight는 성공했다.
  - 첫 baseline smoke는 종료 코드 `0`과 artifact 생성까지는 성공했다.
  - 하지만 실제 실행 인자에서 `snr_db=10`, `use_private_SGD=1`로 찍혀 스펙과 불일치했다.
- 결정:
  - 첫 baseline smoke는 exploratory/invalid로 간주하고, 수정된 스펙으로 baseline smoke를 다시 실행한 뒤 나머지 ablation smoke를 진행한다.

## 열린 질문

- 없음

## 남은 다음 단계

- `docker compose run --rm sfl-semantic check-gpu`
- baseline 및 3개 ablation smoke 실행
- smoke 통과 시 full run 실행
- 결과 취합 후 `RESULT.md`와 `RESULTS_LEDGER.md` 갱신

- 일시: `2026-03-29 20:52 KST`
- 수행 내용:
  - Docker GPU preflight 성공
  - baseline `SSFLv6` smoke 재실행 및 스펙 일치 확인
  - `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta` smoke 성공
  - baseline `SSFLv6` full run seed `1` 시작
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic check-gpu`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/smoke`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_vib --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/SSFLv6_w_o_vib/smoke`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_film --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/SSFLv6_w_o_film/smoke`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_beta --channel_type=rayleigh --partition_type=class --n_clients=2 --n_client_data=10 --batch_size=10 --n_epochs=1 --n_rounds=1 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/SSFLv6_w_o_beta/smoke`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/full`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/smoke/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/SSFLv6_w_o_vib/smoke/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/SSFLv6_w_o_film/smoke/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/SSFLv6_w_o_beta/smoke/...`
- 관찰:
  - 4개 smoke 모두 종료 코드 `0`, `.npz` 저장, 로그 생성까지 확인됐다.
  - smoke에서 `class` 분할 + 극소 데이터로 인해 `data.py` 경고가 있었지만 실행 자체는 끝까지 통과했다.
  - baseline full run seed `1`은 정상적으로 round를 진행 중이다.
- 결정:
  - full sweep는 baseline seed `1` 완료 후 동일 패턴으로 باقي seed와 ablation을 이어간다.

- 일시: `2026-03-29 21:29 KST`
- 수행 내용:
  - comm-debug 중 넣었던 threshold 수정 제거
  - ablation 실험은 원래 threshold 식으로 복귀한 뒤 `seed=1` trend run으로 먼저 다시 실행해 경향 확인하기로 범위 조정
  - `SPEC.md`에 current execution scope 반영
- 변경한 파일:
  - `src/utils/trainer.py`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/SPEC.md`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - 없음
- 생성된 산출물:
  - 없음
- 관찰:
  - 원래 FiLM threshold 식은 `0.5 - (snr_normalized * 0.3)`이다.
- 결정:
  - baseline `SSFLv6`, `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta`를 원래 threshold 기준 `seed=1` trend run으로 재실행한다.

- 일시: `2026-03-29 21:36 KST`
- 수행 내용:
  - 원래 threshold 기준 baseline `SSFLv6` 200라운드 재실행을 단독으로 시작
  - run이 정상 진행되는지 확인
  - 경향 확인 목적에 맞춰 범위를 `n_rounds=20` exploratory trend run으로 축소 결정
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/SPEC.md`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend/SSFLv6/full`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend/SSFLv6/full/...`
- 관찰:
  - 원래 threshold 기준 baseline은 단독 실행 시 정상 진행됐다.
  - round `8` 시점 관찰값은 `Acc 15.48%`, `Total comm 1336.09 MB`, `Data 116.50 MB`, `Model 46.97 MB`였다.
- 결정:
  - 경향 확인이 목적이므로 네 알고리즘 모두 `n_rounds=20`, `seed=1`로 맞춘 exploratory trend run으로 전환한다.

- 일시: `2026-03-29 21:40 KST`
- 수행 내용:
  - 원래 threshold 기준 `n_rounds=20`, `seed=1` exploratory trend run 실행
  - `SSFLv6`, `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta` 순차 실행 완료
  - 각 설정의 round `20` 통신량과 `Test SNR 12dB` 정확도 추출
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=20 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6/full`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_vib --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=20 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6_w_o_vib/full`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_film --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=20 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6_w_o_film/full`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_beta --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=20 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6_w_o_beta/full`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6/full/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6_w_o_vib/full/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6_w_o_film/full/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-trend20/SSFLv6_w_o_beta/full/...`
- 관찰:
  - `SSFLv6`: round `20` 기준 `Acc 20.30%`, `Total comm 3234.32 MB`, `Test SNR 12dB 16.48%`
  - `SSFLv6_w_o_vib`: round `20` 기준 `Acc 14.93%`, `Total comm 17100.88 MB`, `Test SNR 12dB 12.35%`
  - `SSFLv6_w_o_film`: round `20` 기준 `Acc 21.26%`, `Total comm 17490.85 MB`, `Test SNR 12dB 22.13%`
  - `SSFLv6_w_o_beta`: round `20` 기준 `Acc 19.24%`, `Total comm 3586.46 MB`, `Test SNR 12dB 19.73%`
  - 통신량 경향은 `SSFLv6 << SSFLv6_w_o_beta << SSFLv6_w_o_vib ≈ SSFLv6_w_o_film` 순서다.
  - 성능 경향은 `w_o_film`과 `w_o_beta`가 짧은 horizon에서는 baseline보다 높게 보이지만, 둘 다 baseline보다 통신량이 더 크다.
- 결정:
  - 원래 threshold 기준 짧은 horizon 경향만 보면 baseline `SSFLv6`가 가장 강한 communication-performance trade-off를 보인다.
  - 다음 full sweep 후보는 baseline과 `w_o_beta` 우선, `w_o_vib`와 `w_o_film`는 통신량 회귀가 너무 커 후순위로 둔다.

- 일시: `2026-03-29 22:16 KST`
- 수행 내용:
  - 원래 threshold 기준 `seed=1`, `n_rounds=200` full run 실행
  - `SSFLv6`, `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta` 순차 실행 완료
  - 각 설정의 round `200` 통신량과 `Test SNR 12dB` 정확도 추출
- 변경한 파일:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/WORKLOG.md`
- 실행한 명령어:
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6/full`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_vib --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6_w_o_vib/full`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_film --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6_w_o_film/full`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6_w_o_beta --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=200 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6_w_o_beta/full`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6/full/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6_w_o_vib/full/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6_w_o_film/full/...`
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/orig-threshold-full200/SSFLv6_w_o_beta/full/...`
- 관찰:
  - `SSFLv6`: round `200` 기준 `Acc 43.17%`, `Total comm 28386.97 MB`, `Test SNR 12dB 43.29%`
  - `SSFLv6_w_o_vib`: round `200` 기준 `Acc 21.51%`, `Total comm 177271.38 MB`, `Test SNR 12dB 20.93%`
  - `SSFLv6_w_o_film`: round `200` 기준 `Acc 42.58%`, `Total comm 93566.85 MB`, `Test SNR 12dB 42.43%`
  - `SSFLv6_w_o_beta`: round `200` 기준 `Acc 45.29%`, `Total comm 29419.54 MB`, `Test SNR 12dB 47.09%`
  - full `200` 기준 통신량은 `SSFLv6 < SSFLv6_w_o_beta << SSFLv6_w_o_film << SSFLv6_w_o_vib` 순서다.
  - 성능은 `SSFLv6_w_o_beta`가 가장 높지만, 통신량은 baseline보다 약 `1032.57 MB` 더 크다.
- 결정:
  - 원래 threshold 기준 full `200` 결과에서도 baseline `SSFLv6`가 가장 낮은 통신량을 유지한다.
  - accuracy-only 관점에서는 `w_o_beta`가 강하지만 communication-performance trade-off 기준에선 baseline이 여전히 우선이다.
