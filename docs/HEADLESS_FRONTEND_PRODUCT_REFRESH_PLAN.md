# Headless Frontend Product Refresh Plan

## Objective

Execute the frontend product refresh in branch-scoped slices without asking follow-up questions unless a true blocker prevents progress.

This plan coordinates the child plans in `docs/site/frontend_refresh/` and supersedes older frontend slice plans as the next selected UI execution path.

## Starting Rule

Start from `main` for every slice:

```bash
git switch main
git pull --ff-only
git status --short --branch
```

Untracked screenshot files under `outputs/site_qa/screenshots/` may exist from previous QA runs. Do not commit them unless the current slice intentionally regenerates and reviews them.

## Read Order

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/FRONTEND_PRODUCT_REFRESH_EXEC_PLAN.md`
3. `docs/site/frontend_refresh/CRITICAL_REVIEW.md`
4. Relevant child plan for the selected slice
5. `docs/SITE_VISUAL_DIRECTION_PLAN.md`
6. `docs/SITE_GUIDED_INTAKE_EXEC_PLAN.md`
7. `docs/SITE_TEXT_AND_FRONTEND_FORMATTING_EXEC_PLAN.md`
8. `docs/site/data_modeling/02_json_node_contracts.md`
9. `docs/site/data_modeling/03_card_surfaces_and_profile_sections.md`

## Slice Branches

Create exactly one branch per slice unless the user requests otherwise:

```bash
git switch -c impl-frontend-route-shell
git switch -c impl-frontend-school-cards
git switch -c impl-frontend-intake-results
git switch -c impl-frontend-list-builder
git switch -c impl-frontend-score-card-profile
git switch -c impl-frontend-visual-polish
```

If a branch exists, inspect it before using it:

```bash
git status --short --branch
git log --oneline --decorate -5
git diff --stat main...HEAD
```

Do not overwrite unrelated work.

## Global Scope

### In Scope

- Improve public frontend workflow and presentation.
- Make card views the primary review surfaces.
- Keep advanced tables and admin/source views reachable.
- Use existing generated node data where possible.
- Add helper renderers only when they reduce duplication.
- Update docs, tests, generated site outputs, and publish-safe build artifacts as needed.

### Out Of Scope

- No scoring formula changes.
- No source data scraping.
- No predictive probability model.
- No database, backend, auth, Vercel, React, Next, or framework migration.
- No private applicant values in committed outputs.
- No removal of methodology/source confidence.

## Required Verification

Run for every implementation slice:

```bash
uv run med-school-build-site --site-mode publish_safe
uv run med-school-validate
uv run pytest
git diff --check
```

Run when source CSVs, generated outputs, workbook, or upload bundle behavior changes:

```bash
uv run med-school-build-all
```

Run a privacy smoke check before committing:

```bash
uv run python -c "import html,json,re; from pathlib import Path; text=Path('outputs/site/index.html').read_text(); payload=json.loads(html.unescape(re.search(r'<script type=\"application/json\" id=\"site-data\">(.*?)</script>', text, re.S).group(1))); print(payload['meta'].get('site_mode')); print(payload['routes'].get('admin', [])); raise SystemExit(0 if payload['meta'].get('site_mode') == 'publish_safe' and not payload['routes'].get('admin') else 1)"
```

Run screenshot QA when the slice changes visible layout and the tooling is already available:

```bash
SITE_QA_BASE_URL=http://127.0.0.1:8766 CHROME_DEBUG_PORT=9231 node scripts/capture_site_qa.mjs frontend_refresh
```

Do not install browser dependencies without user approval.

## Suggested Headless Prompt

Use this template and replace `{SLICE_DOC}` and `{BRANCH}`:

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute {SLICE_DOC} end to end as the next frontend product refresh slice.

Follow docs/HEADLESS_WORKER_RUNBOOK.md and docs/HEADLESS_FRONTEND_PRODUCT_REFRESH_PLAN.md first. Start from main, pull latest, create or reuse branch {BRANCH} only after inspecting status, and preserve unrelated untracked screenshot files.

Make the public site more applicant-facing and card-first while preserving deterministic scoring, source transparency, advanced tables, local review state, publish-safe GitHub Pages output, and admin routes in local_full mode.

Do not change scoring formulas. Do not scrape/download data. Do not implement predictive admissions probability. Do not migrate frameworks or persistence. Do not commit private applicant answers or private-derived outputs.

Regenerate required site outputs, run uv run med-school-build-site --site-mode publish_safe, uv run med-school-validate, uv run pytest, git diff --check, the publish-safe privacy smoke check, and screenshot QA if dependencies are already available. Commit only the intended public-safe code/docs/generated outputs.
```

## Handoff Requirements

Every completed slice must report:

- branch name;
- commit hash;
- routes changed;
- public-safe payload mode result;
- tests/build commands run;
- screenshot QA result or reason it was skipped;
- known limitations and next slice.

