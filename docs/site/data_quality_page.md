# Site Plan: Data Quality Page

## Objective

Make validation warnings and errors easy to inspect, filter, and connect back to affected schools or data files.

## Inputs

- `data_quality_report.json`
- `school_master.json`

## Primary Table

Columns:

- severity
- file
- row id
- field
- message
- suggested fix
- linked school name when row id matches a school

## Filters

- Severity: error, warning, info.
- File.
- Field.
- School row.
- Message search.

## Summary Metrics

- error count
- warning count
- warnings by file
- warnings by field
- schools with most warnings

## Interactions

- Click a school-related warning to open School Detail.
- Click file filter to narrow issue type.

## Definition of Done

- Validation report is visible in the site.
- Errors and warnings are distinguishable.
- Warnings can be traced to school or file context.
- The page remains useful with hundreds of expected warnings.
