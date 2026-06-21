# WCL Major Revision Handoff - 2026-06-21

이 문서는 처음 보는 Codex가 현재 revision 상태를 빠르게 파악하고 다음 작업을 이어가기 위한 인수인계 메모이다.

## 현재 목표

- IEEE WCL major revision response letter와 manuscript revision 마무리.
- Reviewer 1-4를 제외한 대부분의 response는 작성되어 있으나, 제출 전 문장/수식/실험 일치성 검토가 필요하다.
- Rayleigh 실험은 symbol-wise fading 코드로 다시 돌려야 한다.

## 주요 파일

- 최신 수정 manuscript PDF: `papers/IEEE_WCL_SSFL__Major_rev_ (1).pdf`
- 현재 response letter PDF: `papers/response_letter_IEEE_WCL__Major_Revision__선민_ (1).pdf`
- revision notes: `docs/manuscript/revision/`
- 참조 convergence 논문: `convergence.pdf`
- 코드 변경 파일: `src/models/model.py`

## GitHub 상태

- `main` 브랜치가 GitHub `origin/main`과 동기화되어 있음.
- 코드 변경 커밋:
  - `e94782a Use symbol-wise Rayleigh fading`
  - 내용: `src/models/model.py`의 `RayleighChannel`을 symbol-wise fading으로 변경.
- 문서 artifact 정리 커밋:
  - `b106068 Remove manuscript artifacts from repository`
  - 내용: GitHub에서 tracked PDF/FDF/TEX 제거, `.gitignore`에 문서 artifact ignore 규칙 추가.
- 현재 GitHub에는 tracked `*.pdf`, `*.tex`, `*.fdf`가 없어야 한다.
- `reference.bib`, `reference_20.bib`, `revision.txt`, `docs/manuscript/`의 일부 파일은 로컬에 남아 있을 수 있으나 커밋하지 않았다.
- 사용자가 GitHub token을 채팅에 직접 노출한 적이 있다. 값은 이 문서에 저장하지 않는다. 보안상 token revoke/rotate 권장.

## 코드 변경 요약

`src/models/model.py`의 `RayleighChannel.forward()`에서 Rayleigh coefficient shape를 변경했다.

변경 전:

```python
h_r = torch.randn(batch_size, 1, device=x.device) * math.sqrt(0.5)
h_i = torch.randn(batch_size, 1, device=x.device) * math.sqrt(0.5)
```

변경 후:

```python
h_r = torch.randn(batch_size, K, device=x.device) * math.sqrt(0.5)
h_i = torch.randn(batch_size, K, device=x.device) * math.sqrt(0.5)
```

의미:

- 기존 코드는 sample-wise/block Rayleigh fading이었다.
- 수정 후 각 complex symbol마다 독립적인 Rayleigh fading coefficient를 적용한다.
- 논문 문장 "each transmitted symbol experiences an independent complex fading coefficient"와 일치한다.

검증:

- `python -m py_compile src/models/model.py` 통과.
- 호스트 환경에 `torch`가 없어 forward smoke test는 실행하지 못했다.
- 최종 검증은 Docker/GPU 환경에서 Rayleigh 실험 재실행 필요.

주의:

- 입력 feature dimension은 real/imag pair로 묶이므로 짝수여야 한다. 기존 코드도 같은 가정이었다.
- Rayleigh 결과는 이전 block fading 결과와 달라질 수 있으므로 반드시 모든 비교 방법에 대해 동일 조건으로 재실험해야 한다.

## Manuscript 핵심 결정사항

### Reviewer 1-1: Dynamic channel

- Dynamic channel은 "time-varying channel quality represented by SNR"로 정의.
- `t`는 mini-batch transmission time index.
- quasi-static channel assumption을 명시:
  - 각 mini-batch transmission 동안 channel quality는 fixed.
  - 서로 다른 transmission time에서는 변할 수 있음.
- Section II-A에 `dynamic_channel` reference 사용:
  - "Following the quasi-static channel assumption commonly adopted in channel-adaptive wireless transmission~\cite{dynamic_channel}, ..."

### Reviewer 1-2: Rayleigh model

- Main system formulation은 AWGN uplink channel로 전개.
- Eq. (2)에서 Rayleigh fading 가정을 제거.
- Rayleigh는 Section IV-A 실험에서 robustness evaluation으로 설명.
- Rayleigh 실험 문장:
  - "In the Rayleigh experiments, each transmitted symbol experiences an independent complex fading coefficient, and the target average SNR is used to determine the noise power."
- 이 문장은 코드 수정 후 Rayleigh 실험을 다시 돌린다는 전제에서만 사용해야 한다.

### Reviewer 1-3: SNR definition

- Section II-A에서 SNR 정의:

```latex
s_t = \frac{P_t}{N_t}
```

- `P_t`: average transmit power of smashed data.
- `N_t`: noise power.
- `s_t`: current mini-batch transmission의 channel quality.
- Section III-B의 SNR-driven masking에서 기존 `s` 대신 `s_t`와 `s_t^{norm}` 사용.

### Reviewer 1-4: Convergence/insight

- 현재 response letter PDF에는 1-4 response에 한국어 작업 메모가 그대로 들어가 있으므로 반드시 교체해야 한다.
- 라운드를 늘려 Fig. 3(a)가 안정적인 accuracy level에 도달했다고 가정하는 방향으로 response를 작성하기로 했다.
- 만약 실제 확장 실험 후에도 수렴이 명확하지 않으면 "maintains convergence" 대신 "shows stable performance improvement" 또는 "achieves higher accuracy within the same training budget"로 낮춰야 한다.
- Non-IID insight:
  - VIB-driven semantic masking이 VIB loss를 통해 latent information 양을 제한하면서 task-relevant information은 보존.
  - non-IID local distributions로 인한 client-specific/task-irrelevant feature bias를 줄여 server-side model이 더 일관된 task-relevant features를 학습하도록 설명.
- Low-SNR insight:
  - 전체 high-dimensional smashed data를 보내면 noise-corrupted, less-informative dimensions도 서버로 전달됨.
  - SNR-driven channel mask는 low SNR에서 더 selective하게 동작하여 noisy/less-informative dimensions 전송을 줄이고 essential semantic information을 보존.
- 본문 position에서 기존 "maintains convergence" 표현은 실제 extended-round 결과가 안정화됐을 때만 사용.

### Reviewer 1-5: Number of clients

- Section IV-A에 8 clients 명시.
- communication cost는 participating clients 수에 approximately linearly 증가한다고 간단히 언급.
- client 수 변화 실험은 하지 않는 방향.

### Reviewer 2-1: Convergence analysis

- 본문에는 compact version만 넣기로 했다.
- Full derivation/update rules는 response letter에 자세히 설명.
- 본문 핵심 구성:
  - standard non-convex SFL convergence framework under heterogeneous data reference.
  - full-participation SFL-V2 case.
  - CA-SSFL effect as bounded perturbation:

```latex
\mathbb{E}
\left[
\left\|
\tilde{\mathbf{g}}_{i}^{r,t}
-
\mathbf{g}_{i}^{r,t}
\right\|^2
\right]
\le
\delta_{\mathrm{CA}}^2,
\quad \forall i,r,t.
```

  - final bound includes `C_\Delta\delta_{\mathrm{CA}}^2`, not `\eta\delta_{\mathrm{CA}}^2`, because perturbation is not assumed zero-mean.
  - `C_\Delta>0` should be defined as a constant associated with possible perturbation bias.
- Notation:
  - 우리 논문에서는 client index를 `i`로 유지.
  - `r`: communication round.
  - `t`: mini-batch transmission time index within the round.
  - `\tau`: local mini-batch updates per round.
- 참고 convergence 논문은 client를 `n`으로 쓰지만, 우리 notation을 굳이 따라 바꾸지 않기로 했다.

### Reviewer 2-2: Dynamic slicing and overhead

- 본문에는 짧게 압축해서 반영.
- response letter에는 자세히 설명.
- 중요한 보강 포인트:
  - active index set:

```latex
\mathcal{A}=\{k \mid M_{\mathrm{final}}^{(k)}=1\}
```

  - `\tilde{\mathbf{z}}`는 `\mathcal{A}`에 해당하는 active values만 모아 구성.
  - `\tilde{\mathbf{z}}`만 보내면 원래 위치를 알 수 없으므로 `\mathcal{A}`를 metadata로 함께 전송.
  - additional communication round는 필요 없음.
  - server는 zero-initialized tensor에 `\mathcal{A}` 위치대로 값을 넣어 원래 차원으로 복원.
  - backward에서도 같은 `\mathcal{A}`로 active dimension gradient만 client에 전송.
  - index transmission overhead는 reported communication cost에 포함.
  - `\mathcal{A}`는 position information만 포함하고 feature/gradient value 자체는 포함하지 않으므로 full latent/gradient 전송 대비 overhead가 작다고 설명.

## Response letter에서 발견된 수정 필요 사항

현재 PDF `papers/response_letter_IEEE_WCL__Major_Revision__선민_ (1).pdf`를 `pdftotext`로 확인했을 때 다음 문제가 있었다.

### 반드시 수정

1. Cover letter 첫 문단 영어가 어색함.
   - 기존:
     - "Following the mention of the reviewers, we check through the paper again. And, we revised ..."
   - 추천:

```latex
We sincerely thank the editor and reviewers for their valuable time and constructive comments. Following the reviewers' suggestions, we carefully revised the manuscript to address the raised concerns. In this response letter, we address each comment point by point, and the corresponding revisions in the manuscript are highlighted in red.
```

2. `Decisioned Date`는 `Decision Date`로 수정.

3. Reviewer 1 Comment 4 response에 한국어 메모가 그대로 있음. 완전한 영어 response로 교체.

4. Reviewer 1 Comment 4 position에 `maintains convergence`가 남아 있음.
   - extended-round Fig. 3(a)를 실제로 만들고 안정화됐을 때만 사용.
   - 아니면 표현 완화.

5. Reviewer 2 Comment 1/본문 convergence 수식 LaTeX source 확인.
   - `\mathbf{g}*{i}^{r,t}` 같은 오타가 없어야 함.
   - 벡터 norm은 `\left\|...\right\|^2` 사용.
   - `\Theta=\{\Theta_C,\Theta_S\}` braces 확인.

### 수정 권장

1. Reviewer 1 Comment 3 SNR 식은 inline보다 displayed equation으로 두면 PDF 줄바꿈이 덜 어색함.

2. Reviewer 2 Comment 2 response에 다음 문장을 넣으면 좋음:

```latex
The index set is transmitted as metadata together with the sliced latent values, without requiring an additional communication round.
```

3. `Section IVA`처럼 보이는 부분은 source에서 `Section IV-A`로 되어 있는지 확인.

4. Reviewer 1 Comment 5 reviewer 원문은 `plays` 문법 오류가 있으나 reviewer quote는 그대로 두어도 됨.

## 다음 작업 체크리스트

1. Rayleigh symbol-wise 코드로 모든 Rayleigh 실험 재실행.
   - SFL, SC-USFL, CA-SSFL 모두 동일 channel setting 사용.
   - target average SNR로 noise power 결정.
   - 결과가 기존 Fig/Table과 달라질 가능성 있음.

2. Fig. 3(a) convergence curve 재생성.
   - round를 늘려 안정적인 accuracy level 도달 여부 확인.
   - 실제로 안정화되면 response에 "reaches a stable accuracy level" 사용.
   - 안정화가 약하면 표현 완화.

3. Response letter 1-4 영어로 교체.

4. Response letter 2-2를 보강 버전으로 교체.

5. Cover letter/metadata 문장 교정.

6. Final PDF를 다시 뽑아 `pdftotext`로 다음 항목 검색:
   - 한국어 잔여 문장
   - `*{i}` 오타
   - `maskthreshold`
   - `Decisioned`
   - `maintains convergence`
   - `Section IVA`

7. 제출 전 GitHub에는 code만 유지하고 manuscript PDF/TEX는 commit하지 말 것.

