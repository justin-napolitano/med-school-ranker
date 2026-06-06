# Medical School Ranker Seed

CSV and XLSX decision model for ranking U.S. MD and DO medical school options while keeping every inclusion, exclusion, weight, and source auditable.

## Planning Docs

Start here before expanding the seed data model:

- [Executive Plan](docs/EXEC_PLAN.md)
- [Plan Critical Review](docs/PLAN_CRITICAL_REVIEW.md)
- [Headless Worker Runbook](docs/HEADLESS_WORKER_RUNBOOK.md)
- [Headless Execution Plan: Phase 1](docs/HEADLESS_EXECUTION_PLAN.md)
- [Source Data Integration Executive Plan](docs/SOURCE_DATA_INTEGRATION_PLAN.md)
- [Headless Source Data Integration Plan: Phase 2A](docs/HEADLESS_SOURCE_DATA_INTEGRATION_PLAN.md)
- [Headless Scoring Execution Plan: Phase 2B](docs/HEADLESS_SCORING_EXECUTION_PLAN.md)
- [Static Review Site Executive Plan](docs/SITE_EXEC_PLAN.md)
- [Product Site Rebuild Executive Plan](docs/SITE_PRODUCT_REBUILD_EXEC_PLAN.md)
- [Headless Product Site Rebuild Execution Plan](docs/HEADLESS_PRODUCT_SITE_REBUILD_EXECUTION_PLAN.md)
- [Frontend Product Polish Executive Plan](docs/FRONTEND_PRODUCT_POLISH_EXEC_PLAN.md)
- [Headless Frontend Product Polish Plan](docs/HEADLESS_FRONTEND_PRODUCT_POLISH_PLAN.md)
- [Headless Site Execution Plan: Phase 1.5A](docs/HEADLESS_SITE_EXECUTION_PLAN.md)
- [Data Architecture](docs/plans/data_architecture.md)
- [School Universe](docs/plans/school_universe.md)
- [Applicant Profiles](docs/plans/applicant_profiles.md)
- [Admissions Stats](docs/plans/admissions_stats.md)
- [Cost and Debt](docs/plans/cost_and_debt.md)
- [Admissions Probability](docs/plans/admissions_probability.md)
- [Attendance Preference](docs/plans/attendance_preference.md)
- [Residency and Match](docs/plans/residency_and_match.md)
- [Hidden Curriculum](docs/plans/hidden_curriculum.md)
- [Scoring Engine](docs/plans/scoring_engine.md)
- [Workbook and Export](docs/plans/workbook_and_export.md)
- [Validation and QA](docs/plans/validation_and_qa.md)
- [Governance](docs/plans/governance.md)

Static site page/menu/table plans:

- [Navigation and Layout](docs/site/navigation_and_layout.md)
- [Dashboard Page](docs/site/dashboard_page.md)
- [Rankings Page](docs/site/rankings_page.md)
- [School Detail Page](docs/site/school_detail_page.md)
- [Partner Review Page](docs/site/partner_review_page.md)
- [Admissions Sources Page](docs/site/admissions_sources_page.md)
- [Data Quality Page](docs/site/data_quality_page.md)
- [Plans Page](docs/site/plans_page.md)
- [Tables and Filters](docs/site/tables_and_filters.md)
- [Build and Deploy](docs/site/build_and_deploy.md)

Product site rebuild plans:

- [Routes and Information Architecture](docs/site/product_rebuild/01_routes_and_information_architecture.md)
- [Rankings and List Builder](docs/site/product_rebuild/02_rankings_and_list_builder.md)
- [School Profiles](docs/site/product_rebuild/03_school_profiles.md)
- [Curated Lists and Scoring Lenses](docs/site/product_rebuild/04_curated_lists_and_scoring_lenses.md)
- [Admin Separation and Publish-Safe Mode](docs/site/product_rebuild/05_admin_publish_safe.md)
- [Visual Design and Reporting Quality](docs/site/product_rebuild/06_visual_reporting_quality.md)
- [Product Site Critical Review](docs/site/product_rebuild/CRITICAL_REVIEW.md)

Frontend product polish plans:

- [Visual System and Product Shell](docs/site/product_polish/01_visual_system_and_product_shell.md)
- [Intake and Rankings Polish](docs/site/product_polish/02_intake_and_rankings_polish.md)
- [School Cards and Score Cards](docs/site/product_polish/03_school_cards_and_score_cards.md)
- [Applications and Actions Polish](docs/site/product_polish/04_applications_and_actions_polish.md)
- [Mobile and Responsive Polish](docs/site/product_polish/05_mobile_and_responsive_polish.md)
- [QA and Publish-Safe Review](docs/site/product_polish/06_qa_and_publish_safe_review.md)
- [Product Polish Critical Review](docs/site/product_polish/CRITICAL_REVIEW.md)

## Files

- `outputs/med_school_ranker.xlsx`: upload this workbook to Google Sheets. It contains the tabs below.
- `outputs/site/index.html`: open this local static review site in a browser for dashboard, rankings, detail, source, quality, and plan review.
- `data/project_subplans.csv`: import as **Project Subplans**. Machine-readable index of the exec plan and subplans.
- `data/school_master.csv`: import as **School Master**. One row per LCME MD program and AOA/COCA DO school/site row.
- `data/applicant_profiles.csv`: import as **Applicant Profiles**. Public/template applicant profile fields only.
- `data/user_preferences.csv`: import as **User Preferences**. Controls Admissions Score, Attendance Score, and Overall School Value.
- `data/scenario_weights.csv`: import as **Scenario Weights**. Creates alternative rankings for prestige, lifestyle, finance, specialty optionality, and admissions realism.
- `data/normalized/admissions_stats.csv`: import as **Admissions Stats**. Blank/template stats layer for future source-verified GPA/MCAT values.
- `data/manual/admissions_source_queue.csv`: import as **Admissions Source Queue**. One row per school to track public admissions stats source review.
- `data/manual/source_match_overrides.csv`: import as **Source Match Overrides**. Manual reviewed source-to-school match decisions for ambiguous imports.
- `data/manual/partner_inputs.csv`: import as **Partner Inputs**. Simple partner-facing fit scores and notes.
- `outputs/calculated_rankings.csv`: import as **Calculated Rankings**. Regenerated by the script from the master sheet plus weights.
- `data/final_application_list.csv`: import as **Final Application List**. Generated from persisted visibility and dossier state once schools survive filtering.
- `outputs/data_quality_report.csv`: import as **Data Quality**. Validation warnings and errors from the latest build.
- `data/field_definitions.csv`: import as **Field Definitions**. Short explanations for the model fields.
- `data/sources.csv`: import as **Sources**. Source URLs and source dates used for the seed universe.
- `med-school-ranker-upload.zip`: archive containing the workbook, CSVs, static site, README, and project files.

## Upload

For the cleanest Google Sheets workflow, upload:

```text
outputs/med_school_ranker.xlsx
```

Google Sheets should preserve these worksheets:

- `Instructions`
- `Project Subplans`
- `School Master`
- `Applicant Profiles`
- `User Preferences`
- `Scenario Weights`
- `Admissions Stats`
- `Admissions Source Queue`
- `Source Match Overrides`
- `Partner Inputs`
- `Calculated Rankings`
- `Final Application List`
- `Data Quality`
- `Sources`
- `Field Definitions`

## Current Seed Universe

- 159 MD program rows from the LCME Accredited Programs directory, excluding Puerto Rico by current project decision.
- 74 DO school/site rows from the AOA Osteopathic Medical Schools directory.
- 233 total rows.

The DO side is deliberately campus/site-level where the official directory exposes separate locations. That makes the sheet larger than the rough "~200 schools" target, but it keeps location-sensitive decisions transparent. Use `parent_school_name`, `campus_name`, and `application_unit_assumption` to decide later whether to collapse or keep campuses separate.

## Scoring Structure

Keep these separate:

- **Admissions Score**: how likely the school is to convert for this applicant.
- **Attendance Score**: how much the applicant would want to attend if accepted.
- **Overall School Value**: weighted blend of admissions, attendance, and regret.

The starter weights are in `data/user_preferences.csv`. Adjust those weights directly, then rerun the script.

Important subjective fields are intentionally blank. Do not invent them. Fill them only after source review or personal evaluation.

## Suggested Workflow

1. Upload `outputs/med_school_ranker.xlsx` to Google Sheets for review and sharing.
2. Fill in applicant-specific scores in `School Master`, using 1-10 where score columns ask for a score.
3. Keep `manual_exclusion_flag` as `FALSE` until there is a real reason to cut a school.
4. When cutting a school, set `manual_exclusion_flag` to `TRUE` and fill `exclusion_reason`.
5. Export updated `School Master`, `User Preferences`, and `Scenario Weights` back to CSV before regenerating locally.
6. Run:

```bash
uv run med-school-build-all
```

7. Re-upload `outputs/med_school_ranker.xlsx` or re-import `outputs/calculated_rankings.csv` into the Calculated Rankings tab.

## Local Commands

From this folder:

```bash
uv run med-school-build-rankings
uv run med-school-build-workbook
uv run med-school-build-site
uv run med-school-build-site --site-mode publish_safe
uv run med-school-build-all
uv run med-school-build-final-list
uv run med-school-import-reviewer-state --visibility-export school_visibility_export.csv --dossier-export school_dossier_edits_export.csv
uv run med-school-validate
uv run pytest
```

Compatibility wrappers are also available:

```bash
uv run python scripts/build_rankings.py
uv run python scripts/build_workbook.py
uv run python scripts/build_site.py
uv run python scripts/build_all.py
```

## GitHub Pages

The public static site is deployed by `.github/workflows/deploy-pages.yml`.

The workflow rebuilds source-derived outputs, generates `outputs/site` with:

```bash
uv run med-school-build-site --site-mode publish_safe
```

Then it validates, runs tests, uploads `outputs/site`, and deploys to GitHub Pages. Pull requests run the same build/test path without deploying.

## Score Meanings

Use a consistent 1-10 interpretation:

- `1`: very poor fit or high concern.
- `5`: neutral or average.
- `10`: excellent fit or strong advantage.

For cost/debt fields, higher should always mean better for the applicant:

- `attendance_cost_score = 10`: very affordable.
- `debt_burden_score = 10`: low projected debt burden.

## Source Discipline

The seed verifies school identity, degree type, city/state, accreditation/source fields, and public school/site URLs where available. MCAT/GPA and cost fields are source-integrated where current public or third-party source tables provide them; some MCAT/GPA rows are explicitly marked as assumed matches pending better source review. The project still does not claim to have verified match, curriculum, culture, or other subjective data.

For every researched school, fill:

- `last_verified_date`
- the relevant source URL fields
- `data_confidence`
- short notes when the source is ambiguous

## Dynamic Tiers

The generated rankings classify schools from the entered 1-10 scores:

- `Dream`: Admissions Score below 3 and Attendance Score at least 8.
- `Reach`: Admissions Score below 5.
- `Target`: Admissions Score from 5 to below 7.
- `Likely`: Admissions Score 7 or higher.
- `Unscored`: missing admissions or attendance score.

These are not true acceptance probabilities. They are applicant-specific decision tiers based on your entered evidence.
