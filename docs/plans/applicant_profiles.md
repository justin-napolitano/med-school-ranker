# Applicant Profiles Plan

## Objective

Support multiple applicant profiles so the same school universe can be ranked for different applicants, assumptions, and weighting strategies.

## Scope

This plan covers applicant stats, residency, geography filters, profile-specific weights, hard filters, soft preferences, and partner-facing spreadsheet inputs.

## Inputs

- Applicant MCAT and GPA values.
- Applicant residency and geography constraints.
- Applicant preference weights.
- Applicant-specific hard filters.
- Partner-entered personal fit and normative preference scores.

## Outputs

- `data/applicant_profiles.csv`
- `data/manual/private/applicant_profiles.local.csv`
- Generated profile-specific rankings.
- Workbook tabs for editable profile inputs.

## Schema

Recommended public/template fields:

- `applicant_profile_id`
- `profile_name`
- `is_default_profile`
- `mcat_total`
- `overall_gpa`
- `science_gpa`
- `state_of_residence`
- `preferred_setting`
- `urban_preference_score`
- `rural_tolerance_score`
- `specialty_interest`
- `target_application_count`
- `cost_weight_level`
- `hidden_curriculum_weight_level`
- `specialty_weight_level`
- `notes`

Private/local fields may include more specific personal preferences and should stay out of git by default.

## Source Policy

- Applicant-entered data is manual and private by default.
- Commit templates and fake example profiles only.
- Real applicant profiles live in ignored local files unless the user explicitly chooses otherwise.
- Private-derived outputs must live under ignored `outputs/private/`.
- Public committed builds must not include private applicant stats or private-derived score outputs.

## Implementation Steps

1. Add public applicant profile template.
2. Add ignored local private profile path.
3. Update scoring engine to select or iterate over applicant profiles.
4. Add profile-specific weight sets.
5. Add workbook input tabs for profile fields and partner-entered manual scores.
6. Generate rankings per profile or per selected active profile.
7. Add a local-private scoring mode only if its outputs are ignored and excluded from the upload bundle.

## Validation Rules

- `applicant_profile_id` is required and unique.
- MCAT must be blank or between 472 and 528.
- GPA must be blank or between 0 and 4.0.
- `target_application_count` defaults to 25 if blank.
- Hard filters must be explicit and reviewable.

## Current Defaults

- Support multiple profiles from the beginning.
- Keep real profile data local and ignored.
- Default target application count is 25.
- Default setting preference favors urban schools.
- Emergency medicine is the current specialty interest, but low weight.
- Cost and debt are low weight.
- Hidden curriculum is tracked for awareness but low weight by default.

## Open Questions

- Should the workbook allow profile switching inside Google Sheets, or should each build output one workbook per profile?
- Should partner-entered scores be stored in a separate tab from applicant facts?
- Should hard filters be applied before ranking, after ranking, or displayed as warnings?

## Definition of Done

- Multiple profiles can be represented without duplicating the school universe.
- Private applicant data is ignored by git.
- Rankings can be generated per profile.
- The workbook gives the partner a simple place to enter or adjust normative values.
