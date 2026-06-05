# Product Site Rebuild Critical Review

## Findings

### High: Product rebuild requires an explicit headless loop

Without a headless execution plan, a worker could read the product UX docs but still stop for clarification about sequence, verification, or dirty generated outputs. The rebuild needs an independent loop that tells the worker how to audit, implement, regenerate, verify, and hand off.

Resolution:

- `docs/HEADLESS_PRODUCT_SITE_REBUILD_EXECUTION_PLAN.md` defines the independent execution loop, phase order, commands, stop conditions, and handoff format.

### High: Publish-safe mode must remove payloads, not just hide admin routes

The current static architecture embeds data in the generated HTML. A hidden admin tab is not security if admin/private rows still exist in `site_payload.json` or embedded JSON.

Resolution:

- `05_admin_publish_safe.md` requires separate `local_full` and `publish_safe` payload behavior.
- The headless plan requires publish-safe exclusion tests.

Residual risk:

- Implementation must actually split product-safe and admin-local payloads before any public publishing.

### High: Curated lists depend on missing or immature fields

Lists such as best cities, best culture fit, best public, and best private require fields that are not fully mature yet, especially `ownership_type`, `region`, city facts, and culture-fit evidence.

Resolution:

- `04_curated_lists_and_scoring_lenses.md` identifies the required field backlog and requires low-confidence labeling when facts are missing.

Residual risk:

- Early list pages should avoid overclaiming. They can ship as provisional if missing-data behavior is explicit.

### Medium: AAMC grid context can be misread as school-specific probability

The AAMC MCAT/GPA grid is national aggregate MD-granting-school context. If displayed casually, users may read it as a school-specific acceptance probability.

Resolution:

- School profile and ranking plans require explicit AAMC caveats.
- The headless plan forbids claiming school-specific probability from the AAMC grid.

### Medium: Existing Phase 1.5 plan conflicts with product UX direction

The old static-site plan says the dashboard is the default view. The product rebuild should default to rankings and move dashboard/status/admin surfaces under admin routes.

Resolution:

- `docs/SITE_EXEC_PLAN.md` now labels itself as the Phase 1.5 baseline and points to the product rebuild executive plan for current UX decisions.

### Medium: Visual quality needs objective QA, not taste-only review

"Beautiful" and "USNews-worthy" are subjective unless the worker has concrete checks. The plan needs visual acceptance criteria and screenshot/mobile smoke checks.

Resolution:

- `06_visual_reporting_quality.md` defines visual system requirements and QA checks.
- The headless plan requires screenshot or browser smoke checks when tooling is available.

Residual risk:

- If no browser/screenshot tooling is available, the worker must report that gap rather than pretending visual QA passed.

### Low: Current plan assumes static routing, which may eventually limit polish

Hash routing is fine for local static review and publish-safe GitHub Pages. A later framework migration could improve component structure, but it is not required to deliver value.

Resolution:

- The product plan permits the current static approach and does not block on framework migration.

## Independence Checklist

A headless worker can run independently if all are true:

- It can locate the controlling plan: `docs/SITE_PRODUCT_REBUILD_EXEC_PLAN.md`.
- It can locate the headless plan: `docs/HEADLESS_PRODUCT_SITE_REBUILD_EXECUTION_PLAN.md`.
- It knows the route split and default route.
- It knows which admin/private data must not ship in publish-safe mode.
- It knows the phase order.
- It has required commands and stop conditions.
- It has tests/verification expectations.
- It has explicit warnings about missing curated-list fields and AAMC grid caveats.

Current status:

- Executable when explicitly selected, but recommended after Phase 2B deterministic scoring.
- If run before scoring, start only with route shell/admin separation/publish-safe scaffolding.
- Data-contract and generator-splitting work can proceed separately, but scoring-dependent product UX should not overclaim.

## Recommended First Worker Slice

If this plan is explicitly selected before Phase 2B scoring is complete, start with route shell and admin separation only:

1. Add hash route state.
2. Make `#/rankings` the default route.
3. Move dashboard/status pages under `#/admin`.
4. Add school slug generation.
5. Add tests for default route, admin route, and profile route resolution.
6. Run `uv run med-school-build-all` and `uv run pytest`.

This slice creates the product/admin boundary before adding curated-list and profile complexity.
