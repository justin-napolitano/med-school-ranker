# Headless Product Site Rebuild Execution Plan

## Current Status

This plan is executable when the product-site rebuild is explicitly selected, but it should now run after the site data-modeling/card-contract work in `docs/HEADLESS_SITE_DATA_MODELING_EXECUTION_PLAN.md`.

If this product-site plan is run before JSON node/card contracts exist, limit the first slice to route shell, admin separation, and publish-safe scaffolding. Do not build polished card/profile UX that depends on node fields that do not exist yet.

## Objective

Execute the product-site rebuild independently from the current repository state, without asking follow-up questions unless a true blocker prevents progress.

The worker should implement the applicant-facing site upgrade described in [Product Site Rebuild Executive Plan](SITE_PRODUCT_REBUILD_EXEC_PLAN.md), while preserving the existing static build path and local workbook/data workflows.

## Execution Mode

- Run non-interactively.
- Read this plan first, then the product rebuild executive plan and child plans.
- Work from the current repo state.
- Do not bypass the data-modeling contract for card/profile surfaces. If card/profile node fields are missing, implement only safe scaffolding or stop with a concrete gap report.
- Prefer incremental implementation with passing tests after each major phase.
- Keep generated outputs in sync when source CSVs or site payloads change.
- Preserve private-data exclusions.
- Do not introduce a backend.
- Do not add GitHub Pages deployment wiring in this loop.
- Do not treat admin-shaped aggregate payloads as final product card contracts.

## Starting Commands

Run at the start:

```bash
git status --short
uv run pytest
uv run med-school-build-all
```

If the tree is dirty, inspect the dirty files before editing. Treat existing dirty changes as user/worker work and do not revert them.

## Required Plan Inputs

Read:

```text
docs/SITE_PRODUCT_REBUILD_EXEC_PLAN.md
docs/site/product_rebuild/01_routes_and_information_architecture.md
docs/site/product_rebuild/02_rankings_and_list_builder.md
docs/site/product_rebuild/03_school_profiles.md
docs/site/product_rebuild/04_curated_lists_and_scoring_lenses.md
docs/site/product_rebuild/05_admin_publish_safe.md
docs/site/product_rebuild/06_visual_reporting_quality.md
docs/site/product_rebuild/CRITICAL_REVIEW.md
```

Use the older `docs/SITE_EXEC_PLAN.md` only as baseline context, not as the current product UX decision.

## Headless Loop

Repeat this loop until all required phases pass verification:

1. **Audit**
   - Check `git status --short`.
   - Read relevant source files and tests.
   - Confirm current generated payload row counts.
   - Identify whether any existing worker changes affect the current phase.

2. **Plan the Slice**
   - Choose the smallest phase slice that can be completed and tested.
   - State assumptions in code comments or docs only where needed.
   - Do not broaden scope into unrelated refactors.

3. **Implement**
   - Update schemas, payload builder, route rendering, styles, and tests as needed.
   - Keep public routes and admin routes separated.
   - Keep missing data visible.
   - Keep AAMC grid language as national aggregate context.

4. **Regenerate**
   - Run build commands required by the files changed.
   - If site source or payload changes, regenerate `outputs/site/`.
   - If workbook/source data changes, run `uv run med-school-build-all`.

5. **Verify**
   - Run `uv run pytest`.
   - Run `uv run med-school-build-all`.
   - Inspect payload counts and publish-safe/private-data checks.
   - For visual phases, run screenshot or browser smoke checks when tooling is available.

6. **Review**
   - Check `git diff --stat`.
   - Review changed files for accidental private/admin leaks.
   - Ensure generated artifacts match source changes.
   - Write a concise handoff summary with commands run and known residual risks.

## Phase Order

### Phase 0: Guardrails and Readiness

- Add or verify `local_full` and `publish_safe` site mode scaffolding.
- Split route/payload planning into product-safe and admin-local sections before moving admin views.
- Add school/list slug generation to the payload contract.
- Add AAMC grid caveat text as reusable display copy.
- Add curated-list field-readiness metadata so missing `ownership_type`, `region`, city, culture, scoring, or cost fields produce provisional list status.
- Add tests for publish-safe exclusion and provisional curated-list behavior before deeper UI work.

### Phase 1: Route Shell

- Default route becomes `#/rankings`.
- Public and admin route groups are separated.
- School/list/admin routes are hash-addressable.
- Tests cover default route and route payload.

### Phase 2: Rankings and Lens UI

- Rankings becomes the primary value surface.
- Add filters and scoring lens controls.
- Add reason chips and shortlist/list-builder controls.
- Preserve sortable table behavior.
- If Phase 2B deterministic scoring has not been implemented, keep lens behavior scaffolded or visibly provisional.

### Phase 3: School Profiles

- Add `#/schools/:school_slug`.
- Add profile payloads and sections.
- Link profile routes from rankings and lists.
- Add confidence/risk/source panels.

### Phase 4: Curated Lists

- Add curated-list and scoring-profile schemas.
- Add seeded lists.
- Add list index and list detail routes.
- Add apply-lens behavior.
- Defer high-confidence curated-list claims until required scoring/profile fields exist.

### Phase 5: Admin and Publish-Safe

- Move dashboard/status/source/data-quality/build-health into admin routes.
- Add `local_full` and `publish_safe` modes.
- Test that publish-safe output excludes private/admin payloads.

### Phase 6: Visual and Reporting Polish

- Upgrade visual system.
- Add mobile and desktop smoke checks.
- Verify no overlapping text or incoherent table overflow.
- Confirm public routes feel like a polished reporting product.

## Required Verification

At the end of the loop, all must pass:

```bash
uv run med-school-build-all
uv run pytest
```

Required checks:

- `outputs/site/index.html` exists.
- `#/rankings` is the default user-facing route.
- `#/admin` routes exist only in local/full mode.
- `#/schools/:school_slug` resolves for every active school.
- `#/lists/:list_slug` resolves for every enabled curated list.
- A curated list can be applied as filter, boost, or replacement scoring.
- Publish-safe output excludes private/admin data.
- Curated list field-readiness metadata prevents high-confidence claims from missing fields.
- AAMC grid caveat text appears wherever AAMC rate/band context is exposed.
- Site payload active school count matches `data/school_master.csv`.
- AAMC grid has 110 rows when source integration has been run.
- Puerto Rico remains excluded from active school data.

## Stop Conditions

Stop and report a blocker only if:

- required source files are missing and cannot be generated;
- tests fail for reasons unrelated to the current work and cannot be isolated;
- the current tree has conflicting edits in the same files that make the next step unsafe;
- publish-safe exclusion cannot be implemented without schema or product decisions not covered by these plans;
- curated-list field readiness cannot be represented without adding schema that conflicts with existing scoring work;
- required browser/screenshot tooling is unavailable for visual QA after implementation otherwise passes.

## Do Not Do

- Do not revert dirty worker changes.
- Do not hide admin data while still embedding it in publish-safe payloads.
- Do not infer public/private/culture/city facts without source or manual review fields.
- Do not claim school-specific admissions probability from the AAMC grid.
- Do not add real applicant/private data.
- Do not wire deployment before publish-safe mode passes tests.

## Handoff Format

Each worker should close with:

- implemented phases;
- files changed;
- generated outputs changed;
- commands run;
- failing or skipped checks;
- residual risks;
- next recommended slice.
