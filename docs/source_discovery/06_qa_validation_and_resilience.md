# 06 QA Validation And Resilience

## Validation

Extend validation to fail on:

- MCAT outside 472-528.
- GPA outside 0-4.0.
- normalized official rows with missing source URL.
- normalized official rows whose source URL is a search engine, AI answer page, or rejected third-party host.
- official rows with `metric_type=minimum_requirement` selected as score-driving stats.
- source rows with values but no `source_last_checked`.

Warn on:

- missing cohort year.
- unknown population.
- no official source candidate.
- official source conflict.
- official source extraction unavailable because PDF parsing is not installed.

## Headless QA

Run:

```bash
uv run med-school-discover-official-stats
uv run med-school-extract-official-stats
uv run med-school-apply-official-stats
uv run med-school-validate
uv run med-school-build-all
uv run pytest
cd frontend && npm run build
cd frontend && npm run smoke
cd frontend && ASTRO_BASE_PATH=/med-school-ranker npm run build
cd frontend && ASTRO_BASE_PATH=/med-school-ranker npm run smoke
git diff --check
```

## Resilience Rules

- Network failures create queue rows, not partial crashes.
- Fetch timeouts should be short and per-source.
- Content-size limits should prevent huge PDFs or pages from blocking a run.
- The pipeline should be resumable from candidate CSVs.
- Manual queue decisions must survive regeneration.
- Official source discovery should not block the app build.

## First-Pass Success Criteria

The first pass is successful even with incomplete coverage if it:

- builds schemas and commands,
- processes existing known school websites/admissions URLs,
- extracts a subset of safe official rows,
- emits clear coverage and review reports,
- updates profiles to show official/provisional/missing source status.
