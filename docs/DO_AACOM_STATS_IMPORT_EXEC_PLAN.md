# DO AACOM Stats Import Executive Plan

## Objective

Build a deterministic DO-school stats importer from AACOM-hosted College of Osteopathic Medicine profile pages. This should be a separate pipeline from MD official-source discovery because DO schools have a centralized AACOM profile surface with consistent MCAT/GPA labels.

The target output is a set of source-backed DO admissions stats rows with clear source labeling, evidence text, source URL, checked date, metric type, and coverage reporting.

## Source Scope

Primary source:

```text
https://www.aacom.org/detail-pages/com/{aacom-school-slug}
```

AACOM profile pages currently expose a consistent `MCAT/GPA Information` section with labels such as:

- `Mean MCAT Score`
- `Avg. Cum. Undergrad GPA Score`
- `Oldest MCAT Considered`
- `Latest MCAT Score Accepted`

Important source caveat: AACOM's Choose D.O. Explorer states that information is submitted by each College of Osteopathic Medicine and has not been verified by AACOM. Therefore rows should be labeled as `aacom_com_submitted_profile`, not as independently AACOM-verified.

## Non-Goals

- Do not mix this with MD school official-domain discovery.
- Do not scrape hidden Choose D.O. Explorer search results if they are not displayed to crawlers.
- Do not infer values from admissions minimums, MCAT date policies, or traffic guideline text.
- Do not relabel current third-party values as official.
- Do not delete existing provisional rows until selection rules explicitly prefer AACOM rows.

## New Commands

Add a dedicated command family rather than extending the generic official scanner too far:

```bash
uv run med-school-discover-aacom-do-profiles
uv run med-school-extract-aacom-do-stats
uv run med-school-apply-aacom-do-stats
```

Suggested modules:

```text
src/med_school_ranker/aacom_do_discovery.py
src/med_school_ranker/aacom_do_extraction.py
src/med_school_ranker/aacom_do_apply.py
```

## Data Outputs

Create these files:

```text
data/source_tables/aacom_do_profile_candidates.csv
data/source_tables/aacom_do_extracted_stats.csv
outputs/aacom_do_profile_coverage.csv
outputs/aacom_do_profile_review_queue.csv
outputs/aacom_do_profile_conflicts.csv
```

Candidate columns:

```text
school_id
school_name
degree_type
campus_name
state_abbrev
school_website
aacom_profile_url
aacom_profile_title
aacom_slug
match_status
match_score
match_reason
discovery_method
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
aacom_profile_url
aacom_profile_title
fetch_status
extraction_status
stats_academic_year
metric_population
metric_type
mcat_mean
overall_gpa_mean
oldest_mcat_considered
latest_mcat_accepted
evidence_text
source_last_checked
data_confidence
review_status
notes
```

## Discovery Strategy

Use deterministic discovery only:

1. Read active `degree_type=DO` rows from `data/school_master.csv`.
2. Fetch AACOM static site map or static page anchors if available.
3. Accept links matching `/detail-pages/com/`.
4. Match AACOM profile title to `school_name`, `campus_name`, and `source_acronym`.
5. If the Choose D.O. Explorer search results are hidden from crawlers, do not automate browser-only search in this slice.
6. Write unmatched DO schools to review, not guessed slugs.

Matching rules:

- Exact `source_acronym` or profile abbreviation match: safe.
- High token similarity on school name plus state match: safe.
- Multi-campus parent names without campus/location match: review.
- New/unlisted schools: review.

## Extraction Strategy

Parse fetched AACOM HTML as text and extract only values under `MCAT/GPA Information`.

Accept:

- `Mean MCAT Score` followed by a numeric value in 472-528.
- `Avg. Cum. Undergrad GPA Score` followed by a numeric value in 0-4.
- Optional MCAT date fields as metadata, not score inputs.

Reject:

- Admissions requirements.
- Minimum score requirements.
- Traffic guideline dates.
- Tuition/fee values.
- Any value outside allowed MCAT/GPA ranges.

## Apply Strategy

Append or promote AACOM rows into `data/normalized/admissions_stats.csv` with:

```text
metric_population=AACOM COM-submitted profile
metric_type=aacom_reported_mean
published_source_count=1
mcat_mean_enrolled={Mean MCAT Score}
overall_gpa_mean_enrolled={Avg. Cum. Undergrad GPA Score}
published_mcat_average={Mean MCAT Score}
published_gpa_average={Avg. Cum. Undergrad GPA Score}
source_name=AACOM Choose D.O. Explorer
source_url={aacom_profile_url}
data_confidence=aacom_com_submitted_profile
```

Selection policy:

- AACOM DO profile rows beat current third-party DO provisional rows for DO schools.
- AACOM rows do not override MD rows.
- If an AACOM row conflicts sharply with a current official school page, write conflict review and preserve both.

## Site Integration

For DO profiles:

- Show `AACOM profile` as a source link when present.
- Label the source as `COM-submitted AACOM profile`.
- Keep the source caveat visible in methodology: COM-submitted; not independently verified by AACOM.

## Validation

Add validation that:

- AACOM rows must have `degree_type=DO`.
- AACOM source URLs must be `aacom.org/detail-pages/com/...`.
- Accepted rows must include both MCAT and GPA values.
- `data_confidence=aacom_com_submitted_profile` must not be used for non-AACOM URLs.
- Multi-campus profile matches require state/campus support or review.

## Verification

Run:

```bash
uv run med-school-discover-aacom-do-profiles
uv run med-school-extract-aacom-do-stats
uv run med-school-apply-aacom-do-stats
uv run med-school-validate
uv run pytest
cd frontend && npm run build
cd frontend && npm run smoke
git diff --check
```

## Definition Of Done

- DO profile candidates are discovered without Google or AI snippets.
- AACOM extraction works on at least one fixture and multiple live-style HTML samples.
- Accepted AACOM rows are source-linked and DO-only.
- Coverage report shows matched, unmatched, extracted, review, and conflict counts.
- Site/source labels avoid claiming AACOM independently verified the values.
