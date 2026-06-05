# Scoring Engine Plan

## Objective

Generate transparent, scenario-aware rankings from separate data layers while preserving component scores and data coverage.

## Scope

This plan covers weighted scores, scenario models, dynamic tiers, data completeness, score explanations, and ranking output generation.

It does not cover a trained school-specific admissions probability model. That is future scope and is documented in [Predictive Admissions Model Future Scope](../PREDICTIVE_ADMISSIONS_MODEL_FUTURE_SCOPE.md).

## Inputs

- School master or generated aggregate.
- User preferences.
- Scenario weights.
- Applicant profiles.
- Normalized data layers.
- Manual judgment layers.

## Outputs

- `outputs/calculated_rankings.csv`
- Profile-specific ranking outputs.
- Scenario rank and score columns.
- Data coverage columns.
- Future score explanation columns.
- Data quality warnings.

The next executable implementation pass is [Headless Scoring Execution Plan](../HEADLESS_SCORING_EXECUTION_PLAN.md).

## Score Groups

Core score groups:

- Admissions Score
- Attendance Score
- Overall School Value
- Prestige Maximizer
- Lifestyle Maximizer
- Financial Maximizer
- Specialty Optionality
- Admissions Realist

Default weighting posture:

- Admissions realism and MCAT/GPA fit dominate the first narrowing pass.
- Cost and debt are low weight.
- Specialty fit is low weight.
- Hidden curriculum is low weight but visible.
- Geography and setting can be hard filters or soft scores.

## Source Policy

- Scoring formulas are source code and documentation.
- Component scores remain visible.
- Missing data is excluded from weighted average and reflected in coverage.
- Manual overrides require notes.
- Default committed builds must use public/template applicant profiles only.
- Private profile-derived outputs must be written only under ignored `outputs/private/`.

## Deterministic Formula Defaults

Phase 2B should start with these first-pass formulas:

- MCAT fit: `clamp(1, 10, 7 + (applicant_mcat_total - school_mcat) / 2)`.
- GPA fit: `clamp(1, 10, 7 + (applicant_overall_gpa - school_gpa) / 0.08)`.
- OOS/residency fit: same-state schools score 10; OOS-accepting schools score 6; explicit OOS-unfriendly schools score 1; unknown policy scores 4 with a warning.
- Cost score: lower applicant-relevant COA or tuition receives a higher percentile-derived 1-10 score.
- Partner fit: project partner-entered location, culture, four-year happiness, and regret scores directly; do not infer them.

These are fit scores, not acceptance probabilities.

## Implementation Steps

1. Keep current ranking builder as baseline.
2. Add schema validation before scoring.
3. Add multi-profile support.
4. Add profile-specific weights and hard filters.
5. Add scoring explanation fields.
6. Add data completeness penalties configurable by scenario.
7. Add tests for missing data behavior and tie ranking.
8. Keep predictive admissions probability out of scope until the future model plan is activated.

## Validation Rules

- Weights must be positive numbers.
- Score references must point to existing columns.
- Score values must be blank or between 1 and 10 unless documented otherwise.
- Scenario rankings must report coverage.
- Overall rank should not hide low coverage.

## Open Questions

- Should data completeness become a numeric penalty later, or remain warning/filter-only after Phase 2B?
- Should private/local outputs get a separate static site build mode after deterministic scoring works?
- Should workbook profile switching happen inside Google Sheets, or should local builds generate per-profile outputs?

## Definition of Done

- Rankings are reproducible.
- Every scenario score is traceable to weights and component columns.
- Rankings can be generated per applicant profile.
- Low data coverage is visible.
- Tests protect scoring behavior.
