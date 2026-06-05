# Headless Slice B: School Visibility Controls

## Objective

Add reversible school hide/restore behavior so users can remove schools from the current working view without deleting them or losing auditability.

## Prerequisite

Slice A should be complete and committed.

## Scope

Do:

- add hide/restore controls to ranking rows or row detail actions;
- add visible/all/hidden filters;
- add a hidden-school review surface;
- keep visibility state in in-memory browser state;
- add CSV export for non-default visibility decisions;
- include export schema fields.

Do not:

- implement school dossiers;
- implement research queue;
- use `localStorage` or `sessionStorage`;
- write visibility decisions back to source CSVs;
- delete schools from payloads or generated data;
- change scoring formulas.

## Required Context

Read:

- `docs/HEADLESS_WORKER_RUNBOOK.md`
- `docs/site/ux_review/02_school_visibility_controls.md`
- `docs/site/ux_review/CRITICAL_REVIEW.md`
- `src/med_school_ranker/site.py`

## Export Contract

Export file:

```text
school_visibility_export.csv
```

Required columns:

```text
export_schema_version
exported_at
school_id
school_name
visibility_state
visibility_reason
hidden_at
updated_at
source
notes
```

Required schema version:

```text
site_visibility_v1
```

## Verification

Required:

```bash
uv run pytest
uv run med-school-build-site
uv run med-school-build-all
```

Manual/browser or screenshot verification:

- hide one school;
- visible view excludes it;
- all view includes it;
- hidden view includes it;
- restore returns it to visible view;
- export downloads valid CSV with schema fields.

Privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/private outputs/private
```

## Done Criteria

- Hide/restore works in memory.
- Hidden-school review works.
- Visibility export works.
- Full universe remains accessible.
- Commit message should be similar to `Add school visibility controls`.
