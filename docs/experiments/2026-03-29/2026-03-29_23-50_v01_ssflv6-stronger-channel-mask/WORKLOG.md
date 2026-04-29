# 작업 로그

이 파일은 해당 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태: `진단 완료`
- 현재 blocker: 현재 후보는 data comm 감소 폭이 작고 초기 성능이 더 나빠 미채택
- 다음 구체 행동: 필요 시 더 강한 다음 후보를 새로 설계

## 로그

- 일시: `2026-03-29 23:50 KST`
- 수행 내용:
  - 새 stronger-mask 시도용 `PLAN.md`, `SPEC.md`, `WORKLOG.md`, `RESULT.md` 생성
  - 기존 `beta=0.001` sweep는 사용자 redirect로 중단
- 변경한 파일:
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/PLAN.md`
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/SPEC.md`
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/WORKLOG.md`
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/RESULT.md`
- 실행한 명령어:
  - 없음
- 생성된 산출물:
  - 없음
- 관찰:
  - 사용자는 현재보다 조금 더 강한 channel mask를 원했다.
- 결정:
  - 중간 강도의 threshold 후보를 먼저 5라운드에서 검증한다.

- 일시: `2026-03-29 23:52 KST`
- 수행 내용:
  - current canonical보다 소폭 강한 threshold 후보 적용
  - `python -m py_compile src/utils/trainer.py` 검증
  - `SSFLv6` `seed=1`, `n_rounds=5` 진단 run 실행
  - 진단 후 코드를 canonical threshold로 복원
- 변경한 파일:
  - `src/utils/trainer.py`
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/WORKLOG.md`
- 실행한 명령어:
  - `python -m py_compile src/utils/trainer.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=5 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/artifacts/diag_ssflv6_5r`
- 생성된 산출물:
  - `docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/artifacts/diag_ssflv6_5r/...`
- 관찰:
  - 후보 식은 `max(0.25, min(0.60, 0.60 - (snr_normalized * 0.35)))`였다.
  - round당 model comm는 그대로 `46.97 MB`였다.
  - round당 data comm는 `113.26 MB`, `114.31 MB`, `116.40 MB`, `116.03 MB` 수준으로 current canonical `119~123 MB` 대비 소폭 감소에 그쳤다.
  - breakdown 기준 `avg_active_indices`는 대략 `548~564` 수준으로 current canonical `580~600`보다만 약간 낮았다.
  - round `5` acc는 `12.25%`, `Test SNR 12dB`는 `10.79%`로 current canonical 5라운드 진단보다 더 약했다.
- 결정:
  - 이 후보는 “조금 더 강한 마스크”로서 통신량 감소 폭이 너무 작고 초기 성능 손실이 커서 미채택한다.
  - canonical 코드는 원래 threshold 식으로 복원 유지한다.
