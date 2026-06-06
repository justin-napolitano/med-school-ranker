# Headless Worker Runbook

## Purpose

This runbook tells a headless worker how to continue the project without relying on conversational context.

The next selected headless execution phase is:

```text
Live Scoring And Filter Controls
docs/LIVE_SCORING_FILTERS_EXEC_PLAN.md
```

The most recently executed phase is:

```text
Publish-Safe GitHub Pages Deploy Flow
docs/site/build_and_deploy.md
```

Do not rerun that slice unless the user explicitly asks.

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

For the selected live scoring and filter-controls phase, read in this order first:

1. `docs/LIVE_SCORING_FILTERS_EXEC_PLAN.md`
2. `docs/site/live_scoring_filters/CRITICAL_REVIEW.md`
3. `docs/site/live_scoring_filters/01_filter_controls.md`
4. `docs/site/live_scoring_filters/02_live_score_engine.md`
5. `docs/site/live_scoring_filters/03_weight_controls_and_ux.md`
6. `docs/site/live_scoring_filters/04_card_copy_and_methodology.md`
7. `docs/site/live_scoring_filters/05_headless_qa_and_critical_review.md`
8. `docs/site/live_scoring_filters/HEADLESS_PROMPT.md`

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

Use this prompt for the next `codex exec` run:

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/LIVE_SCORING_FILTERS_EXEC_PLAN.md and follow docs/site/live_scoring_filters/HEADLESS_PROMPT.md.

Preserve current uncommitted product-app work. Do not stage untracked screenshot artifacts. Add browser-local live scoring, state/city/Texas exclusions, source-backed-or-disabled ownership filtering, Not Interested behavior, methodology updates, and smoke checks. Remove data-confidence/source-confidence filters for now; confidence/source-quality may remain transparency-only.

Do not scrape/download data. Do not implement predictive admissions probability. Do not migrate frameworks or persistence. Do not commit private applicant answers or private-derived outputs.

Run cd frontend && npm run build && npm run smoke, then cd .. && uv run med-school-validate && uv run pytest && git diff --check. Commit intended changes only and do not push.
```

The executed data-modeling and profile-node prompts are preserved in their respective headless plans for history.

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
