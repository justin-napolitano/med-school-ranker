# Site Plan: Rankings Page

## Objective

Provide the main review table for comparing schools and narrowing the universe toward the application list.

Rankings is the highest-priority table for Phase 1.5A. If implementation tradeoffs are needed, polish this table before lower-priority pages.

## Inputs

- `calculated_rankings.json`
- `school_master.json`
- `partner_inputs.json`
- `data_quality_report.json`

## Primary Table

Columns:

- overall rank
- school name
- degree type
- city
- state
- dynamic tier
- suggested funnel bucket
- overall school value
- admissions score
- attendance score
- regret index score
- data completeness score
- warning count
- hard-no flag
- partner notes indicator

## Filters

- Search by school/city/state.
- Degree: MD, DO.
- State.
- Dynamic tier.
- Funnel bucket.
- Hard-no status.
- Data quality warnings present.
- Partner input present.

## Sorting

Default sort:

1. Overall rank when populated.
2. School name.

Alternate sorts:

- admissions score descending
- attendance score descending
- data completeness descending
- warning count descending
- state/city

## Interactions

- Click school name to open detail.
- Toggle visible columns in later pass.
- Select multiple rows for future comparison drawer in later pass.
- Do not implement comparison in the first pass; reserve it for Phase 1.5B.

## Empty/Unscored State

Because many scores are blank early, the table must still be useful:

- Show unscored schools.
- Explain blank score fields as missing/not researched.
- Do not hide unranked schools by default.

## Definition of Done

- Table shows all active schools.
- Rankings table receives the most complete filtering/sorting polish in Phase 1.5A.
- Filters work together.
- Sort behavior is stable.
- Unscored rows remain visible.
- Data quality badges or counts are visible.
