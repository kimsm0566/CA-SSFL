# Harness Engineering Best Practices

This document records the best practices surveyed from public references on coding agents, agent evaluation, and harness engineering, and translates them into concrete guidance for this repository.

It is intentionally separate from `HARNESS.md`.

- `HARNESS.md` defines how this repository should operate.
- this file explains why those rules exist and which external practices informed them
- if this file ever appears to conflict with an operating document, follow `AGENTS.md`, `HARNESS.md`, `DOCKER.md`, `docs/experiments/README.md`, and `docs/evals/EVAL_PROTOCOL.md`

## What Harness Engineering Means Here

In this project, harness engineering means designing the full research environment around the model and code, not just tuning prompts.

The harness includes:

- repository-local documentation
- experiment planning artifacts
- execution scripts
- evaluation rules
- validation steps
- logging and result storage
- approval boundaries for risky edits

The practical goal is to make agent-assisted research:

- reproducible
- legible
- comparable
- resistant to vague or inflated performance claims

## Surveyed Themes

### 1. Keep The Entry File Short

Multiple sources converge on the same idea:

- a root instruction file should be short
- detailed knowledge should live in structured docs
- one giant instruction file degrades over time

Why this matters here:

- this repository mixes code, datasets, checkpoints, and historical result artifacts
- agents need a stable map, not a long wall of text
- stale instructions are especially dangerous in research code because they lead to invalid comparisons

Repository policy derived from this:

- `AGENTS.md` is the short entrypoint
- detailed process and evaluation rules live in `docs/`

### 2. Repository-Local Knowledge Must Be The Source Of Truth

Agent platforms consistently stress that agents can only reliably use information that exists in the repository at runtime.

Why this matters here:

- experiment intent, evaluation rules, and comparison contracts should not live only in chat or memory
- if a future agent cannot discover the canonical baseline or metric contract from the repo, the harness is incomplete

Repository policy derived from this:

- store plans, protocols, and results notes under `docs/`
- treat those documents as durable project memory

### 3. Plans Should Be First-Class Artifacts

Harness-engineering guidance for long-running agents emphasizes explicit plans, progress artifacts, and structured handoff state.

Why this matters here:

- research tasks span multiple sessions
- experiments often stall because the rationale for a prior change was never written down
- the project needs a place to track what is being tried, what failed, and what should happen next

Repository policy derived from this:

- maintain `docs/experiments/ACTIVE_PLAN.md`
- organize substantial attempts as dated experiment folders
- use `docs/experiments/_template/` as the folder template
- log meaningful experiment outcomes in `docs/experiments/RESULTS_LEDGER.md`

### 4. Prefer Simple, Composable Agent Workflows

Best-practice guidance for agents generally recommends:

- start with the simplest orchestration that works
- add complexity only when evaluation data shows it is needed

Why this matters here:

- the project goal is scientific progress, not agent sophistication for its own sake
- if a simple plan, implementation, and evaluation loop works, multi-agent decomposition should not be the default

Repository policy derived from this:

- one hypothesis at a time
- one substantial experiment note per serious change
- separate planning, implementation, and evaluation artifacts clearly

### 5. Use Eval-Driven Development

Evaluation best-practice references are consistent on several points:

- evaluate early
- make evals task-specific
- log everything
- combine automated checks with human review
- treat evaluation as continuous, not a one-time event

Why this matters here:

- the repository optimizes a trade-off, not a single scalar metric
- small code changes can change accounting logic, result schema, or evaluation behavior without changing the model itself
- if evaluation is loose, it is easy to mistake bookkeeping changes for model improvements

Repository policy derived from this:

- maintain a formal evaluation contract in `docs/evals/EVAL_PROTOCOL.md`
- distinguish smoke tests from matched comparisons
- distinguish matched comparisons from robustness evaluations

### 6. Do Not Overclaim From Small Or Unmatched Runs

Agent-eval guidance warns against "vibe-based" evaluation and against making claims from uncontrolled comparisons.

Why this matters here:

- this project uses multiple algorithms, channels, SNR settings, seeds, and compression settings
- unmatched comparisons are easy to produce and hard to trust

Repository policy derived from this:

- no claim-making from a single-seed run unless explicitly labeled smoke-only
- no claim-making from runs with mismatched fixed conditions
- report both communication cost and task performance together

### 7. Preserve Raw Artifacts And Comparison Boundaries

Harness engineering works best when the system protects its own reference points.

Why this matters here:

- historical result directories are the closest thing this repo has to benchmark memory
- editing old results in place destroys comparability
- modifying checkpoints or datasets silently can invalidate experiments

Repository policy derived from this:

- protect `src/results/`, `src/old_results/`, `src/old_results2/`, `src/checkpoints/`, and dataset directories
- add new outputs instead of rewriting historical outputs

### 8. Make End-To-End Validation Explicit

Long-running agent guidance emphasizes that agents often mark work complete too early unless validation is explicit.

Why this matters here:

- code can compile while evaluation logic is broken
- training can run while saved artifacts no longer match plotting code
- communication accounting can change without an obvious error

Repository policy derived from this:

- require at least static validation for Python edits
- require the smallest feasible smoke test for behavioral changes
- require explicit statements about what was not validated

### 9. Favor Legibility Over Cleverness

Harness-engineering guidance repeatedly favors structured, boring, navigable systems over opaque cleverness.

Why this matters here:

- this is already a research codebase with heavy algorithmic branching
- extra hidden assumptions make future ablations harder
- cleaner code paths make agent-assisted iteration much safer

Repository policy derived from this:

- keep canonical paths readable
- isolate exploratory logic
- prefer explicit experiment contracts over implicit assumptions

## What Good Practice Looks Like In This Repository

Good practice in this project means:

- every substantial experiment starts with a written hypothesis
- baselines and fixed conditions are explicit
- code changes are scoped to one main idea
- result claims reference matched conditions
- meaningful runs leave a ledger entry
- evaluation distinguishes execution success from actual improvement

## What Bad Practice Looks Like In This Repository

Bad practice in this project includes:

- changing default hyperparameters without documenting the impact
- mixing exploratory code into canonical evaluation paths
- claiming improvement from unmatched runs
- rewriting old result files in place
- changing communication accounting and reporting a "model improvement"
- storing critical rationale only in chat history

## Adaptation For This Project

The public best practices were mostly written for general coding agents or web-app agents. This repository is different:

- the work is research-oriented
- performance claims depend on controlled comparison
- the output is experimental evidence, not only code

So the harness here must emphasize:

- experiment design discipline
- metric contracts
- seed and condition matching
- append-only result logging
- protection of historical artifacts

That is why this repository uses:

- a short root `AGENTS.md`
- a docs-based system of record
- an active plan
- a folder-based experiment template
- a results ledger
- a formal evaluation protocol

## Sources Surveyed

- OpenAI, "Harness engineering: leveraging Codex in an agent-first world"
- OpenAI, "Introducing Codex"
- OpenAI, "Evaluation best practices"
- OpenAI, "A practical guide to building agents"
- Anthropic, "Building effective agents"
- Anthropic, "Effective harnesses for long-running agents"
- AGENTS.md open format documentation
- GitHub Docs on effective repository custom instructions

## Source Links

- https://openai.com/index/harness-engineering/
- https://openai.com/index/introducing-codex/
- https://platform.openai.com/docs/guides/evaluation-best-practices
- https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- https://agents.md/
- https://docs.github.com/en/copilot/concepts/prompting/response-customization
