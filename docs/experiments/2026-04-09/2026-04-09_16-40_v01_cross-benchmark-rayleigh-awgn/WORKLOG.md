# 작업 로그

## 현재 맥락

- 현재 상태: `완료`
- 다음 구체 행동:
  - `Rayleigh` follow-up 통신량 절감 sweep으로 이동

## 로그

- 일시: `2026-04-09 16:40 KST`
- 수행 내용:
  - `SFL`, `SC-USFL`, `SSFLv6 baseline`, `SSFLv6 candidate`의 cross-benchmark 범위를 확정
  - 사용자 요청에 따라 `AWGN` 채널의 `SFL`, `SC-USFL`도 동일 seed set으로 포함
  - seed set을 논문 기준 `1,2,3,4`로 고정
- 생성된 산출물:
  - `PLAN.md`
  - `SPEC.md`
  - `WORKLOG.md`
- 일시: `2026-04-09 12:59 KST`
- 수행 내용:
  - `Rayleigh/AWGN` cross-benchmark `20개 npz` 생성 완료
  - `SFL`/`SC-USFL` smoke에서 드러난 `semantic_enable` 및 MPI 종료 경로 버그 수정 후 본 큐 재실행
  - `SSFLv6 candidate`가 `Rayleigh`에서 `SC-USFL` 대비 accuracy, `-6 dB`, comm 모두 우세함을 확인
  - `SFL`는 accuracy/robustness에서 여전히 강하지만 comm는 압도적으로 큼
  - overnight autonomous follow-up은 JSON 파싱 실패로 미진행 확인
- 생성된 산출물:
  - `RESULT.md`
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-cross-benchmark/`
