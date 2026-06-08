# MD Official Stats Discovery Executive Plan

## Objective

Build a separate MD-school official stats discovery pipeline that improves MCAT/GPA source quality where official public MD sources exist, without pretending that MD schools have the same centralized reporting structure as DO schools.

The MD path should be conservative, coverage-oriented, and explicit about missing official values.

## Source Reality

Unlike DO schools, MD schools do not have an AACOM-style centralized public profile page with school-level mean MCAT/GPA values. MD coverage must be treated as opportunistic and fragmented.

Valid MD official source classes:

1. Official school admissions/class profile pages.
2. Official school, university, or health-system annual reports/fact books.
3. State or application-system reports, where public and school-specific.
4. AAMC public MSAR advisor reports for non-score fields and any public school-specific fields they expose.

Invalid as official evidence:

- Google AI Overview text.
- Search snippets.
- Consultant pages.
- Forums.
- Crowdsourced spreadsheets.
- Admissions minimums or eligibility requirements.

## Non-Goals

- Do not create a single MD scraper that assumes every school has class-profile stats.
- Do not treat AAMC aggregate MCAT/GPA grid values as school-level MD statistics.
- Do not scrape restricted MSAR content.
- Do not use third-party values unless labeled provisional.
- Do not silently average official MD rows with third-party rows.

## New Commands

Use MD-specific command names so this pipeline can evolve independently:

```bash
uv run med-school-discover-md-official-stats
uv run med-school-extract-md-official-stats
uv run med-school-apply-md-official-stats
```

Suggested modules:

```text
src/med_school_ranker/md_official_discovery.py
src/med_school_ranker/md_official_extraction.py
src/med_school_ranker/md_official_apply.py
```

## Data Outputs

Create these files:

```text
data/source_tables/md_official_source_candidates.csv
data/source_tables/md_official_extracted_stats.csv
outputs/md_official_coverage.csv
outputs/md_official_review_queue.csv
outputs/md_official_conflicts.csv
```

Candidate columns:

```text
school_id
school_name
degree_type
state_abbrev
school_website
candidate_source_url
candidate_source_title
candidate_source_type
source_host
official_domain_status
official_domain_score
discovery_method
search_or_sitemap_query
source_last_checked
fetch_status
review_status
notes
```

Extracted columns:

```text
school_id
school_name
degree_type
candidate_source_url
candidate_source_title
candidate_source_type
stats_cohort_year
metric_population
metric_type
mcat_value
mcat_metric
gpa_value
gpa_metric
evidence_text
source_publication_date
source_last_checked
data_confidence
review_status
notes
```

## Discovery Strategy

Use deterministic official-domain discovery before any optional search provider.

1. Read active `degree_type=MD` rows from `data/school_master.csv`.
2. Seed each school with `website` and existing `admissions_source_url`.
3. Fetch official-domain `robots.txt` and parse `Sitemap:` entries.
4. Fetch likely sitemap URLs:
   - `/sitemap.xml`
   - `/sitemap_index.xml`
   - `/wp-sitemap.xml`
5. Filter discovered URLs by path/title terms:
   - `class-profile`
   - `entering-class`
   - `student-profile`
   - `facts-and-figures`
   - `admissions-statistics`
   - `annual-report`
   - `fact-book`
6. Crawl only one-hop links from official admissions pages when sitemap coverage is missing.
7. Keep every candidate tied to an official domain score and discovery method.

Do not use Google snippets as values. If optional web search is added later, search results can only create candidate URLs, and candidate URLs still must pass the official-source classifier and fetched-evidence checks.

## State/Application-System Special Cases

Handle these as explicit adapters, not as generic MD rules:

- `TMDSAS`: Texas MD schools may have public application-system statistics.
- State university systems: only if a public school-specific report exists.
- AAMC public reports: use for public fields where allowed, but keep school-specific score extraction separate unless the report actually provides school-level MCAT/GPA values.

Each adapter must document:

- source URL,
- permitted use,
- school matching logic,
- metric population,
- cohort year,
- extraction confidence.

## Extraction Strategy

Reuse the official extraction engine but with MD-specific source acceptance.

Accept only when context includes class/profile/report language:

- `entering class`
- `matriculants`
- `enrolled students`
- `accepted students`
- `class profile`
- `facts and figures`
- `annual report`

Reject or review:

- `minimum MCAT`
- `minimum GPA`
- `requirement`
- `eligibility`
- `screen`
- `recommended`
- `competitive applicants`

Metric policy:

- Preserve `mean` vs `median`.
- Preserve accepted vs matriculated/enrolled populations.
- Prefer matriculated/enrolled for score-screen fit if both are available.
- Do not collapse conflicting official rows without a deterministic policy.

## Apply Strategy

Append accepted MD official rows to `data/normalized/admissions_stats.csv` with:

```text
metric_population={matriculated/enrolled/accepted/official profile}
metric_type=md_official_published_{mean|median|value}
source_name=Official MD school source
source_url={candidate_source_url}
data_confidence=md_official_public_source
```

Selection policy:

- MD official rows beat third-party provisional rows when both MCAT and GPA are present and source context is clear.
- Third-party rows remain visible as fallback/context.
- Partial official rows go to review unless they improve one missing field without creating a misleading pair.

## Site Integration

For MD school profiles:

- Show `Official MCAT/GPA source` only when an accepted official row exists.
- Show `Provisional third-party source` when official source is missing.
- Show `Official source missing` when no official source exists.
- Do not make the absence of official MD stats look like a data failure; it is expected for many schools.

## Validation

Add validation that:

- MD official rows must have `degree_type=MD`.
- Candidate source URLs must pass official-domain checks or adapter-specific official-source checks.
- Search, AI, forum, and consultant hosts cannot have `data_confidence=md_official_public_source`.
- Accepted rows must include evidence text and source URL.
- Minimum requirement contexts cannot be accepted.

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

## Definition Of Done

- MD discovery produces a candidate table from official domains without using Google/AI snippets as evidence.
- Accepted MD rows are limited to official public sources with clear context.
- Coverage distinguishes accepted official, official candidate pending review, provisional-only, and no official source found.
- Site labels make MD official coverage opportunistic rather than expected.
- The MD flow remains separate from the DO/AACOM importer.
