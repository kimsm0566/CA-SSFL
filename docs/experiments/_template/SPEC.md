# 실험 스펙

## 메타데이터

- 실험 id: `YYYY-MM-DD_HH-MM_vNN_short-slug`
- 문서 폴더: `docs/experiments/YYYY-MM-DD/YYYY-MM-DD_HH-MM_vNN_short-slug/`
- 시작 일시: `YYYY-MM-DD HH:MM TZ`
- 상태: 제안 | 진행중 | 완료 | 보류 | 기각
- 담당자:

## 요약

아이디어를 한 단락으로 간단히 설명한다.

## 질문

이 시도가 정확히 어떤 질문에 답하려는가?

## 가설

반증 가능한 가설 1개를 명시한다.

## 기준선

- 기준선 알고리즘:
- 기준선 설정:
- 기준선 산출물 경로:
- 이 비교가 적절한 이유:

## 고정 조건

- dataset:
- partition_type:
- n_clients:
- n_client_data:
- batch_size:
- n_epochs:
- n_rounds:
- channel_type:
- seed_set:
- evaluation_path:

## 변경 변수

- 대상 코드 경로:
- 바꾸는 변수:
- 탐색 범위:

## 지표

### 주요 지표

- 최종 테스트 정확도
- 누적 통신량

### 보조 지표

- multi-SNR 정확도
- 최악 SNR 정확도
- seed 평균 및 표준편차
- 학습 안정성

## 검증 계획

### 스모크 체크

- 명령어:
- 성공 신호:

### 매칭 비교

- 명령어:
- 예상 산출물 경로: `/workspace/tmp/YYYY-MM-DD/your-run-slug`

### 강건성 후속 검증

- 추가 seed:
- 추가 SNR:
- 추가 channel 설정:

## 예상 실행 규모와 시간

- 총 실행 수:
- run당 예상 시간:
- 총 예상 시간:
- 시간 추정 전제:

## 승격 기준

어떤 조건이 충족되어야 실제 개선으로 볼 것인가?

## 중단 기준

어떤 조건이면 이 아이디어 추적을 중단할 것인가?

## 리스크와 교란 요인

- 가능한 교란 요인:
- 예상 실패 모드:
- 결과를 무효화할 수 있는 요소:
