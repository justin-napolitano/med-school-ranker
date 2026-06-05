# Static Review Site Executive Plan

## Objective

Build a static, GitHub Pages-ready review website for fast browsing, filtering, and comparing medical schools from the same CSV source of truth that powers the workbook.

The site is for rapid review by the user. The workbook remains the partner-friendly collaborative input artifact.

## Current Decision

- Build a static generated site, not a full web app.
- Use repo CSVs as source data.
- Generate JSON and static assets into `outputs/site/`.
- Publishable via GitHub Pages.
- No backend, database, authentication, or server-side rendering in the first pass.
- No in-browser writes in the first pass.
- Editing still happens in CSV/XLSX; the site is read-only review.

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
    partner_inputs.json
    admissions_source_queue.json
    data_quality_report.json
    project_subplans.json
```

Primary command:

```bash
uv run med-school-build-site
```

Full build command should eventually include site generation:

```bash
uv run med-school-build-all
```

## Architecture

Use one of these conservative approaches:

1. Plain generated HTML/CSS/JS with embedded or adjacent JSON.
2. Small Vite app if the implementation benefits from component structure.

Default recommendation: plain static HTML/CSS/JS for Phase 1.5. The current needs are tables, filters, detail panes, and source links; a framework is not necessary yet.

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

## Navigation Model

Primary menu items:

- Dashboard
- Rankings
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
- First screen should be the review dashboard.
- Keep controls obvious and compact.
- Use tables for comparison and detail panels for per-school context.
- Surface data quality and missing data instead of hiding it.
- Keep subjective partner inputs visually separate from source-derived facts.

## Implementation Phases

### Phase 1.5A: Static Site Baseline

- Add `med-school-build-site` command.
- Generate JSON from CSVs.
- Generate `outputs/site/index.html`.
- Implement dashboard, rankings table, detail panel, data quality table, and source queue table.
- Add basic styling and client-side filtering.
- Add tests/smoke checks for required files and valid JSON.

### Phase 1.5B: Review Ergonomics

- Add saved filter presets through URL query params.
- Add comparison drawer for selected schools.
- Add better missing-data badges.
- Add source-link panels.

### Phase 1.5C: GitHub Pages Polish

- Add deployment instructions.
- Add optional GitHub Actions workflow.
- Add static asset cache-safe filenames if needed.

## Validation Rules

- Site build must fail if required CSV/JSON inputs are missing.
- Generated JSON must be parseable.
- `index.html` must reference existing asset/data files.
- School count in site JSON must match active `school_master.csv`.
- Puerto Rico remains excluded from active site data.
- No private `data/manual/private` files should be copied into `outputs/site`.

## Definition of Done

The static review site plan is ready for execution when:

- Each page/menu/table plan has objective, inputs, components, interactions, and done criteria.
- `data/project_subplans.csv` indexes the site plans.
- README points to the site plan.
- A future headless worker can implement Phase 1.5A without asking follow-up questions.
