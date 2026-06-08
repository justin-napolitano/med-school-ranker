# 03 Extraction And Normalization

## Extraction Strategy

Use deterministic extraction first. LLM extraction can be added later only as a review assistant and must still cite fetched source text.

Supported content:

- HTML text from public pages.
- PDF text from public PDFs, if a PDF text dependency is added.
- CSV/manual imported candidate rows.

Recommended dependencies:

- `beautifulsoup4` for HTML cleanup.
- `pypdf` for PDF text extraction.

If dependencies are not added in the first pass, implement HTML extraction and queue PDFs with `extraction_status=needs_pdf_parser`.

## Extracted Values Table

Write:

```text
data/source_tables/official_mcat_gpa_extracted_values.csv
```

Schema:

```text
extraction_id,candidate_id,school_id,school_name,degree_type,source_url,final_url,source_title,source_type,stats_cohort_year,class_label,metric_population,metric_type,mcat_value,gpa_value,science_gpa_value,mcat_context,gpa_context,evidence_text,extraction_confidence,extraction_status,last_checked,notes
```

Allowed `metric_population` values:

- `matriculated`
- `enrolled`
- `accepted`
- `admitted`
- `entering_class`
- `applicant`
- `interviewed`
- `unknown`

Allowed `metric_type` values:

- `median`
- `mean`
- `average`
- `percentile`
- `range`
- `minimum_requirement`
- `unknown`

Rows with `minimum_requirement` must never be used as class-profile stats.

## Pattern Rules

Accept MCAT values only when:

- The number is between 472 and 528.
- Nearby text references class stats, matriculants, enrolled students, accepted students, entering class, admitted class, or class profile.
- Nearby text does not primarily reference minimum requirements, oldest/latest MCAT date, or application screening requirements.

Accept GPA values only when:

- The number is between 0 and 4.0.
- Nearby text references class stats, matriculants, enrolled students, accepted students, entering class, admitted class, or class profile.
- The value is not a minimum requirement unless explicitly stored as `minimum_requirement`.

## Normalized Admissions Stats

Append official rows to:

```text
data/normalized/admissions_stats.csv
```

Required official-row metadata:

- `school_id`
- `school_name`
- `degree_type`
- `stats_cohort_year` when discoverable
- `metric_population`
- `metric_type`
- one or more MCAT/GPA values
- `source_name`
- `source_url`
- `source_publication_date` when discoverable
- `source_last_checked`
- `data_confidence`
- `notes`

Official confidence labels:

- `official_public_source_high_confidence`
- `official_public_source_needs_year_review`
- `official_public_source_needs_population_review`
- `official_public_source_conflict_review`

Only `official_public_source_high_confidence` can become the selected score-driving row without review.
