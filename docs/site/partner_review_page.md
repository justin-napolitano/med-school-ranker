# Site Plan: Partner Review Page

## Objective

Give the partner-facing review inputs a quick browser view so the user can inspect subjective/normative fields without opening the workbook.

## Inputs

- `partner_inputs.json`
- `school_master.json`
- `calculated_rankings.json`

## Primary Table

Columns:

- school name
- degree type
- city
- state
- could live here 4 years
- location fit
- culture fit
- regret index
- hard-no flag
- hard-no reason
- partner notes

## Filters

- Missing partner input.
- Hard-no schools.
- High regret index.
- Low four-year liveability.
- Degree type.
- State.

## Interactions

- Click a row to open School Detail.
- Export/filter copy is later-pass only.

## Static First-Pass Rule

This page is read-only. The workbook remains the place to enter partner scores.

## Definition of Done

- The page clearly shows which schools still need partner review.
- Hard-no schools are easy to spot.
- Subjective fields are not mixed with source-derived facts.
