# Headless Prompt: School Browser And Overrides

You are working in the `med-school-ranker` repo.

Implement the school-browser and per-school override slice described in:

```text
docs/SCHOOL_BROWSER_OVERRIDES_EXEC_PLAN.md
docs/HEADLESS_SCHOOL_BROWSER_OVERRIDES_PLAN.md
docs/site/school_browser_overrides/01_route_and_navigation_contract.md
docs/site/school_browser_overrides/02_school_card_grid_and_search.md
docs/site/school_browser_overrides/03_per_school_override_model.md
docs/site/school_browser_overrides/04_profile_and_compare_integration.md
docs/site/school_browser_overrides/05_local_storage_export_reset_privacy.md
docs/site/school_browser_overrides/06_qa_claim_safety_and_deploy.md
docs/site/school_browser_overrides/CRITICAL_REVIEW.md
```

## Requirements

- Add `/schools/` as a static Astro route inside `ProductAppShell`.
- Keep `/schools/:slug/` working as direct static profile routes.
- Add `Schools` to applicant shell nav.
- Build a school-browser card grid for the full school universe.
- Add text search, state filter, degree filter, status filter, override filter, and sort.
- Extend shared local state with browser-local per-school scoring overrides.
- Show `Global Score` and `Adjusted Score` separately when an override exists.
- Add a visible `Override applied` chip.
- Add edit/reset override controls.
- Keep global scoring unchanged.
- Do not silently reorder Build My List based on school-specific overrides.
- Update profiles and compare/list cards enough that override state is visible.
- Keep `/admin/` outside the applicant shell.
- Keep `/recommendations/` deprecated as a Build My List alias.
- Do not add predictive admissions claims.

## Verification

Run:

```bash
cd frontend
npm run build
npm run smoke
ASTRO_BASE_PATH=/med-school-ranker npm run build
ASTRO_BASE_PATH=/med-school-ranker npm run smoke
```

Run:

```bash
git diff --check
```

If browser tooling is available, run a headless browser QA pass for `/schools/`, profile navigation, override apply/reset persistence, shell nav without full reload, direct refreshes, and admin separation.

## Commit

Commit only intended files.

Do not stage unrelated untracked screenshot artifacts.

Use:

```text
Add school browser overrides
```

