# Experiment Spec

## Metadata

- Experiment id: 2026-03-29_v01_harness-bootstrap
- Start date: 2026-03-29
- Status: completed
- Owner: agent-assisted setup

## Summary

Bootstrap a docs-based research harness for this repository so future agent work on communication-performance improvements follows a stable planning and evaluation workflow.

## Question

Can we create a lightweight but durable documentation harness that supports reproducible, agent-assisted research in this codebase?

## Hypothesis

If we move project operating knowledge into a short root `AGENTS.md` plus structured `docs/` artifacts, future research work will be easier to resume, easier to compare, and less likely to produce invalid claims.

## Baseline

- Baseline algorithm: not applicable
- Baseline config: not applicable
- Baseline artifact path: not applicable
- Why this is the right comparison: this is a repository process change, not a model comparison

## Fixed Conditions

- repository scope: `/home/sunmin/SFL_Semantic`
- docs location: `docs/`
- code location: `src/`

## Change Under Test

- intended code paths: documentation and repository instructions only
- changed variable(s): project documentation harness
- search space: minimal docs set needed for sustained agent collaboration

## Metrics

### Primary

- clear project entrypoint for agents
- explicit evaluation contract
- explicit experiment-planning workflow

### Secondary

- docs discoverability
- consistency between root instructions and docs structure

## Validation Plan

### Smoke Check

- command: inspect created files and cross-references
- expected signal of success: docs tree exists and references resolve correctly

### Matched Comparison

- command(s): not applicable
- expected artifact path: not applicable

### Robustness Follow-Up

- extra seeds: not applicable
- extra SNRs: not applicable
- extra channel settings: not applicable

## Promotion Criteria

The repository should have a short entrypoint, clear docs index, harness rules, evaluation protocol, and experiment workflow without storing Markdown guidance under `src/`.

## Stop Criteria

Stop once the baseline document set exists and is internally consistent.

## Risks And Confounders

- possible confounders: over-documentation, stale duplicated instructions
- likely failure modes: too much detail in `AGENTS.md`, unclear separation of concerns
- what could invalidate the result: if future work does not actually use the docs workflow
