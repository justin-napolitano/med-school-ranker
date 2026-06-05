# Workbook and Export Plan

## Objective

Produce a Google Sheets-ready XLSX workbook that is useful for review, collaboration, filtering, and decision-making without becoming the hidden source of truth.

## Scope

This plan covers workbook tabs, formatting, upload bundle, CSV exports, instructions, and future workbook QA.

## Inputs

- Generated CSVs.
- Source summary.
- Field definitions.
- Data quality report.
- Project docs.

## Outputs

- `outputs/med_school_ranker.xlsx`
- `med-school-ranker-upload.zip`
- Google Sheets-compatible tabs.
- Future workbook QA report.

## Workbook Tabs

Current tabs:

- Instructions
- School Master
- User Preferences
- Scenario Weights
- Calculated Rankings
- Final Application List
- Sources
- Field Definitions

Future tabs:

- Data Quality
- Model Assumptions
- Change Log
- Applicant Profile
- Partner Inputs
- Profile Rankings
- Research Queue

## Source Policy

- Workbook should show source links and source dates.
- Generated tabs should be marked as generated.
- Manual-input tabs should be clear and editable.
- The workbook should not contain hidden formulas that contradict the repo scoring code.
- Partner-facing input tabs should expose simple fields without requiring the reviewer to understand the full data model.

## Implementation Steps

1. Keep XLSX builder as primary export path.
2. Add partner-facing input tabs for applicant profile, weights, hard filters, and manual scores.
3. Add Data Quality tab once validation exists.
4. Add Model Assumptions and Change Log tabs.
5. Add workbook smoke tests for sheet names, row counts, and required columns.
6. Improve formatting for filters, frozen rows, widths, and hyperlinks.

## Validation Rules

- Workbook must contain all expected tabs.
- School Master and Calculated Rankings row counts must match.
- Required sheets must not be empty.
- Hyperlinks should remain clickable where possible.

## Open Questions

- Should Google Sheets formulas be added, or should all calculations stay in Python?
- Should some tabs be protected or marked read-only in instructions?
- Should the workbook include a printable summary tab?

## Current Defaults

- The workbook is a partner-facing report and input surface.
- The partner should be able to plug in values and see scores change where practical.
- The repo remains the canonical build system; spreadsheet formulas may be added for interactive review if they mirror the documented scoring model.

## Definition of Done

- One command produces a review-ready workbook.
- Workbook imports cleanly into Google Sheets.
- Generated and manual tabs are clearly distinguished.
- Workbook QA catches missing tabs or broken row counts.
