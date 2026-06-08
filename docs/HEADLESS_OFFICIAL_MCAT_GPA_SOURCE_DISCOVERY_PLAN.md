# Headless Execution Plan: Official MCAT/GPA Source Discovery

## Objective

Implement the official public source pipeline for school-published MCAT/GPA values without human follow-up during the first pass. The worker should produce reviewable source candidates, extracted values, normalized official rows, coverage reports, and site/profile links when the evidence is safe.

## Execution Mode

- Run non-interactively.
- Prefer deterministic parsing and conservative acceptance.
- Use network only if explicitly allowed by the execution environment.
- If network is unavailable, build the queue/import/apply scaffolding and process existing manual candidate URLs only.
- Do not use AI summaries, search snippets, or LLM-generated text as evidence.
- Do not bypass access restrictions.
- Do not overwrite manual review notes.
- Do not stage pre-existing untracked screenshot artifacts.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

## Required Plan Inputs

Read these before implementation:

```text
docs/OFFICIAL_MCAT_GPA_SOURCE_DISCOVERY_EXEC_PLAN.md
docs/source_discovery/01_source_discovery_contract.md
docs/source_discovery/02_official_source_acceptance_rules.md
docs/source_discovery/03_extraction_and_normalization.md
docs/source_discovery/04_review_queue_and_conflict_resolution.md
docs/source_discovery/05_dossier_and_payload_integration.md
docs/source_discovery/06_qa_validation_and_resilience.md
docs/source_discovery/CRITICAL_REVIEW.md
```

## Implementation Targets

Add modules:

```text
src/med_school_ranker/official_stats_discovery.py
src/med_school_ranker/official_stats_extraction.py
src/med_school_ranker/official_stats_apply.py
src/med_school_ranker/official_source_rules.py
```

Add scripts/entry points in `pyproject.toml`:

```text
med-school-discover-official-stats
med-school-extract-official-stats
med-school-apply-official-stats
```

Add or expand data files:

```text
data/manual/admissions_source_queue.csv
data/source_tables/official_mcat_gpa_source_candidates.csv
data/source_tables/official_mcat_gpa_extracted_values.csv
outputs/official_mcat_gpa_discovery_report.csv
outputs/official_mcat_gpa_review_queue.csv
outputs/official_mcat_gpa_conflicts.csv
outputs/official_mcat_gpa_coverage.csv
```

## Work Sequence

1. **Schema First**
   - Add schema constants for candidate, extracted, review, conflict, and coverage files.
   - Preserve existing rows in `data/manual/admissions_source_queue.csv`; migrate missing columns by appending blanks.

2. **Candidate Generation**
   - Seed one queue row per active school from `data/school_master.csv`.
   - Use `website` and `admissions_source_url` as first candidate URLs.
   - Generate search-query strings, but do not require live search for first-pass completion.
   - If a provider config exists, fetch search results and store candidate URLs with `discovery_method=search`.

3. **URL Classification**
   - Score hosts against school website host, university parent host, `.edu`, official health system domains, and known PDF/report hosts.
   - Reject obvious third-party and nonofficial hosts.
   - Mark ambiguous university-wide sources for review.

4. **Content Fetching**
   - Fetch only public HTTP(S) sources.
   - Respect timeouts and content-size limits.
   - Record status code, content type, final URL, title, and fetch errors.
   - Skip binary snapshots unless explicitly configured.

5. **Extraction**
   - Extract from HTML text and PDF text where supported.
   - Use strict patterns for MCAT and GPA near words such as `median`, `mean`, `average`, `matriculants`, `entering class`, `enrolled`, `accepted`, and `class profile`.
   - Reject MCAT minimums, requirements, oldest/latest MCAT dates, and advice content.
   - Store evidence snippets no longer than a short review excerpt.

6. **Normalize**
   - Append official rows to `data/normalized/admissions_stats.csv` only when source acceptance and extraction confidence pass thresholds.
   - Keep provisional third-party rows.
   - Add review rows when values conflict, population/year is unclear, or source officialness is ambiguous.

7. **Site Integration**
   - Extend payload shaping so profiles can display school website and official stats source.
   - Add labels that distinguish official, provisional, crowdsourced, and missing official stats.
   - Do not make acceptance-probability claims.

8. **Validation**
   - Extend `med-school-validate` or add validation helpers for:
     - MCAT 472-528
     - GPA 0-4.0
     - required source metadata when values are present
     - no `google.com/search`, AI overview, or search-result URLs as evidence
     - no unreviewed ambiguous official-source rows promoted to normalized official rows

## Verification Commands

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

If network access is unavailable, document that discovery was scaffolded and only existing/manual candidate URLs were processed.

## Stop Conditions

Stop and report if:

- A schema change would delete manual review notes.
- The normalized stats table cannot preserve existing provisional rows.
- Extraction starts accepting MCAT/GPA values from search snippets, AI text, or third-party pages as official.
- The site labels official/provisional/crowdsourced source types incorrectly.
- Validation cannot distinguish minimum requirements from class profile statistics.
