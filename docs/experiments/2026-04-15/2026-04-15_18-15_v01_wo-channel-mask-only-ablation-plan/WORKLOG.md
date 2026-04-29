# 작업 로그

이 파일은 `w/o channel mask only` 시도의 진행 상황을 누적 기록하는 협업 로그다.

## 현재 맥락

- 현재 상태:
  - 코드 구현 완료
  - smoke / full run / 결과 집계 완료
- 현재 blocker:
  - 없음
- 다음 구체 행동:
  - exact 결과는 내부 진단용으로만 유지
  - paper-facing Table II는 기존 `w_o_film` 결과 사용

## 로그

- 일시: `2026-04-15 18:15 KST`
- 수행 내용:
  - `w/o channel mask only` 계획 문서 작성
- 변경한 파일:
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/PLAN.md`
- 실행한 명령어:
  - 없음
- 생성된 산출물:
  - 없음
- 관찰:
  - 기존 `SSFLv6_w_o_film`은 exact ablation이 아니라 stronger proxy임
- 결정:
  - `model.py`는 유지하고 final `chan_mask`만 all-pass로 바꾸는 방향으로 정리

- 일시: `2026-04-15 18:23 KST`
- 수행 내용:
  - `channel_mask_allpass_enable` 스위치 구현
  - 결과 경로 구분 추가
  - train/eval 양쪽에 동일 스위치 반영
  - 정적 문법 검증 수행
- 변경한 파일:
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `src/utils/trainer.py`
  - `src/utils/eval.py`
- 실행한 명령어:
  - `python3 -m py_compile src/utils/option.py src/run_exp_main.py src/utils/trainer.py src/utils/eval.py`
- 생성된 산출물:
  - 없음
- 관찰:
  - 기본 동작은 유지되고 `channel_mask_allpass_0/1`로 경로가 분리됨
- 결정:
  - smoke 후 full run으로 진행

- 일시: `2026-04-15 18:38 KST`
- 수행 내용:
  - canonical Docker GPU runtime preflight 수행
  - `AWGN`, `Rayleigh` smoke run 완료
- 변경한 파일:
  - 없음
- 실행한 명령어:
  - `sudo docker compose run --rm sfl-semantic check-gpu`
  - `sudo docker compose run --rm sfl-semantic run-exp ... --channel_type=awgn ... --channel_mask_allpass_enable=1 --seed=1 --result_path=/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-awgn`
  - `sudo docker compose run --rm sfl-semantic run-exp ... --channel_type=rayleigh ... --channel_mask_allpass_enable=1 --seed=1 --result_path=/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-rayleigh`
- 생성된 산출물:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-awgn/.../seed_1.npz`
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-rayleigh/.../seed_1.npz`
- 관찰:
  - `check-gpu`에서 `cuda_available=True`, `device_0=NVIDIA GeForce RTX 4070 SUPER` 확인
  - 두 채널 smoke 모두 artifact 저장 성공
- 결정:
  - canonical full `8 runs` 실행

- 일시: `2026-04-15 19:42 KST`
- 수행 내용:
  - `AWGN`, `Rayleigh`, `seed=1,2,3,4` full queue 실행 완료
  - `8`개 `seed_*.npz` 저장 확인
- 변경한 파일:
  - 없음
- 실행한 명령어:
  - `sudo docker compose run --rm sfl-semantic run-exp ... --channel_mask_allpass_enable=1 --channel_type=<awgn|rayleigh> --seed=<1..4> --result_path=/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation`
- 생성된 산출물:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/logs/full_run.log`
- 관찰:
  - 첫 launcher loop는 zsh의 readonly 변수명 `status` 충돌로 `awgn seed=1` 이후 중단됐지만, 이미 생성된 artifact는 정상 보존됨
  - 이후 bash loop로 나머지 queue를 재개해 최종 `8 runs`를 모두 완료함
- 결정:
  - baseline 및 기존 `w_o_film` proxy와 matched summary 비교 수행

- 일시: `2026-04-15 19:49 KST`
- 수행 내용:
  - exact ablation 결과 집계
  - baseline / proxy / exact 3-way summary 생성
  - 결과 문서화 완료
- 변경한 파일:
  - `scripts/analyze_wo_channel_mask_only_ablation.py`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/SPEC.md`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/WORKLOG.md`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/RESULT.md`
  - `docs/experiments/RESULTS_LEDGER.md`
- 실행한 명령어:
  - `python3 -m py_compile scripts/analyze_wo_channel_mask_only_ablation.py`
  - `sudo docker compose run --rm -T sfl-semantic python /workspace/scripts/analyze_wo_channel_mask_only_ablation.py`
- 생성된 산출물:
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/summary.json`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/RESULT.md`
- 관찰:
  - exact `w/o channel mask only`는 baseline보다 두 채널 모두 `comm` 증가와 정확도 하락을 보였다
  - 하지만 기존 `SSFLv6_w_o_film` proxy보다는 일관되게 덜 나빴다
- 결정:
  - exact 결과와 prior proxy의 paper-facing 역할을 분리

- 일시: `2026-04-15 21:20 KST`
- 수행 내용:
  - paper-facing 결과 사용 결정을 이전 `w_o_film` 결과로 되돌림
  - exact 실험은 내부 진단용 보관으로 재분류
  - prior channel-specific ablation 폴더에 paper-facing 결과 요약 추가
- 변경한 파일:
  - `docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RESULT.md`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/WORKLOG.md`
  - `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/RESULT.md`
  - `docs/experiments/RESULTS_LEDGER.md`
- 실행한 명령어:
  - 없음
- 생성된 산출물:
  - `docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RESULT.md`
- 관찰:
  - exact 결과가 정의상 더 정확하지만, 사용자는 원고 표에서는 기존 `w_o_film` 결과를 선호함
  - 따라서 paper-facing 해석과 internal diagnostic 해석을 분리하는 편이 가장 명확함
- 결정:
  - 논문 Table II 하단 `w/o Channel Masking` 행에는 기존 `SSFLv6_w_o_film` 결과를 사용
