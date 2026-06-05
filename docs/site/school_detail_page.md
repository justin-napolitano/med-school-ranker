# Site Plan: School Detail Page

## Objective

Show all review context for one selected school without forcing the user to scan many workbook columns.

## Inputs

- `school_master.json`
- `calculated_rankings.json`
- `partner_inputs.json`
- `admissions_source_queue.json`
- `admissions_stats.json`
- `data_quality_report.json`

## Sections

### Identity

- school name
- degree type
- city/state
- parent school
- campus name
- accreditation status
- source name and URL

### Ranking Context

- overall rank
- dynamic tier
- funnel bucket
- admissions score
- attendance score
- scenario scores/ranks
- data completeness score

### Partner Review

- could live here 4 years
- location fit
- culture fit
- regret index
- hard-no flag and reason
- partner notes

### Admissions Research

- admissions source queue status
- candidate source URL
- admissions stats values if present
- source confidence
- notes

### Data Quality

- all warnings/errors for this school
- suggested fixes

## Interactions

- Open from any school row.
- Previous/next selected school navigation.
- Copy school ID or source URL in later pass.

## Non-Goals

- No editing in detail page for first pass.
- No live source fetching.

## Definition of Done

- Every school can render a detail page/panel.
- Missing sections show clear empty states.
- Source and data quality context are visible.
- Partner inputs are visually separate from sourced facts.
