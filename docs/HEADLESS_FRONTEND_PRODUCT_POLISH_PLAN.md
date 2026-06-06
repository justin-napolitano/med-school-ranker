# Headless Frontend Product Polish Plan

## Objective

Execute product polish in small, branch-scoped slices over the existing workflow.

This plan should not rebuild guided intake, rankings, list builder, score cards, methodology, or publish-safe deployment. It should make the already-built workflow feel like a polished applicant product.

## Starting Rule

Start every slice from `main`:

```bash
git switch main
git pull --ff-only
git status --short --branch
```

Untracked screenshot files under `outputs/site_qa/screenshots/` may exist from previous QA. Do not commit them unless the current slice intentionally reviews and replaces them.

## Read Order

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/FRONTEND_PRODUCT_POLISH_EXEC_PLAN.md`
3. `docs/site/product_polish/CRITICAL_REVIEW.md`
4. Relevant child plan for the selected slice
5. `docs/SITE_VISUAL_DIRECTION_PLAN.md`
6. `docs/SITE_TEXT_AND_FRONTEND_FORMATTING_EXEC_PLAN.md`
7. `docs/SITE_GUIDED_INTAKE_EXEC_PLAN.md`
8. `docs/site/design_direction/01_audience_and_voice.md`
9. `docs/site/design_direction/02_visual_system_foundations.md`
10. `docs/site/design_direction/03_cards_and_mobile_patterns.md`
11. `docs/site/design_direction/04_transparency_and_trust_patterns.md`
12. `docs/site/design_direction/05_design_qa.md`

## Slice Branches

Use one branch per slice:

```bash
git switch -c impl-product-polish-foundation
git switch -c impl-product-polish-intake-rankings
git switch -c impl-product-polish-score-cards
git switch -c impl-product-polish-applications-actions
git switch -c impl-product-polish-mobile
git switch -c impl-product-polish-qa
```

If a branch exists, inspect it first:

```bash
git status --short --branch
git log --oneline --decorate -5
git diff --stat main...HEAD
```

Do not overwrite unrelated work.

## Scope

### In Scope

- CSS, layout, spacing, typography, color, card hierarchy, responsive behavior.
- Applicant-facing copy and labels.
- Default visibility of admin/raw/source details.
- Status action presentation.
- School card and score-card readability.
- Screenshot QA and publish-safe smoke checks.

### Out Of Scope

- No scoring formula changes.
- No source data changes.
- No predictive model.
- No new workflow states.
- No backend/framework migration.
- No private applicant values in committed output.

## Required Verification

Run for every implementation slice:

```bash
uv run med-school-build-site --site-mode publish_safe
uv run med-school-validate
uv run pytest
git diff --check
```

Run when generated workbook/upload artifacts or CSVs change:

```bash
uv run med-school-build-all
```

Run a publish-safe smoke check before committing:

```bash
uv run python -c "import html,json,re; from pathlib import Path; text=Path('outputs/site/index.html').read_text(); payload=json.loads(html.unescape(re.search(r'<script type=\"application/json\" id=\"site-data\">(.*?)</script>', text, re.S).group(1))); print(payload['meta'].get('site_mode')); print(payload['routes'].get('admin', [])); raise SystemExit(0 if payload['meta'].get('site_mode') == 'publish_safe' and not payload['routes'].get('admin') else 1)"
```

Run screenshot QA when visible layout changes and tooling is available:

```bash
SITE_QA_BASE_URL=http://127.0.0.1:8766 CHROME_DEBUG_PORT=9231 node scripts/capture_site_qa.mjs product_polish
```

Do not install browser dependencies without approval.

## Suggested Headless Prompt

Use this template and replace `{SLICE_DOC}` and `{BRANCH}`:

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute {SLICE_DOC} end to end as the next frontend product polish slice.

Follow docs/HEADLESS_WORKER_RUNBOOK.md and docs/HEADLESS_FRONTEND_PRODUCT_POLISH_PLAN.md first. Start from main, pull latest, create or reuse branch {BRANCH} only after inspecting status, and preserve unrelated untracked screenshot files.

Polish the existing applicant workflow. Do not rebuild workflow. Improve visual hierarchy, card/report presentation, copy clarity, responsive behavior, and public/admin separation while preserving deterministic scoring, source transparency, advanced tables, local review state, publish-safe GitHub Pages output, and local admin routes.

Do not change scoring formulas. Do not scrape/download data. Do not implement predictive admissions probability. Do not migrate frameworks or persistence. Do not commit private applicant answers or private-derived outputs.

Regenerate required site outputs. Run uv run med-school-build-site --site-mode publish_safe, uv run med-school-validate, uv run pytest, git diff --check, the publish-safe smoke check, and screenshot QA if dependencies are already available. Commit only intended public-safe code/docs/generated outputs.
```

## Handoff Requirements

Every completed slice must report:

- branch name;
- commit hash;
- visual surfaces changed;
- public-safe smoke result;
- tests/build commands run;
- screenshot QA result or skip reason;
- known limitations and next polish slice.

