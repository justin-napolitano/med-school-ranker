# Cost and Debt Plan

## Objective

Track tuition, total cost of attendance, expected scholarships, fees, and debt sensitivity separately from general attendance preference.

## Scope

This plan covers in-state and out-of-state tuition, fees, health insurance, total cost of attendance, expected scholarships, cost of living, debt burden score, and application fees where useful.

## Inputs

- AAMC public tuition and fee reports where allowed.
- School financial aid and tuition pages.
- AACOM or school-specific DO cost pages.
- Manual scholarship assumptions.
- Applicant residency status assumptions.
- Current AAMC MSAR tuition parse and school-master patch candidates in `data/source_tables/`.

## Outputs

- `data/normalized/cost_and_debt.csv`
- Derived `attendance_cost_score`
- Derived `debt_burden_score`
- Workbook cost/debt columns and source links.

## Schema

Recommended fields:

- `school_id`
- `tuition_year`
- `in_state_tuition_fees_insurance`
- `out_state_tuition_fees_insurance`
- `estimated_coa_in_state`
- `estimated_coa_out_state`
- `expected_scholarship`
- `application_fee`
- `secondary_fee`
- `deposit_amount`
- `average_grad_indebtedness`
- `residency_assumption`
- `debt_burden_score`
- source metadata fields

## Source Policy

- Prefer direct school cost pages when current and clear.
- Public AAMC tuition reports can be used if usage rights are clear.
- Scholarship estimates are assumptions and must be labeled as manual.
- Cost values must specify year and residency basis.
- AAMC MD tuition rows can populate normalized cost data only when the school match is exact, or when a high-confidence match has a clear second-match gap.
- AAMC rows with all-zero costs, Puerto Rico rows, Canadian/province rows, and review/no-match rows must go to source review.
- DO tuition must remain blank until a DO-specific or school-specific source is added.

## Current Source Drop

The current AAMC MSAR tuition source tables provide a strong MD baseline, but they are not yet integrated into normalized cost data.

- Parsed tuition rows: 176.
- U.S. rows: 163.
- Canadian/province rows: 13.
- Patch candidate rows before ambiguity and zero-cost re-audit: 156.
- Safe rows after second-match gap and zero-cost review: 151.
- Ambiguous high-confidence rows requiring review: 2.
- Exact-match all-zero rows requiring review: 3.
- Additional active MD rows needing source/match review: 3.
- DO rows still missing tuition coverage: 74.

Phase 2A should normalize only the post-audit safe rows and create review queue rows for everything else.

## Implementation Steps

1. Add cost and debt normalized schema.
2. Add manual import template.
3. Add source fields to distinguish tuition, COA, and debt sources.
4. Add debt burden formula using COA minus expected scholarships.
5. Add scenario scoring for financial maximizer.
6. Keep default cost/debt influence low unless the active applicant profile changes it.
7. Add `outputs/cost_and_debt_candidates.csv` and `outputs/cost_and_debt_review.csv`.
8. Add cost coverage and source confidence to workbook and site outputs.

## Validation Rules

- Dollar values must be numeric or blank.
- `tuition_year` is required when a cost value is present.
- In-state and out-of-state fields must not be swapped without a warning.
- Manual scholarship values require notes.

## Open Questions

- Should projected four-year debt assume annual tuition inflation?
- Should cost of living be source-derived or manual judgment?
- How should public school in-state preference be modeled for nonresident applicants?

## Current Defaults

- Cost and debt are tracked for awareness.
- Cost and debt are low-weight in the default ranking.
- Financial maximizer scenario remains available as an alternative view.

## Definition of Done

- Cost data is separate from preference scores.
- Debt burden formula is documented.
- Cost sources and years are visible in workbook.
- Ranking scenarios can use cost without overwriting personal preference.
