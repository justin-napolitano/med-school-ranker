# Site Plan: Dashboard Page

## Objective

Provide the first-screen summary for rapid review of the medical school universe, data completeness, and next research actions.

## Inputs

- `school_master.json`
- `calculated_rankings.json`
- `data_quality_report.json`
- `admissions_source_queue.json`
- `partner_inputs.json`

## Sections

### Summary Metrics

Cards or compact metric cells:

- Total active schools
- MD count
- DO count
- Schools with partner input
- Schools with hard-no flag
- Data quality errors
- Data quality warnings
- Admissions source URLs found

### Top Research Priorities

Table of schools needing attention:

- school name
- degree type
- city/state
- missing source URL flag
- data quality warning count
- partner input missing flag
- next action

### Current Ranking Snapshot

Small table:

- overall rank
- school name
- degree type
- city/state
- admissions score
- attendance score
- data coverage

## Interactions

- Click a metric to filter related page.
- Click a school row to open School Detail.
- Search filters all school tables on the page.

## Table Columns

Research priority table:

- `school_name`
- `degree_type`
- `city`
- `state`
- `candidate_source_url`
- `warning_count`
- `partner_input_status`
- `suggested_next_action`

Ranking snapshot:

- `overall_rank`
- `school_name`
- `degree_type`
- `city`
- `state`
- `dynamic_tier`
- `overall_school_value`
- `data_completeness_score`

## Definition of Done

- Dashboard loads without requiring scores to be populated.
- Counts match source JSON.
- It is obvious which schools need research next.
- Clicking a school opens or navigates to detail.
