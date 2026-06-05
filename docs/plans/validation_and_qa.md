# Validation and QA Plan

## Objective

Make data quality issues visible before rankings are trusted or shared.

## Scope

This plan covers schema validation, source metadata checks, score range checks, duplicate detection, workbook QA, and automated tests.

## Inputs

- All data CSVs.
- Normalized data layers.
- Manual inputs.
- Generated outputs.
- Workbook file.

## Outputs

- `outputs/data_quality_report.csv`
- CLI validation command.
- Test suite.
- Workbook QA checks.

## Validation Categories

- Schema: required columns exist.
- Identity: duplicate `school_id`, missing parent school, ambiguous campus.
- Source: missing source URL, stale source, missing confidence.
- Score: invalid range, missing high-priority score, unexplained override.
- Ranking: low data coverage, no scenario weights, broken formula references.
- Workbook: missing tab, mismatched row count, empty generated output.

## Source Policy

- Validation should not silently fix data.
- Validation should report severity: error, warning, info.
- Build should fail on structural errors.
- Build may warn on incomplete research data.

## Implementation Steps

1. Add validation module.
2. Add schema definitions for current CSVs.
3. Add `med-school-validate` command.
4. Add data quality report generation.
5. Add tests for ranking and workbook generation.
6. Wire validation into `med-school-build-all`.

## Validation Rules

Initial hard errors:

- Duplicate `school_id`.
- Missing required columns.
- Score outside 1-10.
- Exclusion flag true without exclusion reason.
- Scenario weight references unknown column.

Initial warnings:

- Missing source URL.
- Missing source last checked date.
- Ranking coverage below threshold.
- Final application row without rationale.

## Open Questions

- What ranking coverage threshold should trigger warnings?
- Should stale source age thresholds differ by data type?
- Should validation fail if workbook output is older than source CSVs?

## Definition of Done

- Build fails on structural data errors.
- Data quality report is generated every build.
- Tests cover scoring, workbook export, and validation.
- A reviewer can see which schools need more research.
