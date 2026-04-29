# Evaluation Protocol

This file defines how to evaluate changes in this repository without overstating results.

This file is the source of truth for seed policy, evaluation levels, comparison contract, and claim language. Other documents should link here instead of duplicating those rules in full.

## Evaluation Objective

The project does not optimize accuracy alone.

Canonical evaluation asks:

- does a change improve the communication-performance frontier?
- does the gain hold under matched experimental conditions?
- does the gain survive variation across seeds and channel conditions?

## Canonical Metrics

### Primary Metrics

- final test accuracy
- cumulative communication cost in MB

### Secondary Metrics

- accuracy over communication rounds
- loss over communication rounds
- multi-SNR accuracy curve
- average and worst-case SNR performance
- seed mean and seed standard deviation

## Canonical Seed Policy

Unless a document explicitly states otherwise for a smoke check or a debugging-only run, the default seed set for experiments in this repository is:

- `1,2,3,4`

Interpretation:

- `seed 1,2,3,4` is the canonical seed set for claim-making runs.
- New exploratory experiments should also default to `seed 1,2,3,4`.
- Reduced seed sets such as `seed 1,2` are allowed only when the document explicitly labels the run as a smoke check, debugging pass, or temporary budget-saving probe.
- A result should not be promoted from exploratory status unless it is revalidated on `seed 1,2,3,4`.

### Guardrail Metrics

- reproducibility of the run configuration
- artifact schema compatibility
- stability of training behavior
- interpretability of the claimed gain

## Evaluation Levels

### Level 0: Static Validation

Use when:

- only documentation changes
- small refactors with no intended behavioral change

Examples:

- path checks
- schema checks
- `python -m py_compile` on touched files

### Level 1: Smoke Run

Use when:

- a code path changed and basic execution must be verified quickly

Goal:

- prove the modified path still runs end to end

Not sufficient for:

- claiming a new best model
- promoting a default change
- comparing candidate communication-performance trade-offs against a canonical baseline

### Level 2: Matched Comparison

Use when:

- comparing a candidate against a baseline

Requirements:

- same dataset
- same partition type
- same client count
- same client data size
- same training budget
- same seed set
- same evaluation path
- same reporting logic

Budget rule:

- if the canonical baseline uses `200` rounds, the candidate comparison must also use `200` rounds
- short trend runs such as `20` rounds may be used only as smoke or debugging checks
- do not use a short trend run as the deciding evidence for promotion, rejection, or comparative claims

If any of these differ, the result is exploratory rather than claim-making.

### Level 3: Robustness Evaluation

Use when:

- a candidate looks promising and must be stress-tested

Recommended axes:

- multiple seeds
- multi-SNR sweep
- AWGN and Rayleigh when relevant

## Comparison Contract

Do not compare runs as if they were equivalent when any of the following changed without being explicitly controlled for:

- default script hyperparameters
- result schema
- data partition semantics
- evaluation function behavior
- seed set
- communication accounting logic

## Claim Language

Use careful language:

- smoke only: "runs successfully" or "promising"
- single matched run: "candidate improvement"
- repeated matched runs with stable gains: "supported improvement"

Avoid:

- "best"
- "state of the art"
- "improved"

unless the comparison contract is satisfied.

## Provisional Promotion Guidance

Until baseline variance is measured more carefully, use these provisional rules:

- promote a change if it improves accuracy at equal or lower communication cost under matched conditions
- promote a change if it lowers communication cost with only negligible and justified accuracy loss
- do not promote a change that wins on one seed but loses inconsistently across repeated runs
- do not promote a change that breaks robustness to SNR or channel type without an explicit scope restriction

These thresholds should be tightened after canonical baseline variance is measured.

## Reporting Checklist

Every serious result report should include:

- baseline name
- candidate name
- fixed conditions
- changed variables
- seed set
- main metrics
- artifact path
- decision
- remaining unknowns

Also include:

- whether the run used the canonical seed set `1,2,3,4`
- whether the original `SPEC.md` included an expected runtime estimate and whether the observed runtime materially deviated from it

## Human Review Rule

If an automated metric suggests a gain but the result looks suspicious, prefer human inspection over automatic promotion.

Typical suspicion signals:

- communication cost changed because accounting changed, not because the method improved
- one metric improved while another silently regressed
- saved artifact structure changed and downstream scripts no longer compare like-for-like
