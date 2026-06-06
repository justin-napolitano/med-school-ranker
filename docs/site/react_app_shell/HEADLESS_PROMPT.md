You are working in /Users/justin/repos/med-school-ranker.

Implement the React app shell slice end to end.

Read these files first:

1. docs/HEADLESS_WORKER_RUNBOOK.md
2. docs/REACT_APP_SHELL_EXEC_PLAN.md
3. docs/HEADLESS_REACT_APP_SHELL_EXECUTION_PLAN.md
4. docs/site/react_app_shell/01_architecture_and_route_contract.md
5. docs/site/react_app_shell/02_shared_local_state_refactor.md
6. docs/site/react_app_shell/03_route_views_and_profile_contract.md
7. docs/site/react_app_shell/04_navigation_and_static_export.md
8. docs/site/react_app_shell/05_performance_and_loading_ux.md
9. docs/site/react_app_shell/06_qa_deploy_and_smoke.md
10. docs/site/react_app_shell/CRITICAL_REVIEW.md

Start from main unless the user explicitly told you to continue an existing branch:

```bash
git switch main
git pull --ff-only
git status --short --branch
git switch -c impl-react-app-shell
```

If an app-shell branch already exists, inspect it before reusing it. Do not overwrite unrelated work. Do not stage untracked screenshot artifacts under outputs/site_qa/screenshots unless this exact run intentionally updates them.

Goal:

Move the applicant-facing product into one persistent React app shell while keeping Astro static hosting. No database, no account system, no server persistence, no scoring formula changes, no source data changes, and no predictive admissions model.

Implement:

- ProductAppShell that owns one useLocalSchoolState instance.
- Route utilities for base-path-safe app routes.
- Shared local-state prop support for Build My List, Interested, Applying, Not Interested, Compare, and Scoring views.
- React methodology view preserving existing methodology caveats.
- React school profile view preserving existing profile content, using browser-local preferences for score-screen fit, and adding Interested/Applying/Not Interested/Compare actions.
- Existing applicant Astro routes rendering the same app shell with an initialPath.
- App-shell navigation with History API and popstate.
- Internal link handling that excludes external links, modified clicks, target/download links, and /admin/.
- Static direct URL support for all current applicant routes and school profiles.
- Admin/Data hidden from normal applicant navigation while remaining available at /admin/.
- /recommendations/ deprecated as a normal route; Build My List is the canonical recommendation/list-building route.
- First load may render default preferences and then update from browser-local state.
- Smoke checks updated for app-shell output and claim safety.

Keep /admin/ as a separate Astro page outside the applicant shell.

Verification:

```bash
cd frontend
npm run build
npm run smoke
cd ..
git diff --check
```

If generated Python pipeline outputs or Python code change, also run:

```bash
uv run med-school-validate
uv run pytest
```

If practical, run a base-path build:

```bash
cd frontend
ASTRO_BASE_PATH=/med-school-ranker npm run build
npm run smoke
```

Do not weaken smoke checks that guard against unsupported admissions claims. Do not introduce claims like guaranteed admission, safe school, best school, likely admitted, school-specific admit chance, or admissions probability.

Before committing, manually inspect git diff and ensure only intentional app-shell files are staged.

Commit with a focused message. Do not push unless explicitly asked.

Final report must include:

- branch name;
- commit hash;
- routes converted;
- components refactored;
- verification commands and results;
- browser QA result or skip reason;
- known limitations.
