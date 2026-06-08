# 04 Review Queue And Conflict Resolution

## Review Outputs

Write:

```text
outputs/official_mcat_gpa_review_queue.csv
outputs/official_mcat_gpa_conflicts.csv
outputs/official_mcat_gpa_coverage.csv
```

`outputs/official_mcat_gpa_review_queue.csv` schema:

```text
review_id,school_id,school_name,degree_type,candidate_url,review_reason,recommended_action,official_domain_label,source_title,metric_population,metric_type,mcat_value,gpa_value,stats_cohort_year,evidence_text,last_checked
```

`outputs/official_mcat_gpa_conflicts.csv` schema:

```text
conflict_id,school_id,school_name,degree_type,official_source_count,official_urls,mcat_values,mcat_spread,gpa_values,gpa_spread,cohort_years,metric_populations,metric_types,recommended_action
```

`outputs/official_mcat_gpa_coverage.csv` schema:

```text
school_id,school_name,degree_type,state_abbrev,coverage_status,selected_source_type,selected_source_url,official_candidate_count,official_extracted_count,review_count,has_mcat,has_gpa,notes
```

## Review Reasons

Use explicit review reasons:

- `no_candidate_source`
- `candidate_nonofficial`
- `ambiguous_official_domain`
- `fetch_failed`
- `pdf_parser_missing`
- `no_stats_found`
- `minimum_requirement_only`
- `missing_cohort_year`
- `unclear_population`
- `official_value_conflict`
- `third_party_value_conflict`
- `school_identity_ambiguous`

## Conflict Rules

Do not average official and third-party values.

Official values beat third-party provisional values when:

- the source is accepted as official,
- the metric is not a minimum requirement,
- the value ranges are valid,
- population and metric type are clear enough for the score policy.

If two official sources conflict:

- Prefer the most recent cohort year.
- Prefer matriculated/enrolled/entering-class values over accepted/admitted values for attendance realism.
- Prefer median over mean only if the scoring policy asks for median; otherwise preserve both.
- If the policy cannot resolve it deterministically, write conflict review and keep the previous selected value.
