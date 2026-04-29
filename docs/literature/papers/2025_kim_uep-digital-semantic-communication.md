# Unequal Error Protection for Digital Semantic Communication with Channel Coding

## 서지 정보

- 저자: Seonjung Kim, Yongjeong Oh, Yongjune Kim, Namyoon Lee, Yo-Seb Jeon
- 학회/저널 및 연도: arXiv preprint, 2025
- 원문 링크: https://arxiv.org/abs/2508.03381
- 로컬 파일 경로: 없음

## 한 줄 요약

- semantically 중요한 bit는 동일 보호가 아니라 unequal error protection을 받아야 하며, 가장 단순한 repetition조차 중요도 기반이면 효과가 있다.

## 문제 설정

- 학습 설정: digital semantic communication
- 데이터셋: 이미지 전송 task
- 파티션 방식: 해당 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: bit error / short block coding
- SNR 설정: finite blocklength regime
- 통신 제약: total blocklength 최소화

## 방법 요약

- semantic bits의 importance를 learned bit-flip target reliability로 정의
- bit-level UEP:
  - repetition coding으로 bit마다 다른 보호 수준 부여
- block-level UEP:
  - 비슷한 중요도를 가진 bit를 짧은 block으로 묶고 modern channel code 적용

## 보고된 결과

- 주요 지표: task performance, transmission efficiency
- 비교 기준선: uniform protection
- 핵심 성과: UEP가 conventional equal protection 대비 효율/성능 향상
- 강건성 점검: heterogeneous reliability 요구를 명시적으로 모델링

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: `support floor`, future repetition-based protection
- 가장 가까운 in-repo 알고리즘 또는 baseline: `CA-SSFL Orig`
- 바로 재사용 가능해 보이는 점:
  - 전체 semantic vector를 건드리지 말고 top-important feature만 selective repetition하는 방향

## 약점과 재현 리스크

- digital semantic communication setting
- 우리 analog sparse feature channel과 직접 동일하진 않음

## 가능한 개선점

- 현재 구조에서는 “top-k important active feature duplicate transmit” 같은 초소형 repetition 실험으로 번역 가능

## 이 코드베이스에서 검증할 가설

- Rayleigh에서 중요 feature 일부만 한 번 더 보내는 `importance-aware repetition`은 full spreading보다 더 직접적이고 더 controllable한 보호 메커니즘일 수 있다.

## 액션 상태

- 상태: reviewed
- 다음 단계: `importance-aware repetition`를 새 보호 메커니즘 후보로 격상
