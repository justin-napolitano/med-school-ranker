# Headless Slice A: Screenshot QA and Triage

## Objective

Capture visual evidence for the current site, record UX findings, and fix only high-impact layout, label, and clarity issues.

This slice creates the visual baseline for later school visibility and dossier work.

## Scope

Do:

- serve the current generated site;
- capture desktop/mobile screenshots for existing routes/states;
- create `outputs/site_qa/ux_review_findings.csv`;
- fix high-impact layout, copy, label, empty-state, or clarity issues found in screenshots;
- rebuild and retake screenshots for changed views;
- commit screenshots, findings, and public-safe fixes.

Do not:

- add hide/restore school controls;
- add school dossiers;
- add research queue;
- add new export features;
- change scoring formulas;
- add private data to public outputs.

## Required Context

Read:

- `docs/HEADLESS_WORKER_RUNBOOK.md`
- `docs/SITE_UX_REVIEW_AND_RESEARCH_WORKFLOW_PLAN.md`
- `docs/site/ux_review/01_visual_qa_screenshots.md`
- `docs/site/ux_review/CRITICAL_REVIEW.md`
- `src/med_school_ranker/site.py`

## Execution Steps

1. Confirm the worktree is clean or understandable.
2. Run `uv run pytest`.
3. Run `uv run med-school-build-site`.
4. Serve the site locally.
5. Capture screenshots for every existing required view from `01_visual_qa_screenshots.md`.
6. Record findings in `outputs/site_qa/ux_review_findings.csv`.
7. Fix only high-impact visual/clarity issues.
8. Rebuild and retake screenshots for changed views.
9. Run final verification.
10. Commit.

## Screenshot Rule

Screenshots are required for this slice.

If no screenshot mechanism is available, stop before implementation and report the tooling gap. Do not substitute text-only DOM review for screenshot QA.

## Verification

Required:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
```

Privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/private outputs/private
```

## Done Criteria

- Screenshot files exist under `outputs/site_qa/screenshots/`.
- Findings CSV exists.
- High-severity findings are fixed or explicitly deferred with reasons.
- Build/test/privacy checks pass.
- Commit message should be similar to `Run site UX screenshot QA`.
