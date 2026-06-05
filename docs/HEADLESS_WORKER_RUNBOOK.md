# Headless Worker Runbook

## Purpose

This runbook tells a headless worker how to continue the project without relying on conversational context.

The current next executable phase is:

```text
Slice I: Pre-Design Functional UX Consolidation
docs/site/ux_review/HEADLESS_SLICE_I_PRE_DESIGN_FUNCTIONAL_UX.md
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

1. `docs/SITE_UX_REVIEW_AND_RESEARCH_WORKFLOW_PLAN.md`
2. `docs/HEADLESS_SITE_UX_REVIEW_EXECUTION_PLAN.md`
3. `docs/site/ux_review/HEADLESS_SLICE_I_PRE_DESIGN_FUNCTIONAL_UX.md`
4. `docs/site/product_rebuild/02_rankings_and_list_builder.md`
5. `docs/site/product_rebuild/03_school_profiles.md`
6. `docs/site/product_rebuild/06_visual_reporting_quality.md`
7. `docs/EXEC_PLAN.md`

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

Execute docs/site/ux_review/HEADLESS_SLICE_I_PRE_DESIGN_FUNCTIONAL_UX.md end to end.

Follow docs/HEADLESS_WORKER_RUNBOOK.md first. Start from a clean status check and create a clean implementation branch if needed.

This is a functional UX consolidation slice before visual design. Improve Rankings inline review controls, Application List shortlist workflow, Compare side-by-side review, and school profile dossier actions. Update the plan index so implemented UX slices and Slice I status are accurate.

Do not perform a full visual redesign. Do not scrape or download data. Do not change scoring formulas. Do not implement predictive admissions probability. Do not add backend persistence or private data to committed outputs. Keep browser state export/import compatible with the existing reviewer-state and final-list builder paths.

Regenerate workbook, site, upload zip, and data quality outputs. Add or update tests. Run uv run pytest, uv run med-school-validate, uv run med-school-build-all, uv run med-school-build-final-list, git diff --check, and the upload-bundle privacy check. Commit only public-safe code/docs/data/generated outputs.
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
