# Headless Score Cards Simplification Plan

## Worker Goal

Make the Score Cards tab and school profile pages applicant-friendly without changing ranking formulas, source normalization, or stable dossier export schemas.

## Required Context

Read first:

- `docs/SCORE_CARDS_SIMPLIFICATION_EXEC_PLAN.md`
- `docs/site/score_cards_simplification/CRITICAL_REVIEW.md`
- `src/med_school_ranker/site.py`
- `tests/test_phase1.py`

## Implementation Steps

1. Start with a clean status check.
2. Keep current internal `dossier` identifiers stable.
3. Simplify `renderDossiers()` into a school-browser table with applicant-facing columns.
   - Show all schools by default.
   - Primary filters: status, admissions tier, state, degree, and data quality.
   - Hide hard-no schools from the primary view for now.
4. Simplify `renderProfile()` so the first viewport is a school profile, not an audit dashboard.
5. Keep review controls limited to status and compare in this slice.
6. Move export/source/missing-field/data-quality details into collapsed sections.
   - For MCAT/GPA gaps, distinguish approved canonical values, candidate-only values, and no candidate value found.
7. Rebuild the site.
8. Run tests and validation.
9. Verify:
   - Score Cards tab;
   - one school profile;
   - status switch;
   - compare action;
   - missing MCAT/GPA explanation labels;
   - local export.

## Guardrails

- Do not remove transparency; collapse it.
- Do not hide missing data completely.
- Do not rename CSV schemas.
- Do not change score math.
- Do not change source normalization or promote candidate admissions-stat values in this slice.
- Do not add notes UI in this slice.
- Do not migrate frameworks.

## Headless Prompt

```text
You are in /Users/justin/repos/med-school-ranker. Execute the Score Cards Simplification plan. Make the Score Cards tab and school profile pages applicant-facing: simple school-browser table showing all schools by default, clean school profile header, At a Glance, Why It Ranks Here bullets, simple status/compare review controls, and collapsed Data Details. Keep internal dossier schemas and exports stable. Do not add notes UI in this slice. Do not change scoring formulas or source normalization. For missing MCAT/GPA, explain whether the school has an approved canonical value, candidate-only evidence, or no candidate value found. Rebuild the site, run tests and validation, and commit the implementation.
```
