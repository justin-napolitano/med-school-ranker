# Predictive Admissions Model Future Scope

## Status

Future scope. This is intentionally not part of the current scoring pass.

The current scoring model should remain a transparent fit-and-risk model based on applicant GPA/MCAT, school-level source averages, data-quality bands, cost, geography, and manually reviewed fit factors. It should not claim to predict the applicant's true probability of admission.

## Objective

Build a calibrated, evidence-backed admissions prediction model only after the project has enough reliable applicant-outcome data to support it.

The predictive model would answer a narrower question than the ranking model:

> Given a specific applicant profile and a specific school, what is the estimated probability range of receiving an acceptance?

That estimate would be shown as a confidence-calibrated range, not as a definitive chance.

## Why This Is Out of Current Scope

The current project does not yet have the data needed for credible prediction:

- No applicant-specific outcome history for the partner.
- No structured dataset of school applications, interviews, waitlists, and acceptances for comparable applicants.
- Limited school-specific OOS and residency preference data.
- Limited mission-fit, activity-fit, clinical-hour, research-hour, and service-hour data.
- No essay, recommendation, timing, or interview-performance features.
- Current GPA/MCAT data is third-party published average data, not official school-level applicant distribution data.

Implementing prediction now would create false precision. A school-specific score like `23%` would look scientific while depending on incomplete and noisy inputs.

## Current Scope Boundary

Current scope:

- Academic fit score.
- MCAT/GPA delta score.
- AAMC national MCAT/GPA band context.
- OOS friendliness score when sourced.
- Mission/clinical/research fit as explicit manual or source-backed scores.
- Data-quality-adjusted fit scores.
- Dynamic labels such as `likely`, `target`, `reach`, and `high reach`.

Out of current scope:

- School-specific acceptance probability.
- Model-trained probability estimates.
- Black-box ranking.
- Predictions that use unreviewed, missing, or inferred applicant attributes.

## Required Data Before Modeling

Minimum viable predictive dataset:

- Applicant-level applications with outcomes:
  - applied
  - secondary received
  - interview invite
  - waitlist
  - acceptance
  - rejection
- Applicant academic features:
  - MCAT total and subsection scores
  - cumulative GPA
  - science GPA
  - trend if available
- Applicant context:
  - state of residence
  - school in-state or OOS status
  - disadvantaged, first-generation, military, rural, or mission-relevant context if the applicant chooses to model it
- Activity profile:
  - clinical hours
  - shadowing hours
  - volunteering/service hours
  - research hours/publications
  - leadership
  - paid employment
- School features:
  - public/private
  - in-state preference
  - OOS matriculant share
  - class size
  - mission tags
  - average GPA/MCAT
  - tuition/COA
  - application volume and interview volume if available
- Application process features:
  - application submission date
  - secondary turnaround time
  - interview format
  - letter requirements satisfied

The model should not train directly on private data committed to git. Any applicant-level training data should live under `data/manual/private/` or another ignored local/private path.

## Candidate Model Progression

### Phase 1: Transparent Heuristic Baseline

This is the current planned direction.

Use deterministic formulas:

- MCAT delta against school average.
- GPA delta against school average.
- OOS friendliness.
- public/private and state-residency fit.
- mission/research/clinical fit if reviewed.
- data-quality adjustment.

Output:

- fit score
- risk band
- explanation fields

This is not predictive probability.

### Phase 2: Calibrated Logistic Model

Only after collecting enough structured outcome data.

Possible model:

- logistic regression
- regularized logistic regression
- calibrated gradient-boosted trees if data volume is sufficient

Benefits:

- interpretable baseline
- easier calibration
- less false precision than more complex models

Output should be:

- probability range
- calibration confidence
- top positive drivers
- top negative drivers
- missing feature warnings

### Phase 3: Hierarchical School-Aware Model

Only if there is enough data by school and applicant group.

Possible approach:

- school-level intercepts
- state-residency interactions
- public/private interactions
- academic-fit interaction terms

This would help avoid treating Harvard, UCF, FIU, and UF as if they respond identically to MCAT/GPA deltas.

### Phase 4: Scenario and Sensitivity Layer

Add controlled "what-if" analysis:

- What if MCAT were 2 points higher?
- What if application timing improves?
- What if clinical hours are stronger?
- What if only Florida schools are considered?

This should still show uncertainty and assumptions.

## Calibration Requirements

A predictive model is not acceptable unless it is calibrated.

Required checks:

- reliability curve
- Brier score
- calibration by probability bucket
- performance by school type
- performance by in-state vs OOS
- residual review for overconfident predictions

The model should report probability ranges, for example:

- `low confidence: 10-25%`
- `medium confidence: 25-40%`
- `high confidence: 40-55%`

Avoid presenting single-point percentages as final truth.

## Evaluation Requirements

Minimum evaluation outputs:

- cross-validation split by applicant cycle when possible
- holdout test set
- ROC-AUC as a secondary metric
- precision/recall for interview and acceptance outcomes
- calibration metrics as primary decision-safety metrics
- subgroup/fairness audit if sensitive or proxy features are included

Because medical admissions data is noisy and holistic, calibration and explanation matter more than raw ranking accuracy.

## Ethical and Practical Constraints

- The model is decision support, not a promise or gatekeeper.
- Do not optimize only for probability of acceptance if it pushes the applicant toward schools they would dislike.
- Do not hide missing data.
- Do not use sensitive attributes without an explicit reason, user consent, and a fairness review.
- Keep model inputs inspectable.
- Keep manual overrides visible.
- Never overwrite the current transparent scoring model with a black-box output.

## Output Design

If implemented later, predictive outputs should live in a separate file:

```text
data/normalized/predictive_admissions_estimates.csv
```

Recommended columns:

- `applicant_profile_id`
- `school_id`
- `school_name`
- `model_version`
- `prediction_target`
- `probability_low`
- `probability_mid`
- `probability_high`
- `calibration_band`
- `model_confidence`
- `top_positive_drivers`
- `top_negative_drivers`
- `missing_critical_features`
- `do_not_use_for_ranking_flag`
- `source_training_dataset`
- `created_date`
- `notes`

The ranking UI should display predictive estimates as one optional lens, not as the default source of truth.

## Readiness Checklist

Do not start implementation until all are true:

- Applicant profile schema includes academic, residency, activity, and timing fields.
- School-level OOS friendliness and public/private residency preference data exist for most schools.
- Outcome training data has clear provenance and permission to use.
- Current deterministic fit scoring is implemented and validated.
- The project has a model-card template.
- The user explicitly chooses to proceed with predictive modeling.

## Definition of Done

A future predictive model is acceptable only when:

- It is calibrated.
- It is documented with a model card.
- Its inputs are auditable.
- It reports uncertainty.
- It preserves the transparent deterministic score.
- It never commits private applicant-level training data.
