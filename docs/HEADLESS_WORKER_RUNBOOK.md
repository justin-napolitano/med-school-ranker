# Headless Worker Runbook

## Purpose

This runbook tells a headless worker how to continue the project without relying on conversational context.

No next headless execution phase is currently selected.

The most recently executed phase is:

```text
Site Data Modeling Node Slice
docs/HEADLESS_SITE_DATA_MODELING_EXECUTION_PLAN.md
```

Do not rerun that slice unless the user explicitly asks. The likely next work is a product card/profile UI adoption or design slice that consumes the generated node files under `outputs/site/data/nodes/`.

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

For a future card/profile UI adoption phase, read in this order first:

1. `docs/SITE_DATA_MODELING_EXEC_PLAN.md`
2. `docs/SITE_PRODUCT_REBUILD_EXEC_PLAN.md`
3. `docs/site/data_modeling/01_canonical_domain_tables.md`
4. `docs/site/data_modeling/02_json_node_contracts.md`
5. `docs/site/data_modeling/03_card_surfaces_and_profile_sections.md`
6. `docs/site/data_modeling/04_admin_public_payload_separation.md`
7. `docs/site/data_modeling/06_validation_privacy_and_qa.md`
8. `docs/HEADLESS_PRODUCT_SITE_REBUILD_EXECUTION_PLAN.md`
9. `docs/EXEC_PLAN.md`

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

There is no current prompt selected. Before the next `codex exec` run, choose or draft a specific card/profile UI adoption plan and then write a bounded prompt here.

The executed data-modeling prompt is preserved in `docs/HEADLESS_SITE_DATA_MODELING_EXECUTION_PLAN.md` for history.

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
