# Medical School Ranker Executive Plan

## Objective

Build a transparent medical school decision-support system that starts from the full U.S. MD and DO school universe, enriches it with source-traceable data, separates objective facts from human judgments, and produces reviewable CSV and XLSX outputs for Google Sheets.

The system should help answer questions like:

- Which schools are realistic admissions targets for this applicant?
- Which schools would this applicant actually want to attend?
- Which schools survive under different scenarios such as prestige, lifestyle, finance, or specialty optionality?
- Why was a school included, excluded, ranked highly, or ranked poorly?

## Current Project Decisions

- School universe excludes Puerto Rico, Canada, Caribbean programs, and developing/candidate schools for now.
- The system must support multiple applicant profiles, each with its own stats, hard filters, soft preferences, and weights.
- Applicant-specific/private profile data stays local and out of git by default.
- Public source scraping is allowed only for public, non-login school pages and public reports when permitted; restricted sources use user-provided import files.
- The first decision target is narrowing the universe to approximately 25 applications.
- The model should recommend a balanced application basket across Dream, Reach, Target, and Likely tiers.
- Geography supports both hard filters and soft scores, including region, state/city, urban/rural/suburban setting, and demographic/community context.
- Urban environments are preferred by default.
- Cost and debt are low-weight factors unless manually changed for a profile.
- Specialty interest is emergency medicine for now, but specialty weighting stays low; MCAT/GPA fit is the first-order admissions screen.
- Hidden curriculum should be tracked and surfaced, but it should not heavily drive the default ranking algorithm.
- The primary collaboration output is a report/workbook for the user's partner, with easy spreadsheet inputs for normative rankings.

## Non-Goals

- Do not build a black-box ranking engine.
- Do not hide exclusions or manually remove schools without an explicit reason.
- Do not treat all GPA/MCAT, cost, match, or culture data as equally reliable.
- Do not scrape paid, login-gated, or restricted data sources unless rights and access are clear.
- Do not collapse MD programs, DO schools, branch campuses, and additional locations without documenting the application-unit assumption.
- Do not implement school-specific predictive admissions probability until the future-scope model plan and data readiness checklist are satisfied.

## Core Principles

- Every ranked number must trace to a source, formula, or explicit human judgment.
- School facts, admissions stats, costs, match outcomes, hidden curriculum, and personal-fit scores live in separate layers.
- The workbook is a review artifact; normalized CSVs and source snapshots are the project source of truth.
- Missing data stays missing. Unknown values should not silently become zero.
- Higher score values should consistently mean better fit or lower concern for the applicant.
- Source confidence and verification dates are first-class fields, not notes added later.

## Target Outputs

- Raw source snapshots where legally and practically appropriate.
- Normalized CSVs for each data domain.
- Generated `School Master` and `Calculated Rankings` outputs.
- Google Sheets-ready XLSX workbook.
- Upload bundle containing workbook, CSVs, docs, and project code.
- Data quality report listing missing fields, stale sources, duplicate school IDs, invalid scores, and ranking coverage concerns.

## Architecture

The project should evolve toward this structure:

```text
data/
  raw/
  normalized/
  manual/
    private/
  school_master.csv
  applicant_profiles.csv
  user_preferences.csv
  scenario_weights.csv
outputs/
  calculated_rankings.csv
  med_school_ranker.xlsx
  data_quality_report.csv
docs/
  EXEC_PLAN.md
  plans/
src/
  med_school_ranker/
```

Current seed files can remain where they are while the raw, normalized, and manual layers are introduced incrementally.

## Planning Areas

The project is divided into subplans:

- [Data Architecture](plans/data_architecture.md)
- [Source Data Integration](SOURCE_DATA_INTEGRATION_PLAN.md)
- [Plan Critical Review](PLAN_CRITICAL_REVIEW.md)
- [Headless Worker Runbook](HEADLESS_WORKER_RUNBOOK.md)
- [School Universe](plans/school_universe.md)
- [Applicant Profiles](plans/applicant_profiles.md)
- [Admissions Stats](plans/admissions_stats.md)
- [Cost and Debt](plans/cost_and_debt.md)
- [Admissions Probability](plans/admissions_probability.md)
- [Predictive Admissions Model Future Scope](PREDICTIVE_ADMISSIONS_MODEL_FUTURE_SCOPE.md)
- [Attendance Preference](plans/attendance_preference.md)
- [Residency and Match](plans/residency_and_match.md)
- [Hidden Curriculum](plans/hidden_curriculum.md)
- [Scoring Engine](plans/scoring_engine.md)
- [Headless Scoring Execution Plan](HEADLESS_SCORING_EXECUTION_PLAN.md)
- [Scoring Transparency and Rollup Executive Plan](SCORING_TRANSPARENCY_EXEC_PLAN.md)
- [Headless Scoring Transparency Execution Plan](HEADLESS_SCORING_TRANSPARENCY_EXECUTION_PLAN.md)
- [Workbook and Export](plans/workbook_and_export.md)
- [Validation and QA](plans/validation_and_qa.md)
- [Governance](plans/governance.md)
- [Product Site Rebuild Executive Plan](SITE_PRODUCT_REBUILD_EXEC_PLAN.md)
- [Headless Product Site Rebuild Execution Plan](HEADLESS_PRODUCT_SITE_REBUILD_EXECUTION_PLAN.md)
- [Site Profile Node UI Adoption Executive Plan](SITE_PROFILE_NODE_UI_ADOPTION_EXEC_PLAN.md)
- [Headless Site Profile Node UI Adoption Plan](HEADLESS_SITE_PROFILE_NODE_UI_ADOPTION_PLAN.md)
- [Site Visual Direction Plan](SITE_VISUAL_DIRECTION_PLAN.md)
- [Site Guided Applicant Intake Executive Plan](SITE_GUIDED_INTAKE_EXEC_PLAN.md)
- [Headless Guided Applicant Intake Plan](HEADLESS_SITE_GUIDED_INTAKE_PLAN.md)
- [Site UX Review and School Research Workflow Plan](SITE_UX_REVIEW_AND_RESEARCH_WORKFLOW_PLAN.md)
- [Headless Site UX Review Execution Plan](HEADLESS_SITE_UX_REVIEW_EXECUTION_PLAN.md)

## Milestones

### Milestone 1: Planning Baseline

- Create executive plan and seeded subplans.
- Document source policy and separation of data domains.
- Identify schemas needed before importing more data.

### Milestone 2: Project Hardening

- Add schema validation.
- Add tests for ranking generation and workbook generation.
- Add data quality report generation.
- Keep `uv run med-school-build-all` as the main build command.

### Milestone 3: School Universe Pipeline

- Convert current LCME and AOA/COCA school seeding into explicit source adapters.
- Store source metadata and source snapshots where appropriate.
- Validate counts and application-unit assumptions.

### Milestone 4: Admissions Stats Layer

- Add separate admissions stats schema.
- Integrate existing GPA/MCAT source tables as source-backed candidates, conflicts, and reviewed normalized rows.
- Add public school page/source adapter workflow for school-published admitted class profiles where permitted.
- Add manual import template for sources that are public but hard to parse consistently.
- Support user-provided MSAR/manual imports.
- Add source confidence and metric population fields for GPA/MCAT.
- Derive MCAT/GPA fit scores without mixing accepted, matriculated, mean, and median values.

### Milestone 5: Cost, Debt, and Application Logistics

- Add tuition, COA, expected scholarship, fee, and deposit data layers.
- Integrate safe AAMC tuition rows into normalized cost/debt data and queue ambiguous or missing rows for review.
- Add debt burden formulas and sensitivity assumptions.
- Track source dates and confidence.

### Milestone 6: Qualitative Research Workflow

- Add manual research templates for curriculum, culture, hidden curriculum, match outcomes, city fit, and personal notes.
- Keep judgment fields explicit and separate from source-derived facts.

### Milestone 7: Ranking and Scenario Explainability

- Add multi-profile ranking support.
- Improve scenario scoring.
- Add per-school explanation fields showing top positive and negative drivers.
- Add data completeness penalties and warnings.

Phase 2B execution details live in [Headless Scoring Execution Plan](HEADLESS_SCORING_EXECUTION_PLAN.md). This phase is deterministic scoring only. It does not include school-specific predictive admissions probability.

### Milestone 7.5: Scoring Transparency and Rollup

- Add long-form score contribution outputs.
- Add rank confidence, rank bands, and deterministic explanation fields.
- Add workbook/site audit views that answer "Why this rank?"
- Introduce a generated decision rollup table after explainability outputs are stable.
- Move toward normalized domain tables incrementally rather than expanding the master table indefinitely.

Execution details live in [Scoring Transparency and Rollup Executive Plan](SCORING_TRANSPARENCY_EXEC_PLAN.md) and [Headless Scoring Transparency Execution Plan](HEADLESS_SCORING_TRANSPARENCY_EXECUTION_PLAN.md).

### Milestone 7.75: Site Data Modeling and Card Contracts

- Define canonical domain tables separately from generated review outputs.
- Generate JSON read-model nodes for school facts, school cards, profile sections, ranking cards, compare cards, lists, methodology, and admin status.
- Keep the current static site and workbook backward compatible while introducing node contracts.
- Separate admin/local nodes from publish-safe product nodes at payload-generation time.
- Preserve a future Postgres/Vercel migration path without making JSON the source of truth.

Execution details live in [Site Data Modeling Executive Plan](SITE_DATA_MODELING_EXEC_PLAN.md) and [Headless Site Data Modeling Execution Plan](HEADLESS_SITE_DATA_MODELING_EXECUTION_PLAN.md).

### Milestone 7.8: Profile Node UI Adoption

- Make the existing static site consume generated profile/card nodes before visual redesign.
- Render school profile sections from `school_profile_nodes`.
- Add shared node-backed card/section helpers for later design work.
- Preserve current admin, shortlist, compare, visibility, dossier, and publish-safe workflows.
- Keep the site backward compatible while proving the node read model.

Execution details live in [Site Profile Node UI Adoption Executive Plan](SITE_PROFILE_NODE_UI_ADOPTION_EXEC_PLAN.md) and [Headless Site Profile Node UI Adoption Plan](HEADLESS_SITE_PROFILE_NODE_UI_ADOPTION_PLAN.md).

### Milestone 7.85: Visual Direction

- Define a serious, modern, digitally native visual language for current and future applicants.
- Target Gen Z and early Gen Alpha expectations without forced slang, novelty, or fake youth branding.
- Make transparency, source confidence, missing data, and "why this rank" visible parts of the interface.
- Keep style implementation downstream of profile-node/card UI adoption.

Execution details live in [Site Visual Direction Plan](SITE_VISUAL_DIRECTION_PLAN.md).

### Milestone 7.9: Guided Applicant Intake

- Add a normal-language intake flow so users do not need to understand weights, CSVs, or raw tables first.
- Translate answers into deterministic ranking context, filters, result groups, explanation chips, and list targets.
- Keep personal answers browser-local and explicitly exportable.
- Show grouped school cards as the post-intake review surface while keeping advanced tables and methodology available.
- Preserve reversible hide/restore, shortlist, compare, application-list, dossier, research, admin, and publish-safe workflows.

Execution details live in [Site Guided Applicant Intake Executive Plan](SITE_GUIDED_INTAKE_EXEC_PLAN.md) and [Headless Guided Applicant Intake Plan](HEADLESS_SITE_GUIDED_INTAKE_PLAN.md).

### Milestone 8: Review-Ready Workbook

- Add partner-facing input tabs for applicant profile, weights, hard filters, and manual scores.
- Add data quality, assumptions, changelog, and source summary tabs.
- Improve formatting and filters.
- Make the workbook useful for collaboration without hiding the underlying data model.

### Milestone 9: Product-Grade Review Site

- Rebuild the static site around applicant-facing rankings, curated lists, school profiles, scoring lenses, and publish-safe mode.
- Keep this downstream of Phase 2B scoring and the site data-modeling/card-contract work so the site is not polished around placeholder or admin-shaped payloads.

### Milestone 10: Site UX Review and School Research Workflow

- Run screenshot-based desktop/mobile visual QA.
- Improve obvious layout and clarity issues based on screenshots.
- Add reversible hide/restore controls for schools in the working view.
- Add school dossier/profile pages for every school.
- Add structured local research fields, missing-information prompts, and CSV exports.
- Keep source-backed facts, generated scores, and user-entered research clearly separated.

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Mixing accepted vs matriculated GPA/MCAT | Misleading admissions fit | Store metric population and metric type explicitly. |
| Restricted source misuse | Legal or ethical issue | Use manual import templates for restricted data. |
| False precision in subjective fields | Overconfident rankings | Keep judgment scores separate and label them clearly. |
| Stale data | Bad application decisions | Require source date and last checked date. |
| Campus/application-unit confusion | Incorrect school list | Track parent school, campus, and application-unit assumptions. |
| Missing data treated as zero | Ranking distortion | Keep missing values blank and report coverage. |
| Overweighting prestige | Optimizes for wrong outcome | Maintain separate Admissions and Attendance scores plus scenarios. |

## Operating Model

Each major change should follow this path:

1. Update or create the relevant subplan.
2. Define schema changes before writing import code.
3. Add source policy and validation rules.
4. Implement import or scoring logic.
5. Regenerate CSV/XLSX outputs.
6. Review data quality report.
7. Commit code, data schema, and regenerated outputs together when appropriate.

## Definition of Done

The project is first-class when:

- The school universe is reproducible from documented source adapters.
- GPA/MCAT, cost, match, curriculum, and subjective-fit data are separate, auditable layers.
- The workbook can be regenerated from source files with one command.
- Data quality checks fail loudly for invalid or ambiguous data.
- A reviewer can inspect why any school appears, disappears, ranks highly, or ranks poorly.
