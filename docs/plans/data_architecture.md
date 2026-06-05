# Data Architecture Plan

## Objective

Define the project data layers so the workbook remains an output, not the only source of truth.

## Scope

This plan covers raw source files, normalized CSVs, manual research inputs, generated outputs, schema conventions, and provenance requirements.

## Inputs

- Current `data/*.csv` seed files.
- Current generated `outputs/*.csv` and `outputs/*.xlsx`.
- Future source snapshots from public source adapters.
- Future manual research CSVs.

## Outputs

- Stable folder structure.
- Data layer naming conventions.
- Source provenance fields used across all normalized data.
- Documented rule for when data belongs in raw, normalized, manual, or generated outputs.

## Proposed Structure

```text
data/
  raw/
    lcme/
    aoa_coca/
    aamc_public/
    aacom_public/
  normalized/
    school_universe.csv
    admissions_stats.csv
    cost_and_debt.csv
    residency_match.csv
    curriculum.csv
    hidden_curriculum.csv
  manual/
    private/
    personal_fit_scores.csv
    applicant_profiles.local.csv
    manual_overrides.csv
    research_notes.csv
  school_master.csv
  user_preferences.csv
  scenario_weights.csv
outputs/
  calculated_rankings.csv
  med_school_ranker.xlsx
  data_quality_report.csv
```

## Source Policy

- Raw snapshots should preserve what was fetched or manually exported.
- Normalized rows must include source fields.
- Manual rows must include who entered the value, when it was reviewed, and confidence.
- Private applicant-specific rows live under ignored local paths by default.
- Generated files should be reproducible and can be overwritten by build commands.

## Required Provenance Fields

- `source_name`
- `source_url`
- `source_snapshot_path`
- `source_publication_date`
- `source_last_checked`
- `data_confidence`
- `notes`

## Implementation Steps

1. Add `data/raw`, `data/normalized`, and `data/manual` directories.
2. Add `data/manual/private` as ignored local storage for real applicant profiles.
3. Move current school universe toward `data/normalized/school_universe.csv`.
4. Keep current `data/school_master.csv` as the workbook-facing aggregate until the generator is refactored.
5. Add schema metadata for each normalized file.
6. Update the build pipeline to generate `school_master.csv` from normalized and manual layers.

## Validation Rules

- No normalized row without a `school_id`.
- No normalized row without source metadata unless it is explicitly marked as manual.
- No generated file should be treated as an input source of truth.
- `school_id` must be stable across rebuilds.
- Real applicant profile files under private paths must not be committed.

## Open Questions

- Should raw snapshots be committed, or should large snapshots be ignored and documented?
- Should schema definitions live in code, YAML, or docs?
- How much manual research should be in CSV versus Markdown notes?

## Definition of Done

- Data folders exist and are documented.
- Every data domain has a clear source-of-truth file.
- The build pipeline can regenerate workbook-facing CSVs from normalized and manual layers.
- Data quality checks report missing provenance.
