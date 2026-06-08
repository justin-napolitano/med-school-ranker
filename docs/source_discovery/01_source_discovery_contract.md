# 01 Source Discovery Contract

## Purpose

Create a deterministic candidate-source manifest for official school-published MCAT/GPA values.

The manifest must make source discovery reviewable even when automated search is incomplete or unavailable.

## Candidate Table

Write:

```text
data/source_tables/official_mcat_gpa_source_candidates.csv
```

Schema:

```text
candidate_id,school_id,school_name,degree_type,state_abbrev,school_website_url,current_admissions_source_url,candidate_url,final_url,candidate_title,candidate_host,discovery_method,search_query,source_type_hint,official_domain_score,official_domain_label,http_status,content_type,last_checked,fetch_error,review_status,review_notes
```

Allowed `discovery_method` values:

- `school_master_website`
- `school_master_admissions_source_url`
- `manual_queue`
- `search_provider`
- `site_search`
- `sitemap`

Allowed `source_type_hint` values:

- `class_profile`
- `annual_report`
- `fact_book`
- `admissions_statistics`
- `student_profile`
- `pdf_report`
- `school_homepage`
- `unknown`

Allowed `review_status` values:

- `candidate`
- `accepted_for_fetch`
- `needs_review`
- `rejected_nonofficial`
- `rejected_irrelevant`
- `fetch_failed`

## Manual Queue

Expand:

```text
data/manual/admissions_source_queue.csv
```

Required schema:

```text
school_id,school_name,degree_type,candidate_source_url,source_status,extraction_status,review_status,last_checked,source_type_hint,official_domain_label,accepted_source_url,accepted_source_title,reviewed_by,reviewed_date,notes
```

Migration rule:

- If the file already exists with fewer columns, preserve all rows and append missing columns with blanks.
- Never rewrite reviewer notes except by deterministic column migration.

## Search Query Generation

Generate these query strings for each school, but do not rely on search being available:

```text
"{school_name}" "class profile" MCAT GPA
"{school_name}" "entering class" MCAT GPA
"{school_name}" "matriculants" MCAT GPA
"{school_name}" "annual report" MCAT GPA
"{school_name}" "facts and figures" medical school MCAT GPA
site:{school_host} MCAT GPA "class profile"
```

Search results are candidate URLs only. They must pass official source rules before fetching and extraction.

## Deterministic Ordering

Sort candidate output by:

1. `school_id`
2. official-domain label rank
3. source-type hint rank
4. candidate URL
