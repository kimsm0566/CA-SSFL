# Deep Joint Source Channel Coding for Wireless Image Transmission with OFDM

## 서지 정보

- 저자: Mingyu Yang, Chenghong Bian, Hun-Seok Kim
- 학회/저널 및 연도: IEEE ICC, 2021
- 원문 링크: https://arxiv.org/abs/2101.03909
- 로컬 파일 경로: 없음

## 한 줄 요약

- fading 환경에서는 단순 encoder보다 채널 구조를 model-aware하게 넣은 OFDM/신호처리 블록이 훨씬 강건하다.

## 문제 설정

- 학습 설정: model-driven deep JSCC
- 데이터셋: 이미지 전송
- 파티션 방식: 해당 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: multipath fading + OFDM + clipping
- SNR 설정: 다양한 채널 조건 mismatch 포함
- 통신 제약: OFDM 송수신 구조 내 bandwidth 제한

## 방법 요약

- CNN encoder/decoder에 OFDM baseband processing blocks를 differentiable layer로 삽입
- unstructured CNN이 아니라 채널 지식을 반영한 end-to-end 학습
- multipath fading과 clipping에 강한 구조를 직접 반영

## 보고된 결과

- 주요 지표: 재구성 품질
- 비교 기준선: BPG + LDPC + OFDM, unstructured CNN
- 핵심 성과: fading과 clipping 모두에서 baseline 대비 우수
- 강건성 점검: 학습 조건과 다른 채널 조건에도 견고성 보고

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: `src/models/model.py` 채널 모델과 semantic encoder/decoder 경계
- 가장 가까운 in-repo 알고리즘 또는 baseline: `CA-SSFL Orig`
- 바로 재사용 가능해 보이는 점:
  - representation만 바꾸는 것보다 channel-aware inductive bias가 중요하다는 근거

## 약점과 재현 리스크

- OFDM/multipath 중심이라 현재 flat Rayleigh와는 직접 다름
- reconstruction task 위주

## 가능한 개선점

- 우리 쪽에서는 full OFDM이 아니라도, channel-quality-aware masking 또는 post-channel denoising head처럼 model-aware 구조를 넣는 것이 더 효과적일 수 있음

## 이 코드베이스에서 검증할 가설

- Rayleigh robustness 문제는 단순 latent mixing보다 channel-aware restoration 또는 channel-aware gating rule 개선으로 더 잘 해결될 수 있다.

## 액션 상태

- 상태: reviewed
- 다음 단계: `post-channel feature denoising` 또는 `channel-aware masking objective` 검토
