# Headless Site Text and Frontend Formatting Plan

## Worker Goal

Improve applicant-facing text and frontend formatting without changing scoring, source data, or stable export schemas.

## Required Context

Read first:

- `docs/SITE_TEXT_AND_FRONTEND_FORMATTING_EXEC_PLAN.md`
- `docs/site/text_frontend_formatting/CRITICAL_REVIEW.md`
- `src/med_school_ranker/site.py`
- `tests/test_phase1.py`

## Execution Steps

1. Start with a clean status check.
2. Work on a feature branch.
3. Scan generated UI source for confusing visible labels:
   - `Dossier`
   - `OOS`
   - `COA`
   - raw cost values
   - overflowing card text
4. Implement changes through the site builder, not only generated HTML.
5. Rebuild the site.
6. Run tests and validation.
7. Run screenshot or browser QA against:
   - guided intake desktop and mobile;
   - guided cards desktop and mobile;
   - rankings;
   - score-card index;
   - school profile;
   - compare.
8. Commit source, docs, generated site output, and intentional QA artifacts together.

## Verification Commands

```bash
uv run pytest tests/test_phase1.py
uv run med-school-validate
uv run med-school-build-site
```

When a server is available:

```bash
SITE_QA_BASE_URL=http://127.0.0.1:8766 CHROME_DEBUG_PORT=9231 node scripts/capture_site_qa.mjs text_frontend_formatting
```

## Guardrails

- Do not rename `school_dossiers.csv`, `school_dossier_edits_v1`, or existing local-storage keys in a formatting pass.
- Do not change decision rank, score formulas, weights, or data source precedence.
- Do not hide missing data to make the UI look cleaner.
- Do not add a framework migration.
- Do not use screenshots as the only proof; pair visual QA with automated tests and validation.

## Headless Prompt

```text
You are in /Users/justin/repos/med-school-ranker. Execute the Site Text and Frontend Formatting plan. Keep stable internal data contracts, but improve applicant-facing labels, score-card language, currency formatting, text wrapping, and interaction scroll stability. Do not change scoring formulas or source normalization. Rebuild the site, run tests and validation, run screenshot QA if the local server/browser tooling is available, then commit the work.
```

