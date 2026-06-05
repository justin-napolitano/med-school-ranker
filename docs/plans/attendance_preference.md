# Attendance Preference Plan

## Objective

Model how much the applicant would want to attend a school if accepted, separate from admissions probability.

## Scope

This plan covers prestige, location, match outcomes, research, culture, curriculum, four-year happiness, regret index, setting preference, demographic/community context, and lifestyle subcomponents.

## Inputs

- Manual applicant preferences.
- Researched school notes.
- Curriculum and hidden curriculum layers.
- Cost and debt layer.
- Residency and match layer.

## Outputs

- `attendance_score`
- `four_year_happiness_score`
- `regret_index_score`
- Lifestyle and fit component scores.
- Scenario rankings for lifestyle and balanced preference.

## Schema

Recommended fields:

- `attendance_prestige_score`
- `attendance_cost_score`
- `attendance_location_score`
- `setting_type`
- `urban_rural_suburban_score`
- `demographic_context_score`
- `attendance_match_outcomes_score`
- `attendance_research_score`
- `attendance_culture_score`
- `attendance_curriculum_score`
- `four_year_happiness_score`
- `regret_index_score`
- `weather_score`
- `social_life_score`
- `dating_score`
- `outdoor_activities_score`
- `airport_access_score`
- `cost_of_living_score`
- `political_cultural_fit_score`
- `family_access_score`

## Source Policy

- Personal preference scores are human judgment, not objective truth.
- Keep lifestyle components separate so a single city score is not overloaded.
- Source-derived facts can inform manual scores but should not overwrite them silently.

## Implementation Steps

1. Keep existing preference columns in `School Master`.
2. Add manual research template for lifestyle, city setting, demographic/community context, and personal fit.
3. Add optional notes fields for high-impact subjective scores.
4. Add hard-filter and soft-score support for geography.
5. Add scenario weights that can emphasize lifestyle or regret.
6. Add workbook instructions for scoring consistently.

## Validation Rules

- All preference scores must be blank or between 1 and 10.
- High regret index with low attendance score should be flagged for review.
- Schools in final application list should have four-year happiness populated.

## Open Questions

- Should regret index be part of overall score or only a separate warning?
- Should location score be decomposed entirely into lifestyle components?
- Should some lifestyle components be applicant-specific yes/no filters rather than scores?

## Current Defaults

- Urban schools are preferred.
- Geography can be both a hard filter and a soft score.
- Demographic/community context should be tracked separately from simple location desirability.
- Partner-entered normative scores should be easy to update in the workbook.

## Definition of Done

- Attendance Score is separate from Admissions Score.
- Lifestyle and regret fields are visible.
- Subjective scores are labeled as human judgment.
- Final application candidates have enough preference data to defend the decision.
