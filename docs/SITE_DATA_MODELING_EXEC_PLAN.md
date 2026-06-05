# Site Data Modeling Executive Plan

## Objective

Define the data model that lets the current review site evolve into two clean surfaces:

- an admin/review panel for source quality, plans, queues, generated outputs, and browser-local reviewer state;
- a product-style applicant review site with card-based school summaries, profile pages, ranked lists, comparison views, and transparent methodology.

The core decision is:

```text
CSV/source tables remain canonical for now.
Generated JSON nodes become the site read model.
Cards consume generated nodes, not raw CSV-shaped rows.
Postgres can later replace the CSV/source layer without changing the card contracts.
```

This keeps the project moving locally while creating a clean path to Vercel and a future Postgres backend.

## Current State

The repo already has:

- normalized/source CSVs for school identity, admissions stats, cost/debt, policies, letters, reviewer state, rankings, methodology, and score contributions;
- generated workbook, static site, JSON files, and upload bundle;
- `local_full` and `publish_safe` site modes;
- product/admin route separation in the static site;
- school profile routes and generated `school_profiles.json`;
- browser-local visibility, dossier, application-list, and compare workflows;
- deterministic profile-aware scoring and AAMC caveats.

The remaining problem is shape:

- the frontend still reads a large route payload that resembles implementation joins;
- card/profile surfaces do not yet have a stable schema;
- admin/source/review data and product-facing card data need a clearer contract;
- future Postgres/Vercel work needs a migration path that does not rewrite the UI.

## Design Principles

- Treat generated JSON as a read model, not the source of truth.
- Keep canonical tables narrow, domain-specific, and source-traceable.
- Keep card nodes stable and presentation-oriented.
- Keep admin nodes separate from product/public nodes.
- Do not make missing data look complete.
- Do not publish private applicant values or private-derived ranking outputs.
- Keep `outputs/site/data/site_payload.json` working while adding better node files incrementally.
- Make future Postgres tables match canonical domain concepts, not current wide output files.

## External References

These references support the direction but do not override repo-specific decisions:

- [Martin Fowler on CQRS](https://martinfowler.com/bliki/CQRS.html): useful as the architectural pattern behind separate write/source models and read/display models.
- [PostgreSQL JSON Types](https://www.postgresql.org/docs/current/datatype-json.html): useful for later deciding when relational tables should expose JSONB read-model snapshots or card payload caches.
- [Vercel deployment methods](https://vercel.com/docs/deployments/deployment-methods) and [vercel.json configuration](https://vercel.com/docs/project-configuration/vercel-json): useful for future static or hybrid hosting constraints.

## Target Data Layers

```text
data/
  raw/                    # external/source captures, ignored when private or licensed
  normalized/             # source-backed canonical domain rows
  manual/                 # reviewed public/manual inputs
  manual/private/         # local-only applicant data

outputs/
  calculated_rankings.csv
  score_contributions.csv
  scoring_methodology.csv
  school_decision_rollup.csv
  site/
    data/
      site_payload.json              # backward-compatible aggregate payload
      nodes/
        school_nodes.json
        school_card_nodes.json
        school_profile_nodes.json
        ranking_card_nodes.json
        compare_card_nodes.json
        list_nodes.json
        methodology_nodes.json
        admin_status_nodes.json
```

The `nodes/` directory is the new generated read-model layer. It may be embedded in `index.html` for local static review, written as adjacent JSON for hosted review, or later served from Postgres/API routes.

## Target Node Families

### School Fact Nodes

Stable identity and source-backed facts:

- `school_id`
- `school_slug`
- `display_name`
- `degree_type`
- `campus_name`
- `city`
- `state`
- `region`
- `ownership_type`
- `official_url`
- `source_confidence`
- `last_verified`

### Ranking and Fit Nodes

Generated scoring facts:

- `decision_rank`
- `rank_band`
- `rank_confidence`
- `overall_school_value`
- `admissions_score`
- `attendance_score`
- `admissions_fit_tier`
- `application_bucket`
- `top_positive_contributors`
- `top_negative_contributors`
- `missing_or_low_confidence_drivers`
- `aamc_context`

### Card Nodes

Presentation-ready summaries for list/grid surfaces:

- `school_card`
- `ranking_card`
- `comparison_card`
- `profile_snapshot_cards`
- `source_confidence_card`
- `methodology_card`
- `admin_status_card`

Cards should use typed fields and arrays, not generated prose blobs. The UI can render the same cards as compact table rows, grid cards, compare panels, or profile sections.

### Profile Section Nodes

Profile pages should be assembled from section nodes:

- `overview`
- `applicant_fit`
- `admissions_stats`
- `cost_and_debt`
- `requirements`
- `curriculum`
- `match_outcomes`
- `location_context`
- `student_life`
- `source_confidence`
- `reviewer_notes`
- `methodology`

Sections can be `ready`, `partial`, `provisional`, or `missing`. Missing sections must render honestly.

### Admin Nodes

Admin-only nodes include:

- source integration status;
- data quality warnings/errors;
- source review queues;
- conflict/review queues;
- plan status;
- build metadata;
- local reviewer state.

Admin nodes are allowed in `local_full`; they are not allowed in `publish_safe`.

## Product Surfaces Enabled

The card model should support:

- ranked school cards;
- school profile pages similar in density to US News-style fact reports;
- shortlist/application cards;
- comparison cards;
- curated list cards;
- methodology cards;
- source confidence cards;
- admin health cards.

The current generated site can remain the admin panel while the future product routes consume the new nodes.

## Migration Strategy

### Phase 0: Contract Only

- Add docs and project-plan rows.
- Define node schemas in markdown.
- Do not change runtime payload generation yet.

### Phase 1: Generate Node Files

- Add `outputs/site/data/nodes/*.json`.
- Build nodes from existing CSVs and current joined payload.
- Keep `site_payload.json` backward compatible.
- Add tests for shape, counts, IDs, slugs, and publish-safe exclusion.

### Phase 2: Use Nodes in Existing Site

- Start by rendering one surface from nodes, likely school cards or profile snapshot cards.
- Keep admin tables on existing payload until product nodes are stable.
- Verify that node rendering does not reimplement joins in JavaScript.

### Phase 3: Product Card Routes

- Make applicant-facing routes consume card/profile/list nodes.
- Keep admin routes as the current review panel.
- Use the same nodes for table rows and card layouts.

### Phase 4: Persistence and Import

- Add import/merge path for browser-exported reviewer CSVs.
- Keep canonical state in CSV/manual files until Postgres is selected.
- Add deterministic merge reports before writing source files.

### Phase 5: Postgres/Vercel Migration

- Map canonical CSV tables to relational Postgres tables.
- Treat generated node JSON as either build artifacts, API responses, or JSONB cache rows.
- Keep card contracts stable so the frontend does not care whether source data came from CSV or Postgres.

## Non-Goals

- Do not migrate the whole project to Postgres in this phase.
- Do not replace the workbook.
- Do not remove existing CSV outputs.
- Do not change scoring formulas.
- Do not implement predictive admissions probability.
- Do not build auth/login.
- Do not publish private or private-derived payloads.
- Do not scrape new school data.

## Child Plans

- [Headless Site Data Modeling Execution Plan](HEADLESS_SITE_DATA_MODELING_EXECUTION_PLAN.md)
- [Canonical Domain Tables](site/data_modeling/01_canonical_domain_tables.md)
- [JSON Node Contracts](site/data_modeling/02_json_node_contracts.md)
- [Card Surfaces and Profile Sections](site/data_modeling/03_card_surfaces_and_profile_sections.md)
- [Admin/Public Payload Separation](site/data_modeling/04_admin_public_payload_separation.md)
- [Postgres and Vercel Migration Path](site/data_modeling/05_postgres_vercel_migration_path.md)
- [Validation, Privacy, and QA](site/data_modeling/06_validation_privacy_and_qa.md)

## Acceptance Criteria

- The repo has a clear documented distinction between canonical data, generated rollups, generated JSON nodes, admin nodes, and product card nodes.
- Product rebuild plans are gated by this model instead of vague "after scoring" language.
- A headless worker can implement the first node-generation slice without conversational context.
- Publish-safe restrictions are explicit at the node family level.
- Future Postgres migration can preserve the same frontend node/card contracts.
