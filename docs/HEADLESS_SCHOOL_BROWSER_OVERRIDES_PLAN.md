# Headless School Browser Overrides Execution Plan

## Objective

Implement `/schools/` as a school browser inside the React app shell and add browser-local per-school scoring overrides with transparent adjusted-score display.

## Starting Point

Expected branch context:

```text
impl-react-app-shell
```

Expected existing shell routes:

```text
/
/interested/
/applying/
/not-interested/
/compare/
/scoring/
/methodology/
/schools/:slug/
```

Do not remove or rewrite the current app shell.

## Required Docs

Read before implementing:

```text
docs/SCHOOL_BROWSER_OVERRIDES_EXEC_PLAN.md
docs/site/school_browser_overrides/01_route_and_navigation_contract.md
docs/site/school_browser_overrides/02_school_card_grid_and_search.md
docs/site/school_browser_overrides/03_per_school_override_model.md
docs/site/school_browser_overrides/04_profile_and_compare_integration.md
docs/site/school_browser_overrides/05_local_storage_export_reset_privacy.md
docs/site/school_browser_overrides/06_qa_claim_safety_and_deploy.md
docs/site/school_browser_overrides/CRITICAL_REVIEW.md
```

## Build Requirements

Implement:

- `Schools` shell nav item;
- static `/schools/` Astro wrapper;
- app-route resolver support for `/schools/`;
- React school-browser view component;
- shared local-state support for school-specific overrides;
- adjusted-score derivation without mutating global scoring inputs;
- override editor panel;
- reset controls;
- updated profile display for override state;
- smoke checks for route, nav, base path, claim safety, and override labels.

## Guardrails

- Keep Admin/Data out of applicant nav.
- Keep `/recommendations/` deprecated.
- Preserve direct static URLs.
- Preserve base-path safety for GitHub Pages.
- Do not treat per-school custom scoring as admissions probability.
- Do not hide global score when adjusted score exists.
- Do not store private applicant values outside browser local storage.
- Do not stage unrelated untracked screenshots.

## Verification Commands

Run from `frontend/`:

```bash
npm run build
npm run smoke
ASTRO_BASE_PATH=/med-school-ranker npm run build
ASTRO_BASE_PATH=/med-school-ranker npm run smoke
```

Also run:

```bash
git diff --check
```

If a browser is available, run headless QA against a local dev server and verify:

- `/schools/` loads as a shell route;
- shell nav does not full reload;
- direct refresh of `/schools/` works;
- direct refresh of `/schools/:slug/` still works;
- applying a school-specific override changes adjusted score display;
- reset removes the override;
- global score remains visible;
- actions update shared local state across school browser, profile, interested/applying, and compare routes.

## Commit

Use a focused commit message:

```text
Add school browser overrides
```

Do not commit pre-existing untracked screenshot artifacts unless the task explicitly asks for new screenshot outputs.

