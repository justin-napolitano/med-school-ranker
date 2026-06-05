# Product Site Rebuild Executive Plan

## Objective

Rebuild the static review site into a product-grade medical school ranking and reporting experience that is useful to applicants, not just project administrators.

The primary user value should be:

- browse and filter the school universe quickly;
- understand why a school ranks well or poorly;
- open a polished school profile with source-backed facts;
- use curated lists such as best cities, best public schools, best private schools, best culture fit, low-cost options, and admissions realism;
- apply a curated list as a scoring lens, not merely a saved filter;
- keep admin/build/source-health workflows available but separated from the public product routes.

The target quality bar is "USNews-worthy or better" in usefulness: strong tables, polished school profiles, transparent methodology, evidence-backed facts, and applicant-specific fit controls.

## Current State

- `outputs/site/index.html` is generated as a static local site with embedded JSON.
- The current payload includes school master rows, rankings, admissions stats, AAMC MCAT/GPA grid context, cost/debt, policies, LOR rows, source-review queues, and quality reports.
- The current UI is useful but admin-heavy. Dashboard and status views are prominent, while applicant-facing ranking/list/profile workflows need to become the first-class experience.
- Another worker may continue stabilizing the payload contract and splitting the current monolithic site generator. This plan should not block on that work.

## Product Decisions

- The default product route should be rankings, not the admin dashboard.
- Admin/source/build-health pages should live under a separate admin route family.
- School profiles should be first-class routes.
- Curated lists should be first-class routes and data objects.
- Curated lists should be applicable to scoring as lenses.
- Publish-safe mode must remove admin/private payloads rather than only hiding admin navigation.
- The static site approach remains acceptable while product UX is built out.
- Editing can remain in CSV/XLSX for now; in-browser writes are not required for this phase.

## Critical Review Fixes In Scope

The critical review findings are required work in this execution plan, not separate commentary:

- Add a Phase 0 guardrail slice before product feature work.
- Scaffold `local_full` and `publish_safe` payload separation before admin data is moved around.
- Treat publish-safe data removal as a payload-generation requirement, not CSS/nav hiding.
- Add curated-list field-readiness metadata so lists that need immature fields are labeled provisional until those fields are source-backed or manually reviewed.
- Require AAMC MCAT/GPA grid caveats wherever national grid context is displayed.
- Require screenshot/browser smoke checks for the visual-quality phase when tooling is available.
- Keep route-shell/admin separation runnable even if deterministic scoring work is still in progress.

## Route Model

Public/product routes:

```text
/
/rankings
/lists
/lists/:list_slug
/compare
/schools/:school_slug
/methodology
/sources
```

Admin routes:

```text
/admin
/admin/sources
/admin/data-quality
/admin/build
```

For the current static build, implement these as hash routes:

```text
#/rankings
#/lists/best-cities
#/schools/yale-school-of-medicine
#/admin
```

Future hosted builds can convert this to path routing if a router/build system is introduced.

## Non-Goals

- Do not build a backend.
- Do not add login/authentication.
- Do not treat a hidden admin route as data security.
- Do not publish local applicant or partner data.
- Do not invent culture, ownership, city, or prestige facts when source fields are missing.
- Do not add school-specific predictive admissions probability. The AAMC grid is national aggregate context only.
- Do not block this phase on a frontend framework migration.

## Data Requirements

Current usable fields:

- school identity, degree, location, and source URL;
- calculated rankings and score columns;
- normalized GPA/MCAT source averages, bands, spreads, source count, quality band, and AAMC national acceptance-rate band;
- AAMC tuition/COA rows for matched MD schools;
- LOR and admissions policy source rows;
- source-review and data-quality outputs.

Near-term required fields:

- `ownership_type`: public, private, public-private partnership, unknown;
- `region`;
- `city_fit_score` and/or normalized city facts;
- `culture_fit_score` and evidence status;
- `profile_slug` or generated school slug;
- curated-list definitions and scoring profiles.

Missing facts should remain missing. Curated list eligibility should degrade gracefully when a required field is absent.

## Child Plans

- [Headless Product Site Rebuild Execution Plan](HEADLESS_PRODUCT_SITE_REBUILD_EXECUTION_PLAN.md)
- [Routes and Information Architecture](site/product_rebuild/01_routes_and_information_architecture.md)
- [Rankings and List Builder](site/product_rebuild/02_rankings_and_list_builder.md)
- [School Profiles](site/product_rebuild/03_school_profiles.md)
- [Curated Lists and Scoring Lenses](site/product_rebuild/04_curated_lists_and_scoring_lenses.md)
- [Admin Separation and Publish-Safe Mode](site/product_rebuild/05_admin_publish_safe.md)
- [Visual Design and Reporting Quality](site/product_rebuild/06_visual_reporting_quality.md)
- [Critical Review](site/product_rebuild/CRITICAL_REVIEW.md)
- [Site UX Review and School Research Workflow Plan](SITE_UX_REVIEW_AND_RESEARCH_WORKFLOW_PLAN.md)
- [Headless Site UX Review Execution Plan](HEADLESS_SITE_UX_REVIEW_EXECUTION_PLAN.md)

## Implementation Sequence

### Phase 0: Guardrails and Readiness

- Add explicit site mode scaffolding for `local_full` and `publish_safe`.
- Define product-safe payload sections separately from admin-local payload sections.
- Add tests that publish-safe payloads do not contain admin/source-review/private data, even before publish-safe routes are polished.
- Add generated school slugs and list slugs to the payload contract.
- Add curated-list field-readiness metadata covering `ownership_type`, `region`, city facts, culture fields, scoring fields, cost fields, and source-confidence fields.
- Add AAMC grid caveat text as reusable display copy.
- Add tests that missing curated-list fields produce provisional or low-confidence status rather than false claims.

### Phase A: Product Route Shell

- Make `#/rankings` the default route.
- Move admin/status/dashboard surfaces under `#/admin`.
- Add route-aware navigation with public tabs and a separate admin entry.
- Add school slug generation and route opening from tables.

### Phase B: Rankings Value Surface

- Rebuild rankings into the core working page.
- Add applicant-useful filters: degree, state, region, ownership, MCAT band, GPA band, AAMC rate band, tuition/COA, data quality, LOR burden, hard-no state, and partner status.
- Add scoring lens selector.
- Add visible reason chips and source-confidence badges.
- Add shortlist/list-builder controls.

### Phase C: School Profiles

- Add `#/schools/:slug` profile pages.
- Profile sections: overview, applicant fit, admissions facts, cost, requirements, policies, source confidence, risk flags, and related curated lists.
- Make every major fact traceable to source name, URL, and confidence where available.

### Phase D: Curated Lists

- Add `data/curated_lists.csv` and `data/scoring_profiles.csv`.
- Generate list pages from definitions.
- Add "Apply this lens" controls to rankings.
- Support curated routes for best cities, best culture fit, best public, best private, low cost, and admissions realism.
- Use field readiness to mark list confidence and missing-data behavior.
- Do not label a curated list as high confidence unless its required fields are available and reviewed.

### Phase E: Publish-Safe Product Build

- Complete the `local_full` and `publish_safe` mode implementation started in Phase 0.
- In publish-safe mode, omit admin routes and private/local payloads from generated JSON and embedded HTML.
- Add tests that private fields and admin data are absent from publish-safe output.
- Add a build/report line showing which site mode was generated.

### Phase F: Polish and QA

- Upgrade visual hierarchy, typography, cards, tables, profile layout, badges, and empty states.
- Add screenshot/smoke QA for desktop and mobile.
- Keep the site scannable and data-dense rather than marketing-like.

### Phase G: Applicant Research Workflow

- Add reversible school visibility controls so schools can be hidden from the working view without deleting them.
- Add hidden-school review and CSV export.
- Add school dossier/profile index for every school.
- Add dossier pages/panels with precomputed values, source-backed facts, missing research prompts, and local editable research fields.
- Add browser-local CSV exports for dossier edits and visibility decisions.

## Verification

Required commands:

```bash
uv run med-school-build-all
uv run pytest
```

Additional site checks:

- `outputs/site/index.html` contains embedded local payload.
- Public routes render from hash routing.
- `#/rankings` is the default user-facing route.
- `#/admin` is separated from public navigation.
- `#/schools/:slug` opens from ranking rows and curated lists.
- `#/lists/:slug` pages render from data definitions.
- A curated list can be applied as a scoring lens to rankings.
- Publish-safe mode excludes private/admin payloads.
- Field-readiness metadata is present for curated lists and missing fields are not overclaimed.
- AAMC grid is labeled as national aggregate MD data, not school-specific probability.
- Screenshot QA artifacts exist for desktop and mobile views when visual QA is run.
- Schools can be hidden, restored, reviewed, and exported without deleting source rows.
- School dossiers distinguish precomputed source-backed facts from user-entered research.

## Definition of Done

The product-site rebuild is done when:

- applicants can get real value from rankings, curated lists, and school profiles without opening admin pages;
- admin/source/build-health workflows are still available locally under admin routes;
- curated lists can filter or re-score the school universe;
- school profiles are polished, source-backed, and decision-useful;
- the site passes build/test verification;
- publish-safe mode can be generated without leaking local/private/admin data.
- applicants can use the site as a research workflow, not only as a ranking table.
