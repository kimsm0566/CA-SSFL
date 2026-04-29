# 작업 로그

## 현재 맥락

- 현재 상태: `follow-up 실행 준비중`

## 로그

- 일시: `2026-04-09 13:03 KST`
- 수행 내용:
  - `cross-benchmark` 결과를 바탕으로 `Rayleigh` 통신량 절감 후속 실험 범위를 분리
  - 기존 autonomous script의 JSON 파싱 실패를 우회하기 위해 deterministic runner로 재구성
  - `Rayleigh sweep -> best config selection -> AWGN validation` 순서를 고정
- 일시: `2026-04-09 13:15 KST`
- 수행 내용:
  - 사용자 피드백에 따라 Stage A sweep grid를 재설계
  - `beta`는 `0.1, 0.01, 0.001, 0.0001`의 decade 단위로 제한
  - `film_max_t`, `film_min_t`는 `0.1` 단위 쌍 `0.7/0.4`, `0.8/0.5`, `0.9/0.6`만 사용
  - 기존 미세 단위 sweep 실행은 중단하고 새 grid로 재시작
- 일시: `2026-04-09 13:19 KST`
- 수행 내용:
  - 사용자 지적에 따라 `n_clients`를 `9`에서 `8`로 수정
  - MPI 프로세스 수 기준을 `8 clients + 1 server = 9`로 재고정
  - 기존 `n_clients=9` follow-up 실행은 중단
  - 결과 혼선을 막기 위해 새 result root를 `/workspace/tmp/2026-04-09-comm-reduction-followup-nclients8`로 분리
