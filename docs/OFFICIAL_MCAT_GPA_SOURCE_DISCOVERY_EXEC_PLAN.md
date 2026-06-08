# Official MCAT/GPA Source Discovery Executive Plan

## Objective

Build a repeatable pipeline that finds and verifies official school-published MCAT/GPA sources, then uses those sources to upgrade `data/normalized/admissions_stats.csv` and school profile links without treating third-party pages or AI summaries as source truth.

The target user outcome is simple: every school profile should show the school website, the official admissions/class-profile source when available, the MCAT/GPA values taken from that source, the metric definition, and a clear data-quality label.

## Current Problem

Current GPA/MCAT coverage is useful but mostly provisional:

- `data/normalized/admissions_stats.csv` is populated from approved third-party candidate averages and AAMC aggregate grid context.
- Many rows use `third_party_published_average_*` or `assumed_match_review_*` confidence labels.
- `data/school_master.csv` already has `website` and `admissions_source_url`, but admissions stats and school profile links do not yet consistently point to official class-profile or annual-report sources.
- `data/manual/admissions_source_queue.csv` exists but only has a minimal candidate URL/review schema.

The next step is not another single scrape. It is a source-discovery and evidence pipeline.

## Source Hierarchy

Use this hierarchy when selecting values for official stat fields:

1. **Official school admissions/class profile page**
   Example classes of pages: `class profile`, `entering class`, `student profile`, `admissions statistics`, `facts and figures`.

2. **Official school or university annual report / fact book / PDF**
   Accept only when the document identifies the medical school or MD/DO program and the metric population is clear.

3. **Official AAMC/MSAR public advisor report**
   Use where public and permitted, but do not scrape restricted MSAR access.

4. **Third-party source consensus**
   Keep as provisional fallback only. Do not relabel it as official.

5. **Crowdsourced source**
   Keep as context only unless explicitly marked as crowdsourced.

AI search summaries, Google AI Overview text, snippets, and generic search-result snippets are discovery hints only. They must never populate normalized official stats unless a fetched official source supports the value.

## Non-Goals

- Do not bypass login gates, robots restrictions, paywalls, or restricted MSAR content.
- Do not use AI-generated summaries as evidence.
- Do not infer MCAT/GPA values from admission requirements, minimums, percentile bands, or applicant advice pages.
- Do not overwrite third-party provisional rows; add official rows alongside them and let downstream selection rules choose higher-quality rows.
- Do not require perfect coverage before the pipeline is useful.
- Do not mix accepted, admitted, matriculated, enrolled, applicant, and interviewed populations.

## Target Files

New or expanded data contracts:

```text
data/manual/admissions_source_queue.csv
data/source_tables/official_mcat_gpa_source_candidates.csv
data/source_tables/official_mcat_gpa_extracted_values.csv
data/normalized/admissions_stats.csv
outputs/official_mcat_gpa_discovery_report.csv
outputs/official_mcat_gpa_review_queue.csv
outputs/official_mcat_gpa_conflicts.csv
outputs/official_mcat_gpa_coverage.csv
```

Optional local-only cache:

```text
data/raw/public_school_sources/
```

Do not commit large HTML/PDF snapshots by default. Commit parsed source tables and manifests instead. If a snapshot is necessary for reproducibility, document why and confirm it is public and non-private.

## New Commands

Add these project scripts:

```bash
uv run med-school-discover-official-stats
uv run med-school-extract-official-stats
uv run med-school-apply-official-stats
```

Suggested Python entry points:

```text
src/med_school_ranker/official_stats_discovery.py:main
src/med_school_ranker/official_stats_extraction.py:main
src/med_school_ranker/official_stats_apply.py:main
```

The commands must be idempotent and deterministic. Rerunning them should produce stable CSV ordering and should not overwrite human review notes.

## Implementation Slices

1. **Source Discovery Contract**
   - Expand `data/manual/admissions_source_queue.csv` to include candidate URLs, source type, search query, source host, discovery method, official-domain score, and review status.
   - Generate `data/source_tables/official_mcat_gpa_source_candidates.csv` from existing school websites plus optional search results.
   - Use search only when network and a provider are configured. Otherwise accept manual queue rows.

2. **Official Source Acceptance Rules**
   - Implement a URL classifier that scores whether a candidate URL belongs to the school, university, health system, or a known official PDF host.
   - Reject social posts, forums, consultant blogs, admissions-services pages, cached search snippets, and generic third-party aggregators.
   - Mark ambiguous university-wide pages for review rather than accepting them automatically.

3. **Extraction and Normalization**
   - Fetch public HTML/PDF content.
   - Extract candidate MCAT/GPA values with rule-based patterns first.
   - Record surrounding evidence text, document title, class/cohort year, metric population, and metric type.
   - Do not accept values unless they pass numeric ranges and context checks.

4. **Human Review and Conflict Handling**
   - Write all ambiguous, conflicting, or low-context values to `outputs/official_mcat_gpa_review_queue.csv`.
   - Preserve review decisions in `data/manual/admissions_source_queue.csv`.
   - Treat official source conflicts as higher priority than third-party conflicts and do not silently average official rows with third-party rows.

5. **Apply to Normalized Admissions Stats**
   - Add official rows to `data/normalized/admissions_stats.csv` with `data_confidence=official_public_source_*`.
   - Preserve third-party rows.
   - Update downstream selection rules so official public rows beat third-party provisional rows when metric population and metric type are acceptable.

6. **Dossier and Site Integration**
   - School cards and profile pages should link to:
     - `website` from `data/school_master.csv`
     - selected official stats source URL when available
     - fallback provisional source URL when no official source exists
   - Labels must say `Official source`, `Provisional third-party source`, `Crowdsourced context`, or `Missing official source`.

## Definition of Done

- Source discovery creates a reviewable candidate table for all active schools.
- Extraction produces source-linked official MCAT/GPA rows where public sources exist.
- Every accepted official value has source URL, title, checked date, class/cohort year or documented ambiguity, population, metric type, and evidence text.
- `data/normalized/admissions_stats.csv` contains official rows without deleting provisional rows.
- The site shows official source links and source-quality labels on school profiles.
- Validation prevents out-of-range values and rejects AI/search summaries as evidence.
- A coverage report lists official coverage, provisional-only coverage, missing official source, and blocked/manual review counts.
