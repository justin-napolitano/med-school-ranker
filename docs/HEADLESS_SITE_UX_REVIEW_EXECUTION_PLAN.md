# Headless Execution Plan: Site UX Review and Research Workflow

## Objective

Coordinate the site UX review and research workflow work across separate headless slices.

This plan is for a Codex headless worker. It should be executed after the scoring transparency proof of concept is committed.

Do not execute all slices in one run unless the user explicitly asks. The recommended next run is Slice A only.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

## Required Context

Read these first:

- `docs/HEADLESS_WORKER_RUNBOOK.md`
- `docs/SITE_UX_REVIEW_AND_RESEARCH_WORKFLOW_PLAN.md`
- `docs/site/ux_review/01_visual_qa_screenshots.md`
- `docs/site/ux_review/02_school_visibility_controls.md`
- `docs/site/ux_review/03_school_dossier_profiles.md`
- `docs/site/ux_review/04_research_workflow_and_exports.md`
- `docs/site/ux_review/HEADLESS_SLICE_A_SCREENSHOT_QA.md`
- `docs/site/ux_review/HEADLESS_SLICE_B_VISIBILITY_CONTROLS.md`
- `docs/site/ux_review/HEADLESS_SLICE_C_MINIMAL_DOSSIERS.md`
- `docs/site/ux_review/HEADLESS_SLICE_D_DOSSIER_EDITS_EXPORT.md`
- `docs/site/ux_review/HEADLESS_SLICE_E_RESEARCH_QUEUE.md`

Read these as implementation context:

- `docs/SITE_PRODUCT_REBUILD_EXEC_PLAN.md`
- `docs/SCORING_TRANSPARENCY_EXEC_PLAN.md`
- `src/med_school_ranker/site.py`
- `src/med_school_ranker/rankings.py`
- `src/med_school_ranker/workbook.py`
- `tests/`

## Execution Rules

- Run non-interactively.
- Do not fetch network data.
- Do not add a backend.
- Do not add authentication.
- Do not write browser-local edits back to source CSVs in this pass.
- Do not delete schools from source data.
- Do not remove DO schools from the project; only respect MD-only scope where the existing selector requires it.
- Do not implement predictive admissions probability.
- Do not commit private profile data or private-derived outputs.
- Prefer additive site/data outputs and reversible local interactions.
- Execute one slice per headless run unless explicitly instructed otherwise.
- Required order: Slice A, Slice B, Slice C, Slice D, Slice E.
- Research queue, advanced dossier editing, storage persistence, and import/writeback are follow-up until their slice is explicitly selected.
- Browser-local state means in-memory JavaScript state in the first pass. Do not use `localStorage` or `sessionStorage` unless a visible privacy label and clear/reset control are also implemented.

## Slice Order

### Slice A: Screenshot QA and Triage

Plan:

```text
docs/site/ux_review/HEADLESS_SLICE_A_SCREENSHOT_QA.md
```

Purpose:

- capture screenshots;
- record findings;
- fix high-impact visual/clarity issues only.

### Slice B: School Visibility Controls

Plan:

```text
docs/site/ux_review/HEADLESS_SLICE_B_VISIBILITY_CONTROLS.md
```

Purpose:

- hide/restore schools;
- visible/all/hidden filters;
- hidden-school export.

### Slice C: Minimal School Dossiers

Plan:

```text
docs/site/ux_review/HEADLESS_SLICE_C_MINIMAL_DOSSIERS.md
```

Purpose:

- dossier index;
- dossier detail shell;
- precomputed facts and missing prompts.

### Slice D: Dossier Local Edits and Export

Plan:

```text
docs/site/ux_review/HEADLESS_SLICE_D_DOSSIER_EDITS_EXPORT.md
```

Purpose:

- local editable dossier fields;
- dossier edits export.

### Slice E: Research Queue

Plan:

```text
docs/site/ux_review/HEADLESS_SLICE_E_RESEARCH_QUEUE.md
```

Purpose:

- research queue and next actions.

## Shared Preflight

Tasks:

- Confirm clean or understandable git state.
- Run the current test suite.
- Build the current site.
- Serve the site locally.
- Confirm whether screenshot tooling is available.

Commands:

```bash
uv run pytest
uv run med-school-build-site
curl -I http://localhost:8000
```

If no server is already running, start one with an approved local static-server approach already used in the repo.

## Shared Final Checks

Before committing:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
```

Inspect upload bundle privacy:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
```

Check ignored private paths:

```bash
git status --short --ignored data/manual/private data/private outputs/private
```

## Stop Conditions

Stop and report if:

- visual screenshot tooling is unavailable for Phase 1;
- the site cannot be served locally;
- the working tree contains conflicting edits in the same files;
- browser-local persistence requires a backend or writeback policy decision;
- private data would need to be committed to verify behavior.

## Handoff Format

Report:

- commit hash;
- changed paths;
- screenshots captured;
- UX findings fixed;
- tests and privacy checks run;
- any views not screenshot-tested;
- residual risks.
