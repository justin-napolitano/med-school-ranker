# Headless Slice E: Research Queue

## Objective

Add a research queue that helps users decide which schools need more review next.

## Prerequisite

Slices A-D should be complete and committed.

## Scope

Do:

- add a research queue view or section;
- prioritize schools by rank, confidence, missing dossier fields, visibility state, and research status;
- add filters for research status, missing sections, rank band, admissions tier, and visibility state;
- show next research action;
- ensure queue reflects local browser state.

Do not:

- implement import/writeback;
- add persistent storage without a privacy/clear-state plan;
- change scoring formulas;
- make the queue hide the full universe.

## Suggested Queue Columns

```text
school_name
decision_rank
rank_band
admissions_tier
rank_confidence
research_status
missing_sections
next_research_action
visibility_state
open_dossier
```

## Verification

Required:

```bash
uv run pytest
uv run med-school-build-site
uv run med-school-build-all
```

Manual/browser or screenshot verification:

- queue shows schools needing research;
- filters work;
- edited dossier state updates queue status;
- hidden schools can be included/excluded by filter;
- opening a dossier from the queue works.

Privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/private outputs/private
```

## Done Criteria

- Research queue is useful and filterable.
- Queue reflects local state.
- Commit message should be similar to `Add school research queue`.
