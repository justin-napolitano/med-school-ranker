# Frontend Product Refresh Executive Plan

## Objective

Move the public site from an admin-heavy spreadsheet surface to an applicant-facing decision product.

The next frontend work should make the site usable without understanding CSVs, weights, score columns, or source integration internals. The product should still be deterministic, transparent, source-aware, and public-safe.

## Current Baseline

The project already has:

- deterministic scoring and rank explanations;
- guided intake with local answer state;
- public-safe GitHub Pages deployment;
- generated JSON nodes for school cards, ranking cards, profile sections, compare cards, methodology, and list surfaces;
- local Interested/Applying status controls;
- school score-card/profile routes;
- advanced rankings tables and admin/source data views.

The main problem is now presentation and workflow clarity:

- too many pages still read like generated tables;
- school review is not card-first;
- the intake and rankings workflows are not yet a single simple path from answers to school decisions;
- school profiles still contain too much admin/raw detail too early;
- the visual system is not yet coherent enough for a public product.

## Product Direction

Primary public route:

```text
Start with guided intake -> review school cards -> mark Interested/Applying -> open score card when needed -> export/share public-safe output.
```

Advanced tables remain available, but they should no longer be the default mental model.

Public routes should converge toward:

- `#/intake`: guided setup and answer summary;
- `#/rankings`: card-first ranked results with an advanced table mode;
- `#/schools`: searchable school card browser;
- `#/schools/:slug`: applicant-facing school score card;
- `#/applications`: Interested/Applying list builder;
- `#/methodology`: plain-language scoring/source methodology;
- `#/admin/*`: local/admin-only build, source, and data-quality views.

## Design Direction

The product should feel serious and current for Gen Z and early Gen Alpha applicants:

- modern, direct, and mobile-aware;
- not admissions-office formal;
- not slangy, gimmicky, or motivational;
- visually polished without decorative gradients, blobs, or one-hue theming;
- dense enough for repeated research;
- card-first for review, table-capable for power users.

## Branch Strategy

Every implementation slice must run on a clean branch from `main`.

| Slice | Branch | Purpose |
| --- | --- | --- |
| 0 | `impl-frontend-route-shell` | Product/admin route cleanup and navigation framing. |
| 1 | `impl-frontend-school-cards` | Shared applicant-facing school card system and school browser. |
| 2 | `impl-frontend-intake-results` | Guided intake results as card groups rather than table-first output. |
| 3 | `impl-frontend-list-builder` | Rankings/Application List action flow with Interested/Applying limits. |
| 4 | `impl-frontend-score-card-profile` | Simplified per-school score-card profile layout. |
| 5 | `impl-frontend-visual-polish` | Visual system, responsive QA, copy cleanup, and publish-safe smoke tests. |

Do not mix slices unless the headless worker proves the changes are small, tested, and still reviewable in one PR.

## Required Guardrails

- Do not change scoring formulas unless a later scoring plan explicitly requests it.
- Do not scrape or download new source data.
- Do not implement predictive admissions probability.
- Do not commit real private applicant answers.
- Do not remove advanced/admin views; move or de-emphasize them.
- Do not hide missing data or confidence labels.
- Do not make a backend/framework migration in this phase.
- Keep `publish_safe` deploy behavior working after every slice.

## Execution Order

### Slice 0: Product Route Shell

Goal: make the route structure and navigation match the product model before visual or card work expands.

Use:

- [Product Navigation And State](site/frontend_refresh/01_product_navigation_and_state.md)
- [Frontend Refresh QA And Branching](site/frontend_refresh/06_visual_qa_and_branching.md)

### Slice 1: School Card System

Goal: create one reusable school-card renderer that can power rankings, school browser, intake results, and application list previews.

Use:

- [School Card System](site/frontend_refresh/02_school_card_system.md)
- existing node contracts under `docs/site/data_modeling/`
- existing score-card simplification plans.

### Slice 2: Guided Intake Results

Goal: make intake output feel like a guided review product, not a rerendered table.

Use:

- [Guided Intake Results](site/frontend_refresh/03_guided_intake_results.md)
- existing guided-intake plans as compatibility contracts.

### Slice 3: Rankings And List Builder

Goal: make the rankings route a decision queue with clear Interested/Applying actions and hard list limits.

Use:

- [Rankings And List Builder](site/frontend_refresh/04_rankings_and_list_builder.md)

### Slice 4: School Score Card Profile

Goal: simplify each school profile into applicant-readable sections with raw details collapsed.

Use:

- [School Score Card Profile](site/frontend_refresh/05_school_score_card_profile.md)

### Slice 5: Visual Polish And QA

Goal: apply the visual direction after the core workflow is card-first and stable.

Use:

- [Frontend Refresh QA And Branching](site/frontend_refresh/06_visual_qa_and_branching.md)
- existing design direction docs.

## Done Criteria

The frontend refresh is complete when:

- a first-time user can start at intake and understand what to do next;
- school review is primarily card-based;
- rankings still support advanced table review without being the only useful surface;
- Interested/Applying list management is obvious and bounded;
- school profiles are readable without exposing raw admin details first;
- methodology explains deterministic rules, missing data, and source confidence;
- publish-safe GitHub Pages deployment still succeeds;
- screenshot QA covers desktop and mobile for intake, rankings, schools, applications, score cards, methodology, and admin fallback.

