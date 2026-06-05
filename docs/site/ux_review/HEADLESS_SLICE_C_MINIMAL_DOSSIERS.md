# Headless Slice C: Minimal School Dossiers

## Objective

Add a school dossier/profile index and minimal dossier detail view for every active school.

This gives applicants a single place to review precomputed school data before deeper manual research editing is added.

## Prerequisite

Slices A and B should be complete and committed.

## Scope

Do:

- add a dossier/profile index for every active school, including MD and DO;
- add a dossier detail view or panel;
- link ranking rows to dossiers;
- show generated facts separately from local/user fields;
- include missing research prompts;
- use existing precomputed data and source/confidence fields.

Do not:

- add complex editable dossier forms beyond a minimal notes/status placeholder if needed;
- implement full research queue;
- implement persistent storage;
- write notes back to source CSVs;
- exclude DO schools from dossiers because the AAMC selector is MD-only.

## Required Context

Read:

- `docs/HEADLESS_WORKER_RUNBOOK.md`
- `docs/site/ux_review/03_school_dossier_profiles.md`
- `docs/site/ux_review/CRITICAL_REVIEW.md`
- `src/med_school_ranker/site.py`

## Minimal Dossier Sections

Required:

- Summary.
- Applicant Fit.
- Admissions Facts.
- Cost.
- Source/Confidence.
- Missing Research Prompts.
- Links/actions back to rankings.

Optional if straightforward:

- basic local `research_status`;
- basic local notes field;
- export placeholder for Slice D.

## Verification

Required:

```bash
uv run pytest
uv run med-school-build-site
uv run med-school-build-all
```

Manual/browser or screenshot verification:

- dossier index includes all active schools;
- MD and DO schools appear;
- opening a dossier from rankings works;
- precomputed facts are visibly separate from user-entered fields;
- missing prompts appear when expected.

Privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/private outputs/private
```

## Done Criteria

- Every active school has a dossier entry.
- Dossiers open from both index and rankings.
- Generated facts and local fields are visually distinct.
- Commit message should be similar to `Add minimal school dossiers`.
