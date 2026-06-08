You are running inside `/Users/justin/repos/med-school-ranker`.

Implement the official public MCAT/GPA source-discovery pipeline described in:

- `docs/OFFICIAL_MCAT_GPA_SOURCE_DISCOVERY_EXEC_PLAN.md`
- `docs/HEADLESS_OFFICIAL_MCAT_GPA_SOURCE_DISCOVERY_PLAN.md`
- `docs/source_discovery/01_source_discovery_contract.md`
- `docs/source_discovery/02_official_source_acceptance_rules.md`
- `docs/source_discovery/03_extraction_and_normalization.md`
- `docs/source_discovery/04_review_queue_and_conflict_resolution.md`
- `docs/source_discovery/05_dossier_and_payload_integration.md`
- `docs/source_discovery/06_qa_validation_and_resilience.md`
- `docs/source_discovery/CRITICAL_REVIEW.md`

Rules:

- Do not use AI summaries, search snippets, or LLM-generated text as evidence.
- Only fetched official school/university/health-system pages or PDFs can create official normalized MCAT/GPA rows.
- Preserve existing third-party/provisional rows in `data/normalized/admissions_stats.csv`.
- Preserve manual review notes in `data/manual/admissions_source_queue.csv`.
- Do not stage untracked screenshot artifacts under `outputs/site_qa/screenshots/`.
- If network is unavailable, implement the commands and process only existing/manual candidate URLs.
- Prefer conservative review rows over false confidence.

Expected implementation:

1. Add source-discovery, extraction, apply, and official-source-rule modules.
2. Add CLI entry points in `pyproject.toml`.
3. Expand/migrate `data/manual/admissions_source_queue.csv` schema without deleting rows.
4. Generate official source candidate, extracted values, review, conflict, and coverage CSVs.
5. Append safe official rows to `data/normalized/admissions_stats.csv` while retaining provisional rows.
6. Extend payload/profile UI with school website and stats source links plus official/provisional/missing labels.
7. Add validation guardrails for source URLs, value ranges, source type, and minimum-requirement misuse.

Run verification:

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

Commit the finished work with a concise message if all required verification passes or if failures are clearly documented and non-blocking for the scaffold.
