# Headless React App Shell Execution Plan

## Objective

Provide a complete, branch-scoped execution guide for a headless Codex worker to implement the React app shell without new product decisions.

## Starting Rule

Start from current `main` unless the user explicitly says to continue an existing app-shell branch:

```bash
git switch main
git pull --ff-only
git status --short --branch
git switch -c impl-react-app-shell
```

If `impl-react-app-shell` or `build-react-app-shell` already exists, inspect it first:

```bash
git status --short --branch
git log --oneline --decorate -8
git diff --stat main...HEAD
```

Do not overwrite unrelated work. Untracked screenshot files under `outputs/site_qa/screenshots/` may exist; do not stage them unless this exact run intentionally updates QA artifacts.

## Read Order

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/REACT_APP_SHELL_EXEC_PLAN.md`
3. `docs/site/react_app_shell/01_architecture_and_route_contract.md`
4. `docs/site/react_app_shell/02_shared_local_state_refactor.md`
5. `docs/site/react_app_shell/03_route_views_and_profile_contract.md`
6. `docs/site/react_app_shell/04_navigation_and_static_export.md`
7. `docs/site/react_app_shell/05_performance_and_loading_ux.md`
8. `docs/site/react_app_shell/06_qa_deploy_and_smoke.md`
9. `docs/site/react_app_shell/CRITICAL_REVIEW.md`
10. `docs/site/react_app_shell/HEADLESS_PROMPT.md`
11. `docs/SITE_VISUAL_DIRECTION_PLAN.md`
12. `docs/SITE_TEXT_AND_FRONTEND_FORMATTING_EXEC_PLAN.md`
13. `docs/site/design_direction/01_audience_and_voice.md`
14. `docs/site/design_direction/04_transparency_and_trust_patterns.md`

## Execution Slices

Prefer one implementation branch and one PR for this pass because the route shell, shared state, and page wrappers are tightly coupled.

If the worker needs smaller commits, use this commit sequence on the same branch:

1. route utilities and shared local state type;
2. route component refactor to accept shared state;
3. `ProductAppShell` and Astro route wrappers;
4. methodology/profile React views;
5. smoke checks and QA fixes.

Do not split into separate PRs unless the first slice leaves the site in a working state.

## Required Commands

Run before committing:

```bash
cd frontend
npm run build
npm run smoke
cd ..
git diff --check
```

Run broader project validation when Python/generated outputs are touched:

```bash
uv run med-school-validate
uv run pytest
```

If the implementation only touches frontend source and no generated Python pipeline outputs, record that broader validation was not necessary.

## Browser QA

Manual QA or automated browser QA must check:

- first load of `/`;
- confirm first load may render defaults and then update from browser-local state without blocking the page;
- click Build My List, Interested, Applying, Not Interested, Compare, Scoring, Methodology;
- click a school Profile link from a card;
- click Interested/Applying/Not Interested/Compare actions from a school profile;
- browser back and forward;
- edit MCAT/GPA and navigate to another applicant route;
- confirm menus remain stable after browser-local state has updated from defaults;
- click Interested/Applying/Not Interested/Compare from cards;
- update scoring sliders and confirm scoring output changes;
- confirm `/admin/` is not visible in normal applicant navigation;
- open `/admin/` directly and confirm it remains a normal separate page;
- confirm `/recommendations/` is deprecated or aliased to Build My List and is not a second recommendation workflow;
- hard refresh on `/interested/`, `/scoring/`, and one `/schools/:slug/` route;
- run build with `ASTRO_BASE_PATH=/med-school-ranker` if practical.

## Headless Codex Command

Only run this after user approval for privileged sandbox execution:

```bash
codex exec --dangerously-bypass-approvals-and-sandbox "$(cat docs/site/react_app_shell/HEADLESS_PROMPT.md)"
```

If the local Codex CLI uses a different danger-sandbox flag, use the installed CLI's documented equivalent. The worker must still follow the repo commit rules and must not run destructive git commands.

## PR Handoff

When done, push the branch and create a PR only if the user asks. PR body should include:

- app shell architecture summary;
- changed routes;
- state persistence behavior;
- static hosting compatibility;
- commands run;
- known limitations.
