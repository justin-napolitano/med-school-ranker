# Static Review Site Executive Plan

Note: this plan documents the Phase 1.5 static-site baseline. The current product UX rebuild decisions live in [Product Site Rebuild Executive Plan](SITE_PRODUCT_REBUILD_EXEC_PLAN.md), which shifts the default experience from Dashboard to Rankings and moves admin/source/build-health workflows under admin routes.

## Objective

Build a static, GitHub Pages-ready review website for fast browsing, filtering, and comparing medical schools from the same CSV source of truth that powers the workbook.

The site is for rapid review by the user. The workbook remains the partner-friendly collaborative input artifact.

## Current Decision

- Build a static generated site, not a full web app.
- Use repo CSVs as source data.
- Generate JSON and static assets into `outputs/site/`.
- Generate `outputs/site/index.html` as a self-contained local review file with embedded data for Phase 1.5A.
- Publishable via GitHub Pages.
- No backend, database, authentication, or server-side rendering in the first pass.
- No in-browser writes in the first pass.
- Editing still happens in CSV/XLSX; the site is read-only review.
- Homepage opens to Dashboard.
- Rankings is the highest-priority review table for Phase 1.5A usability.
- School comparison is deferred to Phase 1.5B.
- Local review uses `site_privacy_mode=local_full`.
- GitHub Pages deployment is wired through `.github/workflows/deploy-pages.yml`.
- Public publishing must use `site_privacy_mode=publish_safe`.

## Non-Goals

- Do not replace the workbook.
- Do not add account/login flows.
- Do not store private applicant data in the generated site unless explicitly allowed later.
- Do not fetch live external data from the browser.
- Do not scrape GPA/MCAT data as part of the site build.
- Do not make the site dependent on a local dev server for basic review.

## Target Output

```text
outputs/site/
  index.html
  assets/
  data/
    school_master.json
    calculated_rankings.json
    applicant_profiles.json
    admissions_stats.json
    partner_inputs.json
    admissions_source_queue.json
    data_quality_report.json
    project_subplans.json
```

Phase 1.5A must embed the same JSON payload into `index.html` so the site works from `file://` without browser `fetch()` restrictions. Adjacent JSON files are still generated for inspection and future hosting.

Primary command:

```bash
uv run med-school-build-site
```

Full build command should eventually include site generation:

```bash
uv run med-school-build-all
```

Phase 1.5A decision: once `med-school-build-site` exists and tests pass, `uv run med-school-build-all` must run validation, rankings, workbook, site generation, and upload bundle.

## Architecture

Use one of these conservative approaches:

1. Plain generated HTML/CSS/JS with embedded or adjacent JSON.
2. Small Vite app if the implementation benefits from component structure.

Default recommendation: plain static HTML/CSS/JS for Phase 1.5. The current needs are tables, filters, detail panes, and source links; a framework is not necessary yet.

Phase 1.5A implementation rule: do not rely on client-side `fetch()` for required data when opened locally. Generate embedded JSON in `index.html` and optionally write adjacent JSON files for debugging and later GitHub Pages use.

## Data Contract

The site should read generated JSON derived from:

- `data/school_master.csv`
- `outputs/calculated_rankings.csv`
- `data/manual/partner_inputs.csv`
- `data/manual/admissions_source_queue.csv`
- `outputs/data_quality_report.csv`
- `data/project_subplans.csv`
- `data/applicant_profiles.csv`
- `data/normalized/admissions_stats.csv`

The site build should not mutate source CSVs.

## Derived Field Rules

The site builder should create a normalized client payload with derived fields so the frontend does not need to reimplement joins repeatedly.

Join key:

- Use `school_id` for all school-level joins.

Per-school derived fields:

- `warning_count`: count of `data_quality_report` rows where `severity=warning` and `row_id` equals `school_id`.
- `error_count`: count of `data_quality_report` rows where `severity=error` and `row_id` equals `school_id`.
- `partner_input_status`: `present` when any partner score, hard-no flag, hard-no reason, or partner notes exist; otherwise `missing`.
- `partner_notes_indicator`: `yes` when `partner_notes` is nonblank; otherwise `no`.
- `hard_no_flag`: truthy when partner input `hard_no_flag` is truthy.
- `admissions_stats_present`: `yes` when any MCAT/GPA metric field is populated for the school; otherwise `no`.
- `source_queue_status`: from `admissions_source_queue.source_status`, defaulting to `not_started` when blank.
- `suggested_next_action`: `review partner input` if partner input is missing; else `find admissions source` if candidate source URL is blank; else `review data quality` if warnings/errors exist; else `review ranking`.

Truthiness:

- Treat `TRUE`, `true`, `1`, `yes`, and `y` as true.

Missing values:

- Preserve missing source values as empty strings in raw JSON.
- Display missing score/source fields as `Missing` in the UI, not zero.

## Privacy Modes

Local review mode:

- `local_full`: include applicant profile template, partner inputs, source queue, validation report, and rankings. This mode is for local machine review.

Public publish mode:

- `publish_safe`: exclude private/local applicant data, admin routes, reviewer state, and local-only review queues before GitHub Pages publishing.

Private files:

- Never include anything from `data/manual/private` or `data/private` in any site output.

## Navigation Model

Primary menu items:

- Dashboard
- Rankings, highest-priority table view
- School Detail
- Partner Review
- Admissions Sources
- Data Quality
- Plans

Secondary controls:

- Global search
- Degree filter
- State/region filter
- Geography/setting filter
- Data quality filter
- Application bucket filter
- Hard-no filter

## Page Plans

Detailed page plans live in:

- [Navigation and Layout](site/navigation_and_layout.md)
- [Dashboard Page](site/dashboard_page.md)
- [Rankings Page](site/rankings_page.md)
- [School Detail Page](site/school_detail_page.md)
- [Partner Review Page](site/partner_review_page.md)
- [Admissions Sources Page](site/admissions_sources_page.md)
- [Data Quality Page](site/data_quality_page.md)
- [Plans Page](site/plans_page.md)
- [Tables and Filters](site/tables_and_filters.md)
- [Build and Deploy](site/build_and_deploy.md)

## UX Principles

- Dense, scannable, operational UI.
- No landing page or marketing-style hero.
- First screen is the review dashboard.
- Keep controls obvious and compact.
- Use tables for comparison and detail panels for per-school context.
- Surface data quality and missing data instead of hiding it.
- Keep subjective partner inputs visually separate from source-derived facts.

## Implementation Phases

### Phase 1.5A: Static Site Baseline

- Add `med-school-build-site` command.
- Generate JSON from CSVs.
- Generate `outputs/site/index.html`.
- Embed generated JSON in `index.html` for local file opening.
- Implement dashboard, rankings table, detail panel, data quality table, and source queue table, with Rankings receiving the most polish in the first pass.
- Add basic styling and client-side filtering.
- Add tests/smoke checks for required files and valid JSON.

### Phase 1.5B: Review Ergonomics

- Add saved filter presets through URL query params.
- Add comparison drawer for selected schools.
- Add better missing-data badges.
- Add source-link panels.

### Phase 1.5C: GitHub Pages Polish

- Maintain deployment instructions.
- Maintain GitHub Actions workflow.
- Add static asset cache-safe filenames if needed.
- Keep deployment pointed at `outputs/site` generated with `--site-mode publish_safe`.

## Validation Rules

- Site build must fail if required CSV/JSON inputs are missing.
- Generated JSON must be parseable.
- `index.html` must reference existing asset/data files.
- `index.html` must contain an embedded data payload sufficient to run without `fetch()`.
- School count in site JSON must match active `school_master.csv`.
- Puerto Rico remains excluded from active site data.
- No private `data/manual/private` files should be copied into `outputs/site`.

## Definition of Done

The static review site plan is ready for execution when:

- Each page/menu/table plan has objective, inputs, components, interactions, and done criteria.
- `data/project_subplans.csv` indexes the site plans.
- README points to the site plan.
- A future headless worker can implement Phase 1.5A without asking follow-up questions.
