# Headless MD Official Stats Discovery Plan

## Worker Objective

Implement the MD-only official public stats discovery pipeline described in `docs/MD_OFFICIAL_STATS_DISCOVERY_EXEC_PLAN.md`.

## Scope Rules

- Process only `degree_type=MD` schools.
- Treat official MD MCAT/GPA coverage as opportunistic.
- Use official-domain sitemaps, robots sitemap entries, existing official URLs, and explicit state/application-system adapters.
- Do not use AI summaries, search snippets, consultant pages, or forums as evidence.
- Do not modify the DO/AACOM importer in this run.

## Required Implementation

1. Add MD official discovery, extraction, and apply modules.
2. Add CLI scripts:
   - `med-school-discover-md-official-stats`
   - `med-school-extract-md-official-stats`
   - `med-school-apply-md-official-stats`
3. Create source tables and outputs named in the MD exec plan.
4. Add official-domain sitemap discovery with stable ordering.
5. Add one-hop official admissions-page link discovery only when bounded and deterministic.
6. Add validation for MD-only official source rows.
7. Add tests for:
   - sitemap URL filtering,
   - minimum requirement rejection,
   - class-profile extraction,
   - official vs provisional source selection.

## Verification

Run:

```bash
uv run med-school-discover-md-official-stats
uv run med-school-extract-md-official-stats
uv run med-school-apply-md-official-stats
uv run med-school-validate
uv run pytest
cd frontend && npm run build
cd frontend && npm run smoke
git diff --check
```

## Stop Conditions

Stop and report if:

- A source requires login, restricted MSAR access, or paywalled content.
- A value appears only in a search snippet or AI summary.
- Extraction cannot distinguish class profile stats from requirements/minimums.
- The implementation starts applying MD official rows without evidence text.
- The implementation starts modifying DO/AACOM rows.
