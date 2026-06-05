# Headless Execution Plan: Site UX Review and Research Workflow

## Objective

Run a headless visual review of the current site, capture screenshots, improve obvious UX issues, and implement the first applicant workflow features for school visibility and dossiers.

This plan is for a Codex headless worker. It should be executed after the scoring transparency proof of concept is committed.

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
- Required MVP first: screenshot QA, focused visual fixes, hide/restore controls, minimal dossier index/detail, and CSV export.
- Research queue, advanced dossier editing, storage persistence, and import/writeback are follow-up unless the MVP is complete and verified.
- Browser-local state means in-memory JavaScript state in the first pass. Do not use `localStorage` or `sessionStorage` unless a visible privacy label and clear/reset control are also implemented.

## Phase 0: Preflight

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

## Phase 1: Screenshot-Based Visual QA

Tasks:

- Capture screenshots for the routes/states defined in `01_visual_qa_screenshots.md`.
- Save screenshots under `outputs/site_qa/screenshots/`.
- Create `outputs/site_qa/ux_review_findings.csv`.
- Review screenshots for:
  - text overflow;
  - controls that are unclear or too dense;
  - table columns that obscure the main decision;
  - selector confusion;
  - missing private/local labels;
  - broken detail panels;
  - mobile usability failures.
- Apply focused UI fixes.
- Rebuild and retake screenshots for changed views.

If screenshot tooling is unavailable, stop before feature implementation and report the missing tool as a blocker. A text-only DOM/HTML review is not a substitute for screenshot QA in this pass.

## Phase 2: School Visibility Controls

Tasks:

- Add a reversible "hide from view" action to school rows.
- Add a restore action.
- Add filters for visible, hidden, all, and hard-no.
- Add a hidden-school review surface.
- Store visibility state in in-memory browser state.
- Add CSV export for hidden/visibility decisions.
- Keep hidden schools out of the working ranking view only when the visibility filter says so.
- Do not delete hidden rows from payloads or generated data.

Verification:

- Hiding a school removes it from the visible working view.
- Hidden count updates.
- Hidden school can be restored.
- Hidden schools can be exported with reason/status.
- Full universe remains available through `all` or hidden review mode.
- Export includes `export_schema_version`, `exported_at`, `school_id`, `visibility_state`, and `visibility_reason`.

## Phase 3: School Dossier Profiles

Tasks:

- Add a school profiles/dossiers tab or route.
- Provide an index of all active schools, including MD and DO.
- Open a dossier for each school.
- Include precomputed fields from rankings, school master, admissions stats, cost, policies, and score contributions.
- Add local editable research fields defined in `03_school_dossier_profiles.md`.
- Add missing-data research prompts.
- Keep precomputed facts visually distinct from user-entered research fields.
- Keep this phase to a minimal dossier shell if time is constrained: summary, fit, key facts, missing prompts, notes/status fields, and export.

Verification:

- Every active school has a dossier entry.
- Dossier opens from rankings and from the dossier index.
- Precomputed facts are visible and source/confidence labeled.
- Local editable fields can be changed in browser state.
- Dossier edits can be exported as CSV.
- Export includes `export_schema_version`, `exported_at`, and stable `school_id`.

## Phase 4: Research Workflow and Exports

This phase is follow-up unless Phases 1-3 are complete and verified.

Tasks:

- Add filters for research status, missing sections, rank band, admissions tier, and visibility state.
- Add "next research action" display.
- Add export buttons for:
  - visibility decisions;
  - dossier edits;
  - current ranked view.
- Ensure exports are deterministic, clearly named, and do not include private source files.
- Do not implement import/writeback.

Verification:

- Exports download valid CSV.
- Export headers are stable.
- Exported rows reflect the current browser-local state.

## Required Final Checks

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
