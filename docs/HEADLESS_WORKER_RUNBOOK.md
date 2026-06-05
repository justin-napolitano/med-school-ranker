# Headless Worker Runbook

## Purpose

This runbook tells a headless worker how to continue the project without relying on conversational context.

The current next executable phase is:

```text
Phase 2B: Deterministic Scoring
docs/HEADLESS_SCORING_EXECUTION_PLAN.md
```

## Repository

```text
/Users/justin/repos/med-school-ranker
```

## Required Starting Checks

Run from the repo root:

```bash
git status --short
git status --short --ignored data/manual/private data/raw/aamc outputs/private
uv run med-school-build-all
uv run pytest
```

Expected baseline:

- Normal worktree should be clean before edits unless the user explicitly says otherwise.
- `data/manual/private/` is ignored.
- `data/raw/aamc/` is ignored.
- `outputs/private/` is ignored.
- Build and tests pass before the worker changes code.

If baseline build or tests fail, inspect and fix only if the failure is directly related to the assigned phase. Otherwise report the blocker.

## Document Read Order

For the current next phase, read in this order:

1. `docs/PLAN_CRITICAL_REVIEW.md`
2. `docs/HEADLESS_SCORING_EXECUTION_PLAN.md`
3. `docs/EXEC_PLAN.md`
4. `docs/plans/scoring_engine.md`
5. `docs/plans/admissions_probability.md`
6. `docs/plans/applicant_profiles.md`
7. `docs/PREDICTIVE_ADMISSIONS_MODEL_FUTURE_SCOPE.md`

Do not read old conversational context as the source of truth when these docs and the repo disagree. The committed docs win.

## Global Execution Rules

- Run non-interactively.
- Make conservative assumptions from committed docs.
- Do not scrape or download new data.
- Do not implement school-specific predictive admissions probability.
- Do not commit real applicant/private data.
- Do not write private-derived outputs into committed public output files.
- Preserve manual review notes and partner inputs.
- Keep missing values blank; never convert missing data to zero.
- Regenerate workbook/site/upload artifacts when CSVs or displayed docs change.
- Run verification commands before final handoff.

## Privacy Rules

Committed/public build:

- Reads committed `data/applicant_profiles.csv`.
- May generate `outputs/calculated_rankings.csv`, workbook, site, and upload bundle.
- Must not include anything from `data/manual/private/`, `data/private/`, or `outputs/private/`.

Local-private build, if Phase 2B implements it:

- May read `data/manual/private/applicant_profiles.local.csv`.
- Must write private-derived outputs only under `outputs/private/`.
- Must not include private-derived outputs in `med-school-ranker-upload.zip`.
- Must not update committed workbook/site outputs with private values unless the user explicitly requests a local-only uncommitted build.

## Current Headless Worker Prompt

Use this prompt for the next headless execution session:

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/HEADLESS_SCORING_EXECUTION_PLAN.md end to end.

Follow docs/HEADLESS_WORKER_RUNBOOK.md first. Start from a clean status check. Do not scrape or download data. Do not implement predictive admissions probability. Keep private profile input and private-derived outputs out of git and out of the upload bundle.

Implement deterministic Phase 2B scoring from existing normalized data, applicant profile values, partner inputs, scenario weights, and source quality fields. Regenerate rankings, workbook, site, and upload bundle. Add or update tests. Run uv run med-school-build-all and uv run pytest. Commit only public-safe code/docs/data/generated outputs.
```

## Required Final Verification

Run:

```bash
uv run med-school-build-all
uv run pytest
git status --short
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

The final report must include:

- What phase was executed.
- Files changed.
- Output counts that matter.
- Test/build result.
- Confirmation that private paths remained ignored.
- Commit hash, if committed.
