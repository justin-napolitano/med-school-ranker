# Headless Worker Runbook

## Purpose

This runbook tells a headless worker how to continue the project without relying on conversational context.

The next selected headless execution phase is:

```text
Frontend Product Refresh: Slice 0 Route Shell
docs/HEADLESS_FRONTEND_PRODUCT_REFRESH_PLAN.md
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

For the selected frontend product refresh phase, read in this order first:

1. `docs/FRONTEND_PRODUCT_REFRESH_EXEC_PLAN.md`
2. `docs/HEADLESS_FRONTEND_PRODUCT_REFRESH_PLAN.md`
3. `docs/site/frontend_refresh/CRITICAL_REVIEW.md`
4. `docs/site/frontend_refresh/01_product_navigation_and_state.md`
5. `docs/SITE_VISUAL_DIRECTION_PLAN.md`
6. `docs/SITE_GUIDED_INTAKE_EXEC_PLAN.md`
7. `docs/SITE_TEXT_AND_FRONTEND_FORMATTING_EXEC_PLAN.md`
8. `docs/site/data_modeling/02_json_node_contracts.md`
9. `docs/site/data_modeling/03_card_surfaces_and_profile_sections.md`
10. `docs/EXEC_PLAN.md`

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

Execute docs/site/frontend_refresh/01_product_navigation_and_state.md as the first frontend product refresh slice.

Follow docs/HEADLESS_WORKER_RUNBOOK.md and docs/HEADLESS_FRONTEND_PRODUCT_REFRESH_PLAN.md first. Start from main, pull latest, inspect status, and create branch impl-frontend-route-shell if needed.

Clean up the public route shell and navigation so the applicant workflow is primary: intake/start, rankings, schools, applications, methodology, and admin routes under local/admin surfaces. Preserve existing guided intake, rankings, school profile, application-list, compare, local state, advanced tables, publish-safe mode, and GitHub Pages deployment.

Do not change scoring formulas. Do not scrape/download data. Do not implement predictive admissions probability. Do not migrate frameworks or persistence. Do not commit private applicant answers or private-derived outputs.

Regenerate required site outputs. Run uv run med-school-build-site --site-mode publish_safe, uv run med-school-validate, uv run pytest, git diff --check, the publish-safe privacy smoke check from docs/HEADLESS_FRONTEND_PRODUCT_REFRESH_PLAN.md, and screenshot QA if dependencies are already available. Commit only intended public-safe code/docs/generated outputs.
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
