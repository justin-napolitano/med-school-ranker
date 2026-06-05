# Admissions Probability Plan

## Objective

Model admissions realism separately from desire to attend, using applicant fit against school stats and policies.

## Scope

This plan covers MCAT fit, GPA fit, OOS friendliness, mission fit, research fit, clinical fit, regional preference, and application risk.

School-specific predictive probability is explicitly out of current scope. The future design is documented separately in [Predictive Admissions Model Future Scope](../PREDICTIVE_ADMISSIONS_MODEL_FUTURE_SCOPE.md).

## Inputs

- Applicant profile values.
- Admissions stats layer.
- Application policies and residency rules.
- School mission statements.
- Manual applicant-school fit assessments.

## Outputs

- `admissions_score`
- Component fit scores in `School Master`
- Dynamic tiers such as Dream, Reach, Target, and Likely.
- Explanation fields for admissions risk.

## Schema

Recommended fields:

- `admissions_mcat_fit_score`
- `admissions_gpa_fit_score`
- `admissions_oos_friendliness_score`
- `admissions_mission_fit_score`
- `admissions_research_fit_score`
- `admissions_clinical_fit_score`
- `admissions_probability_override`
- `admissions_fit_notes`
- source metadata for any non-manual policy value

## Source Policy

- Quantitative fit should use admissions stats layer, not direct free-text notes.
- OOS friendliness should be source-based where possible.
- Mission, research, and clinical fit can be manual but must remain explicit human judgment.
- Overrides require notes.

## Implementation Steps

1. Use applicant profile file for MCAT, GPA, residency, geography, mission themes, research profile, and clinical profile.
2. Prioritize derived MCAT/GPA fit scores from admissions stats.
3. Add OOS friendliness source fields.
4. Keep mission/research/clinical fit as manual 1-10 scores initially.
5. Improve tier logic once enough component data exists.

## Validation Rules

- Fit scores must be blank or between 1 and 10.
- Overrides require notes.
- Admissions score coverage should be reported.
- Any school with low data coverage should show a warning.

## Open Questions

- Should admissions tiers be based on 1-10 fit scores or broad risk bands?
- How should mission-heavy public schools be handled?
- Should the system recommend minimum numbers of likely, target, reach, and dream applications?

## Current Defaults

- Admissions realism is the first-order screen.
- MCAT and GPA fit should drive the earliest narrowing pass.
- OOS friendliness matters, but should not overpower MCAT/GPA fit without clear evidence.
- The first target is a balanced list of about 25 applications.

## Definition of Done

- Admissions Score can be calculated without Attendance Score.
- Component scores are visible and editable.
- Dynamic tiers are explainable.
- Low-confidence admissions estimates are flagged.
