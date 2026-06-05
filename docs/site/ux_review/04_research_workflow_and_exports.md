# Research Workflow and Exports

## Objective

Turn school review into a workflow: identify what needs research, fill structured fields, hide or shortlist schools, and export the user's working state.

## Workflow Views

Recommended views:

- Rankings working view.
- Hidden schools review.
- Dossier index.
- Research queue.
- Methodology/reference.

For the first implementation pass, the research queue is optional follow-up. Do not delay screenshot QA, visibility controls, or minimal dossiers to build a full queue.

## Research Queue

The research queue should prioritize schools based on:

- high Decision Rank with low dossier completeness;
- target/likely admissions tier with missing personal-fit notes;
- high rank confidence but missing subjective review;
- low rank confidence but high potential value;
- schools in the top 75 that lack dossier status.

Suggested columns:

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

## Exports

Support browser-generated CSV exports:

- `selected_profile_rankings_export.csv`
- `school_visibility_export.csv`
- `school_dossier_edits_export.csv`

Exports should include:

- `export_schema_version`;
- generated timestamp;
- selector/profile assumptions when relevant;
- school IDs;
- stable headers;
- local browser state values.

Use ISO-8601 timestamps for `exported_at`.

## Import Is Future Scope

Do not implement import/writeback in the first pass.

Future import should be planned separately so exported CSVs can be reviewed and copied into `data/manual/` safely.

## Done Criteria

- User can identify schools needing research.
- User can edit local dossier fields.
- User can hide/restore schools.
- User can export current working state.
- Source-backed facts remain distinct from user-entered notes.
