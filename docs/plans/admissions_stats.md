# Admissions Stats Plan

## Objective

Seed GPA and MCAT data as a separate admissions statistics layer so competitiveness calculations are traceable and do not mix incompatible metrics.

## Scope

This plan covers MCAT, overall GPA, science GPA, accepted versus matriculated populations, mean versus median values, percentile ranges, and source confidence.

## Inputs

- User-provided MSAR exports or manual entries where permitted.
- Public school profile pages, including school-published previous accepted or entering class profiles when accessible and permitted.
- AACOM Choose DO Explorer or exported/manual DO profile data where permitted.
- Public aggregate reports only for context, not per-school substitution.
- Current public third-party source tables in `data/source_tables/`, including ProspectiveDoctor, Shemmassian, The Match Guy, and CycleTrack, as provisional evidence only.

## Outputs

- `data/normalized/admissions_stats.csv`
- Derived fields in generated `School Master` and `Calculated Rankings`.
- Data quality warnings for missing or incompatible stats.

## Schema

Recommended fields:

- `school_id`
- `school_name`
- `degree_type`
- `stats_cohort_year`
- `metric_population`
- `metric_type`
- `mcat_median_accepted`
- `mcat_median_matriculated`
- `mcat_mean_enrolled`
- `mcat_10th_percentile`
- `mcat_25th_percentile`
- `mcat_75th_percentile`
- `mcat_90th_percentile`
- `overall_gpa_median_accepted`
- `overall_gpa_median_matriculated`
- `overall_gpa_mean_enrolled`
- `science_gpa_mean_enrolled`
- source metadata fields

## Source Policy

- Do not scrape or bypass restricted MSAR access.
- User-provided MSAR values may be imported if the user has rights to use them.
- Public school websites are acceptable when the page clearly states population, year, and metric type.
- Public scraping is allowed only for non-login, publicly accessible pages where access is permitted; adapters must store source URL, fetch date, and extraction confidence.
- When a school page is public but inconsistent or hard to parse, the system should generate an import/review template rather than guess.
- Third-party values remain provisional unless independently verified, but safely matched candidates are approved for current scoring.
- Third-party close-agreement values may be displayed as provisional values with confidence labels.
- Third-party single-source values may be selected as low-confidence provisional values with warnings.
- Third-party minor or major conflicts must create review queue rows and confidence labels when selected for fit scoring.
- CycleTrack GPA/MCAT values are crowdsourced context, not official entering-class averages, and may be selected only when safely matched.
- Accepted, matriculated, mean, median, and percentile values must remain separate.

## Current Source Drop

Current source tables contain useful evidence but are not yet integrated into this normalized layer.

- ProspectiveDoctor: 146 GPA/MCAT rows.
- Shemmassian: 203 GPA/MCAT rows.
- The Match Guy: 116 GPA/MCAT rows.
- Comparable GPA/MCAT rows: 676.
- Comparison clusters: 316.
- Agreement labels: 202 single-source, 60 major conflict, 27 minor conflict, 27 close agreement.

Phase 2A generates candidate rows and conflict reports; current policy allows safely matched candidate values to affect ranking while preserving confidence labels.

## Implementation Steps

1. Add `admissions_stats.csv` template.
2. Add a source-discovery/import queue for public school admissions profile pages.
3. Add source adapters for parseable public pages.
4. Add importer for manual/user-provided stats CSV.
5. Add matching logic from `school_name` to stable `school_id`.
6. Add derived MCAT/GPA fit scoring formulas.
7. Add workbook columns showing which stats source drove the fit score.
8. Add `outputs/admissions_stats_candidates.csv` and `outputs/admissions_stats_conflicts.csv`.
9. Add source confidence labels to ranking, workbook, and site outputs.

## Validation Rules

- MCAT total must be blank or between 472 and 528.
- GPA must be blank or between 0 and 4.0 unless explicitly documented.
- `metric_population` must be accepted, matriculated, enrolled, applicant, or unknown.
- `metric_type` must identify mean, median, percentile, or range.
- Stats require `stats_cohort_year` and source metadata.

## Open Questions

- Which metric should be canonical for fit scoring: accepted median by default, then matriculated median, then enrolled mean, or fully configurable by profile?
- Should MD and DO use different default fit formulas?
- Which public school profile pages are reliable enough for automated extraction versus manual review?

## Definition of Done

- GPA/MCAT values are seeded in a separate table.
- No GPA/MCAT value enters ranking without source and metric metadata.
- Fit scores can be regenerated and explained.
- Data quality report identifies schools missing stats.
