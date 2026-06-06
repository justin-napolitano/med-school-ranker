# Numeric and Currency Formatting

## Purpose

Prevent spreadsheet-shaped numbers from appearing in applicant-facing cards and profile sections.

## Requirements

- Cost-like fields display as whole-dollar currency.
- Missing or zero-equivalent cost data displays as `Missing`.
- In-state and out-of-state values are displayed separately where the user is comparing cost.
- A separate `Cost used for selected score` row may be shown when the scoring model used a specific cost basis.

## Cost Field Coverage

Format these fields as currency on visible card/profile surfaces:

- `estimated_coa_in_state`
- `estimated_coa_out_state`
- `in_state_tuition_fees_insurance`
- `out_state_tuition_fees_insurance`
- `cost_basis`
- generated node aliases such as `in_state` and `out_state`

## Guardrails

- Do not infer currency values from unrelated fields.
- Do not average costs in the UI.
- Do not mutate source CSV values during display formatting.

