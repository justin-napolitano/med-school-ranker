# Headless Execution Plan: Phase 2B Deterministic Scoring

## Objective

Implement deterministic, profile-aware scoring from existing source-backed data and explicit human inputs.

This phase should make the rankings useful for first-pass school narrowing without pretending to be a school-specific acceptance probability model.

## Execution Mode

- Run non-interactively.
- Use existing committed source tables and normalized outputs.
- Do not fetch new network data.
- Do not scrape school pages.
- Do not implement predictive admissions probability.
- Do not commit real applicant/private data.
- Do not write private-derived results into committed public outputs.
- Keep missing data blank and visible.
- Preserve the current decision excluding Puerto Rico.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

Primary commands to preserve:

```bash
uv run med-school-build-all
uv run med-school-validate
uv run pytest
```

## Phase 2B Scope

### 1. Profile Loading

Default public-safe behavior:

- Load committed profiles from `data/applicant_profiles.csv`.
- Use the default profile when `is_default_profile=TRUE`.
- Public/template profiles may have blank MCAT/GPA values.

Optional local-private behavior:

- Support local private profile input from `data/manual/private/applicant_profiles.local.csv` or an explicit CLI/env selection if implemented.
- Private-derived outputs must go under `outputs/private/`.
- Private-derived outputs must not enter the workbook, site, upload bundle, or git unless the user explicitly requests an uncommitted local review build.

### 2. School Data Projection

Create an internal scoring projection keyed by `school_id` from:

- `data/school_master.csv`
- `data/normalized/admissions_stats.csv`
- `data/normalized/cost_and_debt.csv`
- `data/normalized/admissions_policies.csv`
- `data/manual/partner_inputs.csv`
- `data/user_preferences.csv`
- `data/scenario_weights.csv`
- `data/reference/aamc_mcat_gpa_acceptance_grid.csv`

Do not make `data/school_master.csv` the canonical home for imported GPA/MCAT or cost values. Use normalized layers at scoring time.

### 3. MCAT Fit Score

Use the applicant MCAT and the school's selected published MCAT average.

Preferred school MCAT input order:

1. `data/normalized/admissions_stats.csv` `published_mcat_average`
2. `mcat_mean_enrolled`
3. `mcat_median_matriculated`
4. `mcat_median_accepted`
5. Existing `data/school_master.csv` `median_mcat` only as a fallback

Formula:

```text
delta = applicant_mcat_total - school_mcat
admissions_mcat_fit_score = clamp(1, 10, 7 + delta / 2)
```

Interpretation:

- Applicant equal to school average: about 7.
- Applicant 4 MCAT points above school average: about 9.
- Applicant 6 or more MCAT points above school average: near 10.
- Applicant 4 MCAT points below school average: about 5.
- Applicant 8 or more MCAT points below school average: about 3 or lower.

Round to one decimal. If either value is missing, leave blank and add a missing-score warning.

### 4. GPA Fit Score

Use the applicant overall GPA and the school's selected published GPA average.

Preferred school GPA input order:

1. `data/normalized/admissions_stats.csv` `published_gpa_average`
2. `overall_gpa_mean_enrolled`
3. `overall_gpa_median_matriculated`
4. `overall_gpa_median_accepted`
5. Existing `data/school_master.csv` `median_gpa` only as a fallback

Formula:

```text
delta = applicant_overall_gpa - school_gpa
admissions_gpa_fit_score = clamp(1, 10, 7 + delta / 0.08)
```

Interpretation:

- Applicant equal to school average: about 7.
- Applicant 0.16 GPA above school average: about 9.
- Applicant 0.24 or more GPA above school average: near 10.
- Applicant 0.16 GPA below school average: about 5.
- Applicant 0.32 GPA below school average: about 3.

Round to one decimal. If either value is missing, leave blank and add a missing-score warning.

### 5. AAMC National Band Context

For each profile with MCAT and GPA:

- Determine the profile's AAMC MCAT band.
- Determine the profile's AAMC GPA band.
- Lookup the national AAMC acceptance-rate grid cell in `data/reference/aamc_mcat_gpa_acceptance_grid.csv`.

Output these as profile-context fields:

- `profile_aamc_mcat_band`
- `profile_aamc_gpa_band`
- `profile_aamc_acceptance_rate`
- `profile_aamc_acceptance_rate_band`

These are national MD applicant context fields. They are not school-specific acceptance probabilities.

### 6. Source Quality Fields

Carry these from `admissions_stats` into ranking outputs:

- `stats_data_quality_rank`
- `stats_data_quality_band`
- `stats_data_confidence`
- `stats_source_name`
- `stats_source_url`
- `published_mcat_band`
- `published_gpa_band`
- `published_mcat_average`
- `published_gpa_average`

Do not hide low-quality stats. Make them filterable and explainable.

Default Phase 2B behavior: source quality affects warnings and coverage, not the numeric fit score. Do not silently lower a score because a source is low quality.

### 7. OOS And Residency Fit

Use the applicant state of residence and available school policy fields.

State normalization:

- Accept full state names such as `Florida`.
- Convert to standard two-letter state abbreviation such as `FL`.

Default formula:

```text
if school_state == applicant_state:
    admissions_oos_friendliness_score = 10
elif accepts_oos is truthy:
    admissions_oos_friendliness_score = 6
elif accepts_oos is explicitly false:
    admissions_oos_friendliness_score = 1
else:
    admissions_oos_friendliness_score = 4
```

Add warning text when OOS policy is missing. Do not overfit this score until richer OOS acceptance data exists.

### 8. Cost And Debt Scores

Use `data/normalized/cost_and_debt.csv` where present.

Cost basis:

1. If school state equals applicant state and `estimated_coa_in_state` is present, use it.
2. Else if `estimated_coa_out_state` is present, use it.
3. Else if school state equals applicant state and `in_state_tuition_fees_insurance` is present, use it.
4. Else use `out_state_tuition_fees_insurance` if present.
5. Else leave cost score blank.

Score formula:

- Rank available cost basis values from lowest to highest.
- Lowest cost gets 10.
- Highest cost gets 1.
- Intermediate schools scale linearly.

```text
attendance_cost_score = 10 - 9 * percentile_rank
```

where `percentile_rank` is 0 for cheapest and 1 for most expensive.

Debt burden:

- If expected scholarship is present, subtract it from cost basis before scoring.
- If scholarship is missing, use the same basis as cost and mark the scholarship assumption blank.
- Keep cost/debt low weight by default.

### 9. Partner Input Projection

For matching `applicant_profile_id` and `school_id`, project:

- `could_live_here_4_years_score` to `four_year_happiness_score`
- `location_fit_score` to `attendance_location_score`
- `culture_fit_score` to `attendance_culture_score`
- `regret_index_score` to `regret_index_score`
- `hard_no_flag` and `hard_no_reason` to ranking outputs

Do not invent partner values. Missing partner values stay blank.

If `hard_no_flag` is true:

- Keep the school visible.
- Set `excluded_from_rank=TRUE`.
- Leave rank blank or move it below rankable schools.
- Preserve `hard_no_reason`.

### 10. Admissions And Attendance Scores

Continue using `data/user_preferences.csv` as the source of group weights.

Admissions Score inputs should include:

- `admissions_mcat_fit_score`
- `admissions_gpa_fit_score`
- `admissions_oos_friendliness_score`
- `admissions_mission_fit_score`
- `admissions_research_fit_score`
- `admissions_clinical_fit_score`

Attendance Score inputs should include:

- `attendance_prestige_score`
- `attendance_cost_score`
- `attendance_location_score`
- `four_year_happiness_score`
- `attendance_match_outcomes_score`
- `attendance_research_score`
- `attendance_culture_score`
- `attendance_curriculum_score`

Missing component scores should be excluded from weighted averages and reflected in coverage fields.

### 11. Tiering

Add admissions-only tier:

```text
admissions_fit_tier
```

Default labels:

- `Very High Risk`: admissions score below 4
- `Reach`: admissions score from 4 to below 5.5
- `Target`: admissions score from 5.5 to below 7.5
- `Likely`: admissions score 7.5 or higher
- `Unscored`: missing admissions score

Keep or add desire-aware application label:

```text
application_bucket
```

Default behavior:

- `Dream`: admissions fit is Very High Risk or Reach, and attendance score is at least 8.
- `Reach`: admissions fit is Reach.
- `Target`: admissions fit is Target.
- `Likely`: admissions fit is Likely.
- `Unscored`: missing required score.

### 12. Output Columns

Update public-safe ranking output with fields such as:

```text
applicant_profile_id
profile_name
profile_source
overall_rank
school_id
school_name
degree_type
city
state
admissions_fit_tier
application_bucket
suggested_funnel_bucket
overall_school_value
admissions_score
attendance_score
admissions_mcat_fit_score
admissions_gpa_fit_score
admissions_oos_friendliness_score
attendance_cost_score
four_year_happiness_score
regret_index_score
data_completeness_score
admissions_data_coverage
attendance_data_coverage
overall_data_coverage
profile_aamc_mcat_band
profile_aamc_gpa_band
profile_aamc_acceptance_rate
profile_aamc_acceptance_rate_band
published_mcat_average
published_gpa_average
published_mcat_band
published_gpa_band
stats_data_quality_rank
stats_data_quality_band
stats_data_confidence
cost_basis
cost_data_confidence
excluded_from_rank
hard_no_flag
hard_no_reason
missing_score_inputs
score_warnings
top_positive_drivers
top_negative_drivers
```

The exact column order may be adjusted for readability, but the worker should preserve traceability and coverage.

### 13. Scenario Scores

Continue using `data/scenario_weights.csv`.

For each scenario, output:

- `{scenario_key}_rank`
- `{scenario_key}_score`
- `{scenario_key}_coverage`

Scenario ranks should exclude `excluded_from_rank=TRUE` rows but keep those rows visible.

### 14. Site Updates

Update the static site to show:

- applicant profile selector if multiple public profiles exist
- admissions fit tier filter
- AAMC profile band context
- stats quality filters
- missing score input filter
- hard-no/excluded filter
- score warning badges
- top positive and negative drivers in the detail view

Do not include private profile data in committed site outputs.

### 15. Workbook Updates

Update workbook tabs as needed so the scoring fields are reviewable.

At minimum:

- `Calculated Rankings` should include the new scoring fields.
- `Applicant Profiles` remains public/template only.
- Private profile data must not be committed into workbook outputs.

### 16. Validation Updates

Extend validation to catch:

- invalid generated fit scores outside 1-10
- private paths included in upload bundle
- private paths included in site output
- ranking rows missing `applicant_profile_id`
- hard-no rows missing `hard_no_reason`
- scenario weights referencing missing score columns
- profile MCAT/GPA bands missing when profile stats are present

Warnings:

- school missing MCAT/GPA stats
- school missing cost basis
- school has low stats data quality
- score coverage below 50 percent

### 17. Tests

Add tests for:

- MCAT fit formula
- GPA fit formula
- applicant state normalization, including Florida to FL
- OOS score cases
- cost percentile scoring
- missing inputs remain blank and produce warnings
- hard-no rows stay visible but are excluded from rank
- scenario ranks exclude hard-no rows
- private profile files are not included in public site or upload bundle
- build-all and site generation still pass

## Required Verification

Run:

```bash
uv run med-school-build-all
uv run pytest
git status --short
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

Verify:

- `outputs/calculated_rankings.csv` exists.
- Ranking rows include `applicant_profile_id`.
- Missing stats remain blank rather than zero.
- Stats quality fields are present and filterable.
- Applicant AAMC band context is present when profile stats exist.
- Florida residency normalizes to `FL` in private/local mode if implemented.
- Site and workbook regenerate.
- Upload bundle excludes private paths.
- Tests pass.

## Do Not Do

- Do not scrape more admissions data.
- Do not download raw AAMC files.
- Do not train or simulate a predictive admissions model.
- Do not turn AAMC national acceptance grid cells into school-specific probabilities.
- Do not invent subjective prestige, culture, curriculum, match, happiness, or regret scores.
- Do not commit private applicant profile values.
- Do not publish private scoring outputs.

## Definition Of Done

Phase 2B is done when:

- Deterministic profile-aware scoring is implemented.
- MCAT/GPA fit, OOS fit, cost score, partner inputs, and scenario weights flow into rankings.
- Admissions score and attendance score remain separate.
- Admissions-only tiers and desire-aware application buckets are both visible.
- Data quality and missing inputs are visible.
- Public committed outputs are safe.
- Optional private outputs, if implemented, stay ignored.
- `uv run med-school-build-all` and `uv run pytest` pass.
