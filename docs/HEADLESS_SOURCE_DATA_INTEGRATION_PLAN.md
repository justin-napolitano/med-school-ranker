# Headless Execution Plan: Phase 2A Source Data Integration

## Objective

Execute Phase 2A without human follow-up. This phase integrates the existing source-data drop into normalized CSVs, workbook tabs, static site data, and review reports while preserving source confidence and avoiding unsafe assumptions.

## Execution Mode

- Run non-interactively.
- Use existing files in `data/source_tables/`, `data/raw/aamc/msar_reports/`, and `outputs/source_diffs/`.
- Do not fetch new network data.
- Do not rerun downloader scripts unless the user explicitly asks.
- Do not add real applicant/private data.
- Do not remove or overwrite user-created source files.
- Keep raw/source tables separate from normalized outputs.
- Preserve the project decision excluding Puerto Rico from the active school universe.
- Stop and report only if a structural conflict prevents safe generation of normalized outputs.

## Source Artifact Policy

- Commit source integration code, parsed source CSVs, source-diff reports, normalized outputs, regenerated workbook/site outputs, and source registry updates when implementation is complete.
- Do not add raw binary PDFs/HTML snapshots to `med-school-ranker-upload.zip`.
- Do not commit raw binary source snapshots unless the implementation commit explicitly documents why they are needed for reproducibility and confirms there is no private data.
- If raw snapshots stay local-only, the integration command must be able to run from committed parsed CSV source tables.

## Idempotency Rules

- `uv run med-school-integrate-sources` must be safe to rerun.
- Regenerate normalized and generated outputs from source tables plus manual overrides.
- Never overwrite manual review notes, source match overrides, partner inputs, applicant profile values, or files in `data/manual/private`.
- If a generated file is rebuilt, write deterministic row ordering so diffs are reviewable.
- Missing values remain blank; do not backfill blanks with zero.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

Primary commands to preserve:

```bash
uv run med-school-build-all
uv run med-school-validate
uv run pytest
```

New command to add:

```bash
uv run med-school-integrate-sources
```

## Phase 2A Scope

### 1. Source Inventory Guard

Add a source integration module:

```text
src/med_school_ranker/source_integration.py
```

Add a wrapper:

```text
scripts/integrate_sources.py
```

Add path constants as needed in:

```text
src/med_school_ranker/paths.py
```

Required source inputs:

```text
data/source_tables/aamc_msar_tuition_school_master_patch_candidates.csv
data/source_tables/aamc_msar_tuition_school_master_join_candidates.csv
data/source_tables/aamc_msar_tuition_fees_insurance.csv
data/source_tables/aamc_msar_applications_accepted.csv
data/source_tables/aamc_msar_mcat_dates.csv
data/source_tables/aamc_msar_secondary_application.csv
data/source_tables/aamc_msar_interview_policies.csv
data/source_tables/aamc_msar_waitlist_procedures.csv
data/source_tables/aamc_msar_deposit_information.csv
data/source_tables/aamc_msar_premed_course_requirements.csv
data/source_tables/aamc_msar_community_college_coursework.csv
data/source_tables/aamc_msar_preview_policies.csv
data/source_tables/aamc_msar_daca_policies.csv
data/source_tables/cycletrack_lor_requirements.csv
data/source_tables/cycletrack_lor_links.csv
data/source_tables/all_comparable_mcat_gpa_sources.csv
data/source_tables/source_universe_additions.csv
data/source_tables/source_universe_aamc_msar_reports.csv
outputs/source_diffs/mcat_gpa_source_comparison.csv
outputs/source_diffs/mcat_gpa_conflicts.csv
```

If optional source files are missing, emit a warning in the source integration report rather than crashing. If required source files are missing, fail the integration command before writing partial normalized outputs.

### Shared Matching Policy

Implement one shared school-matching helper and use it for AAMC policy rows, tuition rows, CycleTrack rows, and GPA/MCAT candidates.

Rules:

- Match only against active `data/school_master.csv` rows.
- Prefer exact `school_id` where a source table already provides it.
- Otherwise normalize school names consistently: lowercase, ASCII fold, remove punctuation, collapse whitespace, and strip common corporate suffix noise only when it does not change identity.
- When source rows include state or degree type, require compatibility with `state_abbrev` and `degree_type`.
- Treat exact normalized name matches as safe.
- Treat fuzzy matches as safe only when the top score is at least 0.92 and the second-best score is at least 0.03 lower.
- Treat ties, low second-match gaps, state conflicts, degree conflicts, Puerto Rico rows, Canadian/province rows, and missing master rows as review items.
- Write all non-safe matches to `outputs/source_match_review.csv` and `data/manual/source_review_queue.csv`.

### 2. Add Normalized Schemas

Create or update:

```text
data/normalized/cost_and_debt.csv
data/normalized/admissions_policies.csv
data/normalized/letter_requirements.csv
data/manual/source_review_queue.csv
data/manual/source_match_overrides.csv
outputs/source_integration_report.csv
outputs/source_match_review.csv
outputs/admissions_stats_conflicts.csv
outputs/cost_and_debt_review.csv
outputs/admissions_stats_candidates.csv
outputs/cost_and_debt_candidates.csv
```

Do not put these in `data/manual/private`.

Exact schemas:

```text
data/manual/source_match_overrides.csv
override_id,source_table,source_row_number,source_school_name,source_state,source_degree_type,override_action,school_id,school_name,match_status,reviewed_by,reviewed_date,review_notes

data/manual/source_review_queue.csv
review_id,review_status,review_reason,source_table,source_row_number,source_school_name,source_state,source_degree_type,school_id,school_name,match_score,second_match_score,recommended_action,created_date,resolved_date,resolution_notes

data/normalized/cost_and_debt.csv
school_id,school_name,degree_type,tuition_year,academic_year,in_state_tuition_fees_insurance,out_state_tuition_fees_insurance,estimated_coa_in_state,estimated_coa_out_state,expected_scholarship,application_fee,secondary_fee,deposit_amount,average_grad_indebtedness,residency_assumption,debt_burden_score,attendance_cost_score,source_name,source_url,source_snapshot_path,source_publication_date,source_last_checked,data_confidence,source_table,source_row_number,match_score,match_label,notes

data/normalized/admissions_policies.csv
school_id,school_name,degree_type,policy_category,policy_field,policy_value,policy_value_type,source_name,source_url,source_snapshot_path,source_publication_date,source_last_checked,data_confidence,source_table,source_row_number,match_score,match_label,notes

data/normalized/letter_requirements.csv
school_id,school_name,degree_type,requirement_type,requirement_url,source_name,source_url,source_last_checked,data_confidence,source_table,source_row_number,match_score,match_label,notes

outputs/source_integration_report.csv
severity,category,item,count,message,next_action

outputs/source_match_review.csv
source_table,source_row_number,source_school_name,source_state,source_degree_type,best_school_id,best_school_name,best_match_score,second_school_id,second_school_name,second_match_score,match_label,review_reason,recommended_action

outputs/admissions_stats_candidates.csv
candidate_id,school_id,school_name,degree_type,source_key,source_name,source_url,value_url,source_row_number,source_school_name,metric_context,gpa,mcat,agreement_label,data_confidence,match_score,match_label,notes

outputs/admissions_stats_conflicts.csv
cluster_id,canonical_school_name,school_id,sources_present,source_count,agreement_label,gpa_values,gpa_range,gpa_spread,mcat_values,mcat_range,mcat_spread,metric_definition_note,recommended_action

outputs/cost_and_debt_candidates.csv
school_id,school_name,state_abbrev,in_state_tuition_fees_insurance,out_state_tuition_fees_insurance,estimated_coa_in_state,estimated_coa_out_state,tuition_source_url,tuition_source_name,aamc_source_row_number,aamc_school_name,match_score,match_label,second_match_score,safety_label,notes

outputs/cost_and_debt_review.csv
source_table,source_row_number,source_school_name,source_state,school_id,school_name,match_score,second_match_score,review_reason,recommended_action,notes
```

Allowed `source_match_overrides.override_action` values:

- `accept_match`
- `reject_match`
- `force_no_match`
- `ignore_source_row`

### 3. Cost and Debt Integration

Input:

```text
data/source_tables/aamc_msar_tuition_school_master_patch_candidates.csv
data/source_tables/aamc_msar_tuition_school_master_join_candidates.csv
data/source_tables/aamc_msar_tuition_fees_insurance.csv
```

Safe write rules:

- Write a normalized cost row only when `match_label` is `exact` or `high_confidence`.
- Require a valid `school_id` in `data/school_master.csv`.
- Re-check `data/source_tables/aamc_msar_tuition_school_master_join_candidates.csv`; a `high_confidence` row is safe only when the second-best match is at least 0.03 lower than the selected match.
- Require at least one nonblank, nonzero tuition/COA value.
- Only write U.S. MD rows from the AAMC tuition source.
- Preserve AAMC row number, match score, match label, source name, source URL, PDF file, and notes.
- Apply `data/manual/source_match_overrides.csv` before final safety classification.

Review queue rules:

- Send `review`, `no_match`, Puerto Rico, Canadian/province, all-zero, ambiguous, and DO-missing rows to `data/manual/source_review_queue.csv`.
- Add review reasons that are specific enough for a human to act on.

Expected current baseline:

- 156 AAMC tuition patch candidate rows before ambiguity re-audit.
- 151 safe AAMC tuition rows after second-match gap and zero-cost review.
- 2 ambiguous high-confidence tuition rows that must go to source review.
- 3 exact-match all-zero tuition rows that must go to source review.
- 3 additional active MD rows needing source/match review.
- 74 DO rows missing tuition source coverage.

### 4. Admissions Policy Integration

Inputs:

```text
data/source_tables/aamc_msar_applications_accepted.csv
data/source_tables/aamc_msar_mcat_dates.csv
data/source_tables/aamc_msar_secondary_application.csv
data/source_tables/aamc_msar_interview_policies.csv
data/source_tables/aamc_msar_waitlist_procedures.csv
data/source_tables/aamc_msar_deposit_information.csv
data/source_tables/aamc_msar_premed_course_requirements.csv
data/source_tables/aamc_msar_community_college_coursework.csv
data/source_tables/aamc_msar_preview_policies.csv
data/source_tables/aamc_msar_daca_policies.csv
```

Write policy rows keyed by `school_id` where the school match is exact or high-confidence. Preserve source text and source metadata.

Do not coerce policy text into boolean flags unless the parsed value is unambiguous. For example, OOS acceptance policy text should remain text in Phase 2A; derived OOS friendliness scoring belongs to a later formula pass.

### 5. Letter Requirement Integration

Inputs:

```text
data/source_tables/cycletrack_lor_requirements.csv
data/source_tables/cycletrack_lor_links.csv
```

Write `data/normalized/letter_requirements.csv`.

Rules:

- Preserve requirement URLs and source names.
- Match to `school_id` when high-confidence.
- Keep unmatched rows in source review queue.
- Do not scrape the linked requirement pages in Phase 2A.

### 6. GPA/MCAT Candidate Integration

Inputs:

```text
data/source_tables/all_comparable_mcat_gpa_sources.csv
outputs/source_diffs/mcat_gpa_source_comparison.csv
outputs/source_diffs/mcat_gpa_conflicts.csv
```

Write:

```text
outputs/admissions_stats_candidates.csv
outputs/admissions_stats_conflicts.csv
data/normalized/admissions_stats.csv
```

Rules:

- Preserve all comparable rows in candidate output with source key, source URL, metric context, GPA, MCAT, and notes.
- Map candidate rows to `school_id` when high-confidence name matching is possible.
- Treat CycleTrack values as approved context only when the source row is safely matched.
- Treat published third-party values as provisional.
- Create selected normalized rows for safely matched candidate values, including `close_agreement`, `single_source`, `minor_conflict`, and `major_conflict`.
- Keep conflict and review queue rows visible even when safely matched values are selected for scoring.
- Keep `data_confidence` and `data_quality_band` explicit so approved conflict/single-source values are not mistaken for official school data.
- Never mix accepted, matriculated, mean, median, and crowdsourced rows without encoding that distinction in `metric_population` and `metric_type`.

Default current expectation:

- Some GPA/MCAT rows will remain review-needed because they lack a safely matched source value.
- It is acceptable for the integration report to show that rankings should still be treated as low confidence.

### 7. Source Registry Update

Merge source additions into:

```text
data/sources.csv
```

Inputs:

```text
data/source_tables/source_universe_additions.csv
data/source_tables/source_universe_aamc_msar_reports.csv
```

Rules:

- Deduplicate by `source_name` and `url`.
- Preserve existing LCME, AOA, and AACOM rows.
- Add AAMC MSAR Advisor Reports, ProspectiveDoctor, Shemmassian, The Match Guy, CycleTrack Letters of Recommendation, and CycleTrack School Explorer.

### 8. School Master Projection

Do not make `school_master.csv` the source of truth for imported values. Instead:

- Keep imported values in normalized tables.
- Project selected, source-backed summary fields into generated rankings/site payloads.
- Only patch existing `school_master.csv` fields if the current ranking engine requires it, and document the projection source in `notes` or source URL fields.

If patching `school_master.csv` is necessary in Phase 2A:

- Patch only safe AAMC tuition rows and selected GPA/MCAT rows that meet policy.
- Do not patch unsafe or unmatched conflict rows.
- Preserve blanks for missing data.
- Keep `source_url` and domain-specific source URL fields populated.

### 9. Ranking Integration

Update ranking generation conservatively:

- Use applicant MCAT/GPA fit formulas only when applicant profile MCAT/GPA values are present.
- If applicant stats are blank, leave `admissions_mcat_fit_score` and `admissions_gpa_fit_score` blank.
- Use normalized cost data for generated cost fields only when the data is present and source-backed.
- Keep default cost/debt influence low.
- Add coverage/explanation fields showing stats source confidence and cost source confidence.

Do not treat missing GPA, MCAT, tuition, or COA as zero.

### 10. Workbook Updates

Add workbook tabs:

```text
Cost and Debt
Admissions Policies
Letter Requirements
Source Review Queue
Source Integration Report
Admissions Stats Candidates
Admissions Stats Conflicts
Cost and Debt Review
```

Keep existing tabs.

### 11. Site Updates

Update `src/med_school_ranker/site.py` to include the new normalized and generated outputs in the site payload.

Add to Dashboard:

- admissions stats rows
- selected GPA/MCAT coverage
- GPA/MCAT conflict count
- cost rows
- cost coverage
- source review queue count

Add to Rankings:

- stats present filter
- cost present filter
- source confidence filter
- review-needed filter

Add to School Detail:

- GPA/MCAT values, source confidence, source URL
- tuition/COA values, source confidence, source URL
- admissions policy summary
- letter requirement URL
- review queue items for the school

Keep the site local/static and embedded-data compatible.

### 12. Validation Updates

Extend validation to cover:

- required columns in new normalized files
- value-bearing normalized rows require source metadata
- MCAT/GPA numeric ranges
- dollar field numeric ranges
- source review queue required columns
- source match override required columns
- source match overrides must reference existing `school_id` when `override_action=accept_match`
- no private paths copied into site or upload bundle
- Puerto Rico remains excluded from active school universe and site payload
- conflicting GPA/MCAT rows create warnings and explicit confidence labels when selected

### 13. Tests

Add tests for:

- source integration command creates required normalized outputs
- safe AAMC tuition candidates become cost rows
- review/no-match tuition rows become source review queue entries
- safely matched major GPA/MCAT conflicts become selected rows with conflict confidence labels
- close agreement GPA/MCAT rows become selected provisional rows
- source registry additions are deduped
- workbook includes new source tabs
- site payload includes new source metrics
- build-all still passes

## Build-All Integration

Update:

```bash
uv run med-school-build-all
```

It should run:

1. validation of base inputs
2. source integration
3. validation of normalized/generated source outputs
4. rankings
5. workbook
6. site
7. upload bundle

If source integration finds warnings, build may continue. If it finds missing required source files or invalid normalized values, build should fail.

## Required Verification

Run:

```bash
uv run med-school-integrate-sources
uv run med-school-build-all
uv run pytest
```

Verify:

- `data/normalized/cost_and_debt.csv` exists and contains safe AAMC tuition rows.
- `data/normalized/admissions_stats.csv` exists and contains only source-backed rows.
- `data/manual/source_review_queue.csv` exists and includes review-needed rows.
- `outputs/source_integration_report.csv` exists.
- `outputs/source_match_review.csv` exists and includes ambiguous or unsafe source matches.
- `outputs/admissions_stats_conflicts.csv` exists.
- `outputs/cost_and_debt_review.csv` exists.
- The ambiguous Arizona and Texas Tech AAMC tuition high-confidence matches are not imported as safe cost rows unless manually resolved.
- `outputs/site/index.html` includes source coverage metrics.
- `outputs/med_school_ranker.xlsx` includes the new source tabs.
- `med-school-ranker-upload.zip` includes new normalized/source review outputs but no private paths.
- Puerto Rico remains excluded from active school/site data.

## Do Not Do

- Do not download new data.
- Do not bypass source permissions.
- Do not infer GPA/MCAT for unsafe or unmatched conflict rows.
- Do not populate DO tuition from AAMC MD tuition data.
- Do not turn policy text into unsupported booleans.
- Do not add real applicant values.
- Do not remove untracked source files.
- Do not overwrite manual partner inputs.

## Definition of Done

Phase 2A is done when:

- Source integration is a repeatable command.
- Safe source rows are normalized.
- Unsafe or ambiguous rows are queued for review.
- Rankings, workbook, and site can display the new source-backed layers.
- Data confidence is visible.
- Tests pass.
- The repo has a clear implementation commit that does not accidentally include private data.
