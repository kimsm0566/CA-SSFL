# Literature Review

This directory stores project-relevant paper reviews in a form that can be reused for experiment planning.

The goal is not to accumulate generic summaries. The goal is to extract the parts that matter for this repository:

- communication-performance trade-offs
- robustness across channel conditions and seeds
- fair baseline comparisons
- concrete follow-up hypotheses

## Layout

- `PAPER_TEMPLATE.md`
  - canonical paper-note template
- `papers/`
  - one Markdown note per paper
- `sources/`
  - optional local copies of PDFs or supplementary material when continued review requires them

## Workflow

1. Start from a paper link, DOI, arXiv page, or PDF.
2. If a local copy is needed, save the original PDF under `sources/` with a slug that matches the paper note.
3. Create a paper note under `papers/` using `PAPER_TEMPLATE.md`.
4. Extract the paper's exact setting before interpreting claims:
   - learning setup: semantic, split, federated, or hybrid
   - dataset and partition assumptions
   - client count and training budget
   - channel model and SNR assumptions
   - communication accounting method
5. Record project-specific judgment, not just a summary:
   - how it relates to this repository
   - what seems reusable here
   - what looks weak, incomplete, or hard to reproduce
   - what concrete experiment idea it suggests
6. If the paper leads to a real experiment, reference it from `docs/experiments/` rather than keeping the plan only in the paper note.

## Paper Note Naming

Use this pattern for paper notes and optional local source files:

- `YYYY_first-author_short-slug.md`
- `YYYY_first-author_short-slug.pdf`

Examples:

- `2024_lee_adaptive-semantic-compression.md`
- `2023_kim_split-learning-rayleigh.pdf`

## Required Sections

Each paper note should include at least:

- citation
- source link
- one-line takeaway
- problem setting
- method summary
- reported results
- relation to this project
- weaknesses and reproducibility risks
- possible improvements
- actionable hypotheses for this codebase
- action status

## Language Policy

- Write new literature notes in Korean by default.
- Keep paper note filenames and optional source filenames ASCII-friendly using the documented slug rule.
- Existing older notes may remain mixed-language unless the task explicitly includes translation.

## Review Standard

Do not treat published results as directly transferable. Evaluate whether the claimed gain is meaningful under this repository's contract:

- matched baselines
- communication cost reported with accuracy
- robustness across seeds when claim-making
- robustness across channel conditions when relevant

Use `docs/evals/EVAL_PROTOCOL.md` when deciding whether a paper's evidence is strong enough to justify implementation work here.
