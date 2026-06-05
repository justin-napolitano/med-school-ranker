# Headless Slice D: Dossier Local Edits and Export

## Objective

Add browser-local editable dossier fields and CSV export for applicant research notes.

## Prerequisite

Slices A, B, and C should be complete and committed.

## Scope

Do:

- add editable local fields to dossier detail views;
- keep edits in in-memory browser state;
- add export for non-default dossier edits;
- keep generated facts visually separate from user-entered fields;
- include export schema fields.

Do not:

- use persistent browser storage;
- write edits back to source CSVs;
- implement import;
- add a full research queue;
- change scoring formulas.

## Required Editable Fields

Use a minimal but useful set:

```text
research_status
interest_level
four_year_happiness
location_fit
culture_fit
regret_index
hard_no_flag
hard_no_reason
application_decision_status
notes
```

## Export Contract

Export file:

```text
school_dossier_edits_export.csv
```

Required columns:

```text
export_schema_version
exported_at
school_id
school_name
research_status
interest_level
four_year_happiness
location_fit
culture_fit
regret_index
hard_no_flag
hard_no_reason
application_decision_status
notes
```

Required schema version:

```text
school_dossier_edits_v1
```

## Verification

Required:

```bash
uv run pytest
uv run med-school-build-site
uv run med-school-build-all
```

Manual/browser or screenshot verification:

- editing fields updates the dossier state;
- switching schools does not confuse state between schools;
- export downloads valid CSV;
- export contains only non-default edited rows;
- generated facts remain unchanged.

Privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/private outputs/private
```

## Done Criteria

- Dossier edits work in memory.
- Dossier export works.
- No writeback or persistent storage is added.
- Commit message should be similar to `Add dossier local edits export`.
