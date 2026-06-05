# Headless Execution Plan: Phase 1 Infrastructure

## Objective

Execute Phase 1 infrastructure without human follow-up. This phase turns the current seed into a safer multi-profile project with templates, validation, data quality reporting, and partner-facing workbook tabs.

## Execution Mode

- Run non-interactively.
- Make conservative assumptions from this document and the planning docs.
- Do not scrape or populate GPA/MCAT data in this phase.
- Do not commit real applicant/private data.
- Preserve existing user or generated work unless explicitly updating generated outputs.
- Stop and report if validation or tests expose a structural conflict that cannot be resolved without changing project scope.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

Primary command to preserve:

```bash
uv run med-school-build-all
```

## Phase 1 Scope

### 1. Data Layer Folders

Create and preserve:

```text
data/raw/
data/normalized/
data/manual/
data/manual/private/
```

Keep `data/manual/private/` ignored by git. If empty directories need placeholders, use `.gitkeep` outside private paths only.

### 2. Applicant Profile Templates

Add:

```text
data/applicant_profiles.csv
data/manual/applicant_profiles.example.csv
```

Do not add real applicant data.

Minimum fields:

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

### 3. Admissions Stats Template

Add:

```text
data/normalized/admissions_stats.csv
```

Minimum fields:

- `school_id`
- `school_name`
- `degree_type`
- `stats_cohort_year`
- `metric_population`
- `metric_type`
- `mcat_median_accepted`
- `mcat_median_matriculated`
- `mcat_mean_enrolled`
- `mcat_10th_percentile`
- `mcat_25th_percentile`
- `mcat_75th_percentile`
- `mcat_90th_percentile`
- `overall_gpa_median_accepted`
- `overall_gpa_median_matriculated`
- `overall_gpa_mean_enrolled`
- `science_gpa_mean_enrolled`
- source metadata fields

Leave metric rows blank or template-only unless values are already source-verified.

### 4. Admissions Source Queue

Add:

```text
data/manual/admissions_source_queue.csv
```

Purpose: track public admissions profile pages to review or import later.

Minimum fields:

- `school_id`
- `school_name`
- `degree_type`
- `candidate_source_url`
- `source_status`
- `extraction_status`
- `review_status`
- `last_checked`
- `notes`

Seed one row per school from `data/school_master.csv` with blank source URL/status fields.

### 5. Partner-Facing Inputs

Add:

```text
data/manual/partner_inputs.csv
```

Minimum fields:

- `applicant_profile_id`
- `school_id`
- `school_name`
- `could_live_here_4_years_score`
- `location_fit_score`
- `culture_fit_score`
- `regret_index_score`
- `hard_no_flag`
- `hard_no_reason`
- `partner_notes`

Seed one row per school for the default/template profile with blank scores.

### 6. Validation Command

Add CLI command:

```bash
uv run med-school-validate
```

Validation should produce:

```text
outputs/data_quality_report.csv
```

Report columns:

- `severity`
- `file`
- `row_id`
- `field`
- `message`
- `suggested_fix`

Initial hard errors:

- duplicate `school_id` in `data/school_master.csv`
- missing required columns
- score outside `1-10`
- exclusion flag true without `exclusion_reason`
- scenario weight references unknown column
- applicant profile MCAT outside `472-528`
- applicant profile GPA outside `0-4.0`
- admissions stats MCAT outside `472-528`
- admissions stats GPA outside `0-4.0`

Initial warnings:

- missing source metadata where relevant
- blank admissions source queue URL
- low ranking coverage
- final application list row without rationale

Build behavior:

- `med-school-validate` exits nonzero on errors.
- Warnings still allow build.
- `med-school-build-all` should run validation/report as part of the build. If errors exist, fail before producing misleading final artifacts.

### 7. Workbook Tabs

Add these tabs to the workbook:

- `Applicant Profiles`
- `Admissions Stats`
- `Admissions Source Queue`
- `Partner Inputs`
- `Data Quality`

Keep existing tabs:

- `Instructions`
- `Project Subplans`
- `School Master`
- `User Preferences`
- `Scenario Weights`
- `Calculated Rankings`
- `Final Application List`
- `Sources`
- `Field Definitions`

### 8. Tests

Add `pytest` if not already present.

Add lightweight tests for:

- ranking generation runs
- workbook has required tabs
- validation catches duplicate `school_id`
- validation catches invalid score
- validation catches exclusion without reason

Command:

```bash
uv run pytest
```

## Do Not Do In Phase 1

- Do not scrape MCAT/GPA values.
- Do not infer admissions stats.
- Do not add real applicant/private data.
- Do not build complex school-page parsers.
- Do not make final rankings appear reliable.
- Do not remove existing workbook/CSV outputs from the build.
- Do not change the current project decision excluding Puerto Rico.

## Required Final Verification

Run:

```bash
uv run med-school-build-all
uv run pytest
```

Verify:

- workbook exists at `outputs/med_school_ranker.xlsx`
- upload bundle exists at `med-school-ranker-upload.zip`
- data quality report exists at `outputs/data_quality_report.csv`
- workbook contains all required tabs
- active school universe remains 233 rows
- Puerto Rico remains excluded from active outputs

## Definition of Done

Phase 1 is done when:

- all Phase 1 templates exist
- validation command exists and reports data quality
- build command runs validation, rankings, workbook, and upload bundle
- workbook includes the new input/report tabs
- tests pass
- no real private applicant data is committed
