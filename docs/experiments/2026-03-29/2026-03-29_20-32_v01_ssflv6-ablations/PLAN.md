# 실험 계획

## 메타데이터

- 실험 id: `2026-03-29_20-32_v01_ssflv6-ablations`
- 초안 일시: `2026-03-29 20:32 KST`
- 상태: `실행 및 1차 정리 완료`
- 담당자: `Codex + 사용자`

## 목표

`SSFLv6`의 세 가지 ablation 변형을 각각 독립 실행해서, 현재 코드베이스 기준에서 어떤 구성 요소가 성능과 통신량에 가장 크게 기여하는지 확인한다.

이번 범위의 직접 실행 대상은 다음 네 가지다.

- `SSFLv6` baseline 재실행
- `SSFLv6_w_o_vib`
- `SSFLv6_w_o_film`
- `SSFLv6_w_o_beta`

성공 기준은 다음과 같다.

- baseline과 세 ablation이 모두 동일한 Docker GPU 실행 경로에서 동작한다.
- 각 실험 시작 전에 해당 설정의 smoke test가 먼저 통과한다.
- 세 ablation이 모두 동일한 고정 조건에서 end-to-end로 실행된다.
- 각 ablation의 결과물이 서로 다른 산출물 경로에 저장된다.
- 비교에 필요한 `.npz`와 로그 파일이 새 실험 폴더 아래에 정리된다.

## 지금 하는 이유

- `ACTIVE_PLAN`의 현재 질문 중 하나가 "`SSFLv6`가 실제로 가장 강한 frontier point인가"인데, 그 전에 내부 구성요소 기여도를 분해해 보는 controlled ablation이 필요하다.
- 현재 코드와 스크립트에는 `SSFLv6` 전용 ablation 세 종류가 이미 정의되어 있다.
- `run_exp_cuda0.sh`와 `output.log` 기준으로 과거 실행 흔적은 있으나, 현재 하네스 기준으로 새 실험 폴더에 정리된 독립 실행 기록은 없다.

현재까지 확인된 사실:

- CLI에서 허용된 `SSFLv6` ablation 알고리즘은 `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta`다.
- 현재 스크립트 기준 공통 설정은 `cifar10`, `partition_type=class`, `n_clients=9`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `model_type=resnetv2`, `channel_type=rayleigh`, `snr_db=12`, `compressed_dim=4096`, `beta=0.0005`, `pruning_threshold=1.0`, seed `1..4`다.
- 이번 실험의 실행기는 호스트 직실행이 아니라 Docker GPU 경로로 고정한다.
- 코드상 의미는 다음과 같다.
  - `SSFLv6_w_o_vib`: VIB `KL` 경로 제거
  - `SSFLv6_w_o_film`: FiLM 기반 채널 적응 마스크 제거
  - `SSFLv6_w_o_beta`: beta scheduler 제거, 고정 beta 사용

## 제안 변경사항

- 대상 코드 경로:
  - 기본적으로 코드 변경 없이 실행
  - 필요 시 실행 편의를 위한 새 실험 스크립트 또는 문서 추가:
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/`
    - 선택적으로 `src/run_exp_cuda0.sh`를 직접 수정하지 않는 별도 runner
- 의도한 동작 변화:
  - canonical 학습 로직은 유지한 채, baseline `SSFLv6`와 세 ablation을 같은 조건으로 반복 실행한다.
  - 모든 실행은 Docker GPU 경로에서만 수행한다.
  - 각 실험은 full run 전에 동일 설정의 smoke test를 먼저 수행한다.
  - 결과 저장 경로를 기존 `src/results/` 대신 새 실험 폴더 하위의 분리된 artifact 경로로 지정한다.
- 유지할 조건:
  - 데이터셋, 분할 방식, 클라이언트 수, 로컬 epoch, 라운드 수, 채널 유형, 학습 SNR, 압축 차원, pruning threshold, seed set은 ablation 간 동일하게 유지한다.
  - 보호된 기존 결과 디렉터리는 수정하지 않는다.
  - 성능 주장은 matched 조건이 충족될 때만 한다.

## 후보 접근법

- 접근 A:
  - baseline `SSFLv6`와 세 ablation을 모두 Docker GPU 경로에서 실행한다.
  - 각 설정에 대해 seed `1` smoke test를 먼저 통과시킨 뒤 full seed set으로 확장한다.
  - 장점: 비교 계약이 명확하고, 실행 실패를 초기에 분리할 수 있다.
  - 단점: 총 실행 시간이 길다.

- 접근 B:
  - smoke 없이 곧바로 full seed set을 실행한다.
  - 장점: 절차가 짧다.
  - 단점: 긴 실행이 중간에 깨지면 원인 분리가 어렵고 재시도 비용이 커진다.

- 우선 접근법과 그 이유:
  - 접근 A를 사용한다.
  - 이유: 사용자가 baseline 재실행 포함, Docker 고정, 각 실험 전 smoke 선행을 명시적으로 요청했다.
  - 따라서 이번 시도의 실행 계약은 "Docker GPU 단일 경로 + baseline 포함 + 실험별 smoke 후 full run"이다.

## 계획된 검증

- 스모크 체크:
  - baseline `SSFLv6`에 대해 Docker GPU 경로에서 seed `1`, 축소 budget smoke를 먼저 실행
  - `SSFLv6_w_o_vib`, `SSFLv6_w_o_film`, `SSFLv6_w_o_beta` 각각에 대해 Docker GPU 경로에서 seed `1`, 축소 budget smoke를 먼저 실행
  - smoke는 full run과 동일한 알고리즘/채널/저장 루트를 쓰되, 실행 가능성만 확인하는 최소 budget으로 고정한다
  - smoke 기본 budget 제안:
    - `seed=1`
    - `n_rounds=1`
    - `n_epochs=1`
    - `n_clients=2`
    - `n_client_data=10`
    - `batch_size=10`
    - 나머지 핵심 알고리즘 축은 full run과 동일하게 유지:
      - `dataset=cifar10`
      - `partition_type=class`
      - `model_type=resnetv2`
      - `channel_type=rayleigh`
      - `snr_db=12`
      - `compressed_dim=4096`
      - `beta=0.0005`
      - `pruning_threshold=1.0`
  - smoke 통과 기준은 종료 코드 `0`, `.npz` 저장, 서버/클라이언트 로그 생성이다
- 비교 대상:
  - 1차 비교: baseline `SSFLv6` 대 각 ablation 비교
  - 2차 비교: 세 ablation 상호 비교
- 예상 산출물 경로:
  - 문서:
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/PLAN.md`
    - 후속 `SPEC.md`, `WORKLOG.md`, `RESULT.md`
  - 실행 산출물:
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/`
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6_w_o_vib/`
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6_w_o_film/`
    - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6_w_o_beta/`

## 리스크와 열린 질문

- 기술적 리스크:
  - 3개 ablation 모두 `n_clients=9`, `n_rounds=200`, seeds `1..4`면 실행 시간이 길다.
  - 결과를 `docs/experiments/` 아래에 저장하면 문서 폴더에 raw artifact가 함께 쌓인다.
  - Docker GPU 경로 하나로 고정하면 재현성은 좋아지지만, 컨테이너 빌드/런타임 문제 발생 시 모든 실행이 함께 막힌다.

- 평가상 리스크:
  - 단일 seed smoke 결과를 최종 비교로 오해하면 안 된다.
  - smoke와 full run의 budget이 다르면 smoke 성공이 성능 비교 타당성을 보장하지는 않는다.

- 검토가 필요한 질문:
  - 결과 raw artifact를 정말 `docs/experiments/.../artifacts/`에 둘지, 아니면 실행 결과는 별도 경로에 두고 이 폴더에는 링크와 요약만 둘지?
  - 없음. smoke budget은 빠른 실패 감지를 우선하는 최소값으로 고정한다.

## 사용자 검토 메모

- 피드백:
  - 모든 실험은 Docker GPU 경로에서 실행한다.
  - `SSFLv6` baseline도 다시 실행해서 ablation과 비교한다.
  - 각 실험 전에 해당 설정의 smoke test를 먼저 수행한다.
- 합의된 결정:
  - 실행기는 Docker GPU로 고정한다.
  - baseline `SSFLv6` + ablation 3개를 모두 실행한다.
  - 실험별 smoke 후 full run 순서를 따른다.
- 남은 쟁점:
  - 결과 저장 루트의 최종 형태
  - 없음

## 실행 게이트

- 구현 시작 가능?: `아니오`
- 아니라면 먼저 명확히 할 점:
  - 이 plan 검토 후, full-run 고정 조건과 저장 구조를 `SPEC.md`에 확정해야 한다.
