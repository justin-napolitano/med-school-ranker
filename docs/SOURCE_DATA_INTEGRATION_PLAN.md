# Source Data Integration Executive Plan

## Objective

Turn the newly collected public source tables into source-traceable normalized data that the rankings, workbook, and static site can use without mixing raw extracts, third-party hints, human judgments, and calculated scores.

The immediate goal is to make GPA, MCAT, tuition, cost, and admissions-policy data visible and usable while preserving source confidence and review status.

## Current Source Drop

The repo currently has a source-data drop that is not yet integrated into the canonical model:

- `data/raw/aamc/msar_reports/`
- `data/source_tables/`
- `outputs/source_diffs/`
- `scripts/download_aamc_msar_reports.py`
- `scripts/extract_admissions_sources.py`
- `scripts/parse_aamc_msar_reports.py`
- `scripts/parse_aamc_tuition_pdf.py`

Observed source coverage:

- AAMC MSAR Advisor Reports: 19 links discovered, 17 verified PDFs, 17 downloaded PDFs, 2 non-PDF HTML responses.
- Parsed AAMC tables: 32 CSVs under `data/source_tables/`.
- AAMC tuition: 176 parsed rows, 156 school-master patch candidates before ambiguity and zero-cost re-audit, 151 safe rows after review, 2 ambiguous high-confidence rows, 3 exact-match all-zero rows, 3 additional active MD rows needing source/match review, and 74 DO rows still missing from AAMC tuition.
- GPA/MCAT source rows:
  - ProspectiveDoctor: 146 rows.
  - Shemmassian: 203 rows.
  - The Match Guy: 116 rows.
  - CycleTrack acceptance medians included in comparable rows.
- GPA/MCAT comparison clusters: 316 total, with 202 single-source, 60 major conflicts, 27 minor conflicts, and 27 close agreement.
- CycleTrack: 233 explorer school cards, 932 stats rows, 233 LOR requirement rows, 414 LOR link rows.

Current canonical model gap:

- `data/normalized/admissions_stats.csv` has 0 rows.
- `data/school_master.csv` has 0 populated values for median MCAT, median GPA, tuition, COA, tuition source URL, admissions source URL, and MCAT/GPA fit scores.
- `outputs/site/index.html` and `outputs/med_school_ranker.xlsx` still reflect the old canonical CSVs, not the new source tables.

Source artifact policy:

- Commit source integration code, parsed source CSVs, source-diff reports, normalized outputs, workbook/site outputs, and source registry updates when implementation is complete.
- Do not add raw binary PDFs/HTML snapshots to the upload bundle.
- Do not commit raw binary source snapshots unless the implementation commit explicitly documents why they are needed for reproducibility and confirms there is no private data.

## Current Decision

- Treat the new source tables as evidence, not as final canonical values.
- Keep raw/source tables separate from normalized tables.
- Use official/public AAMC tables for MD tuition and admissions-policy facts where the parse is reliable.
- Treat third-party GPA/MCAT values as provisional unless sources closely agree or a future official/public school source confirms them.
- Treat CycleTrack GPA/MCAT values as crowdsourced context, not official entering-class stats.
- Do not infer applicant-specific admissions fit until the applicant profile has MCAT/GPA values.
- Do not overwrite subjective partner scores or manual judgments during source integration.

## Non-Goals

- Do not fetch new web data in the headless integration pass.
- Do not scrape restricted, paid, login-gated, or permission-unclear data.
- Do not silently choose one conflicting GPA/MCAT source over another.
- Do not collapse MD and DO source policies into one rule.
- Do not populate DO tuition from MD-only AAMC tuition reports.
- Do not publish private applicant data.
- Do not make rankings appear fully reliable when source confidence is low.

## Target Outputs

Normalized source-of-truth files:

```text
data/normalized/admissions_stats.csv
data/normalized/cost_and_debt.csv
data/normalized/admissions_policies.csv
data/normalized/letter_requirements.csv
data/manual/source_review_queue.csv
data/manual/source_match_overrides.csv
```

Generated review outputs:

```text
outputs/source_integration_report.csv
outputs/source_match_review.csv
outputs/admissions_stats_conflicts.csv
outputs/cost_and_debt_review.csv
outputs/calculated_rankings.csv
outputs/med_school_ranker.xlsx
outputs/site/index.html
med-school-ranker-upload.zip
```

Optional but useful generated candidates:

```text
outputs/admissions_stats_candidates.csv
outputs/cost_and_debt_candidates.csv
```

## Data Contracts

### Exact Schemas

Use these headers unless a later plan explicitly changes them.

`data/manual/source_match_overrides.csv`:

```text
override_id,source_table,source_row_number,source_school_name,source_state,source_degree_type,override_action,school_id,school_name,match_status,reviewed_by,reviewed_date,review_notes
```

Allowed `override_action` values:

- `accept_match`
- `reject_match`
- `force_no_match`
- `ignore_source_row`

`data/manual/source_review_queue.csv`:

```text
review_id,review_status,review_reason,source_table,source_row_number,source_school_name,source_state,source_degree_type,school_id,school_name,match_score,second_match_score,recommended_action,created_date,resolved_date,resolution_notes
```

`data/normalized/cost_and_debt.csv`:

```text
school_id,school_name,degree_type,tuition_year,academic_year,in_state_tuition_fees_insurance,out_state_tuition_fees_insurance,estimated_coa_in_state,estimated_coa_out_state,expected_scholarship,application_fee,secondary_fee,deposit_amount,average_grad_indebtedness,residency_assumption,debt_burden_score,attendance_cost_score,source_name,source_url,source_snapshot_path,source_publication_date,source_last_checked,data_confidence,source_table,source_row_number,match_score,match_label,notes
```

`data/normalized/admissions_policies.csv`:

```text
school_id,school_name,degree_type,policy_category,policy_field,policy_value,policy_value_type,source_name,source_url,source_snapshot_path,source_publication_date,source_last_checked,data_confidence,source_table,source_row_number,match_score,match_label,notes
```

`data/normalized/letter_requirements.csv`:

```text
school_id,school_name,degree_type,requirement_type,requirement_url,source_name,source_url,source_last_checked,data_confidence,source_table,source_row_number,match_score,match_label,notes
```

`outputs/source_integration_report.csv`:

```text
severity,category,item,count,message,next_action
```

`outputs/source_match_review.csv`:

```text
source_table,source_row_number,source_school_name,source_state,source_degree_type,best_school_id,best_school_name,best_match_score,second_school_id,second_school_name,second_match_score,match_label,review_reason,recommended_action
```

`outputs/admissions_stats_candidates.csv`:

```text
candidate_id,school_id,school_name,degree_type,source_key,source_name,source_url,value_url,source_row_number,source_school_name,metric_context,gpa,mcat,agreement_label,data_confidence,match_score,match_label,notes
```

`outputs/admissions_stats_conflicts.csv`:

```text
cluster_id,canonical_school_name,school_id,sources_present,source_count,agreement_label,gpa_values,gpa_range,gpa_spread,mcat_values,mcat_range,mcat_spread,metric_definition_note,recommended_action
```

`outputs/cost_and_debt_candidates.csv`:

```text
school_id,school_name,state_abbrev,in_state_tuition_fees_insurance,out_state_tuition_fees_insurance,estimated_coa_in_state,estimated_coa_out_state,tuition_source_url,tuition_source_name,aamc_source_row_number,aamc_school_name,match_score,match_label,second_match_score,safety_label,notes
```

`outputs/cost_and_debt_review.csv`:

```text
source_table,source_row_number,source_school_name,source_state,school_id,school_name,match_score,second_match_score,review_reason,recommended_action,notes
```

### Admissions Stats

`data/normalized/admissions_stats.csv` remains the canonical GPA/MCAT layer.

Rules:

- One row can represent one school, one source, one population, and one metric family.
- `school_id` is required for any row used by rankings.
- `source_name`, `source_url`, `source_last_checked`, and `data_confidence` are required when any metric value is present.
- `metric_population` must distinguish accepted, matriculated, enrolled, applicant, crowdsourced_acceptance, or unknown.
- `metric_type` must distinguish mean, median, percentile, range, or source_average.
- Third-party rows should be retained with confidence labels. Conflicting values may drive fit scoring only when the source row is safely matched and the conflict/confidence label remains visible.

### Cost and Debt

Add `data/normalized/cost_and_debt.csv`.

Rules:

- Use AAMC tuition patch candidates only when match label is `exact`, or when match label is `high_confidence` and the second-best match is at least 0.03 lower than the selected match.
- Do not trust `aamc_msar_tuition_school_master_patch_candidates.csv` by itself; re-check `aamc_msar_tuition_school_master_join_candidates.csv` for second-match ambiguity before writing normalized rows.
- Include `tuition_year`, `academic_year`, source metadata, AAMC source row number, and match confidence.
- Leave DO tuition blank unless a DO-specific or school-specific source exists.
- Keep expected scholarship assumptions blank unless manually entered.
- Derived scores should be generated, not hand-entered, and should preserve missing values.

### Admissions Policies

Add `data/normalized/admissions_policies.csv` for AAMC application acceptance facts and other policy facts.

Rules:

- Preserve policy text where parsed.
- Do not convert policy text to boolean unless the value is unambiguous.
- Track OOS, Canadian, international, DACA, MCAT-date, secondary, interview, waitlist, deposit, and course-requirement source rows separately where appropriate.

### Source Review Queue

Add `data/manual/source_review_queue.csv`.

Rules:

- Every no-match, review match, conflicting GPA/MCAT cluster, zero-cost row, and missing DO tuition row should have a review queue entry.
- Queue entries should include `review_reason`, `source_table`, `source_row_number`, `school_id` when known, and `recommended_action`.
- The queue is a human review workflow, not a blocker for safe normalized rows.

### Source Match Overrides

Add `data/manual/source_match_overrides.csv`.

Rules:

- The file is manually maintained and must not be overwritten by source integration.
- The source integration command should apply override rows before fuzzy matching.
- Overrides must be idempotent and auditable with `reviewed_by`, `reviewed_date`, and `review_notes`.
- A blank override file with headers is valid.
- If an override points to a missing `school_id`, validation should report an error.

### Shared School Matching

Every source integration path should use one shared school-matching helper.

Rules:

- Match only against active `data/school_master.csv` rows.
- Prefer exact `school_id` where source tables already provide it.
- Otherwise normalize school names consistently: lowercase, ASCII fold, remove punctuation, collapse whitespace, and strip common corporate suffix noise only when it does not change identity.
- When source rows include state or degree type, require compatibility with `state_abbrev` and `degree_type`.
- Treat exact normalized name matches as safe.
- Treat fuzzy matches as safe only when the top score is at least 0.92 and the second-best score is at least 0.03 lower.
- Treat ties, low second-match gaps, state conflicts, degree conflicts, Puerto Rico rows, Canadian/province rows, and missing master rows as review items.
- Write all non-safe matches to `outputs/source_match_review.csv` and `data/manual/source_review_queue.csv`.

## Integration Policy

### GPA/MCAT Selection Policy

Headless selection may populate normalized rows as follows after the user-approved "approve all safely matched candidates" policy:

- Safely matched candidate rows are eligible for canonical `admissions_stats.csv`.
- Published third-party sources are averaged by school/cluster and labeled with `data_confidence`.
- `single_source`, `minor_conflict`, and `major_conflict` values can be selected for scoring, but the conflict table and confidence label remain visible.
- `cycletrack_acceptance_median` can be selected only from safely matched source rows and should remain labeled as CycleTrack/crowdsourced context.
- Unsafe matches, no-match rows, low confidence matches, Puerto Rico rows, and incompatible degree/state rows remain review-only.

The rankings engine should prefer fit-driving values in this order when present:

1. Official school or official report stats.
2. Public school profile stats.
3. Approved safely matched third-party candidate averages.
4. Approved safely matched CycleTrack context values.

Default profile behavior: allow display of provisional values, but do not overstate confidence.

### Tuition Selection Policy

Headless selection may populate `cost_and_debt.csv` from AAMC tuition patch candidates when:

- `match_label` is `exact` or `high_confidence`.
- `school_id` exists in `data/school_master.csv`.
- tuition and/or COA values are nonblank and nonzero.
- the source row is a U.S. MD row.

Rows marked `review`, `no_match`, Canadian/province rows, Puerto Rico rows, all-zero rows, and DO schools should go to `source_review_queue.csv`.

### Scoring Policy

Implement formulas, but keep missing values blank.

- MCAT/GPA fit scores require applicant MCAT/GPA values.
- Cost/debt scores can be calculated from normalized cost data, but should remain low-weight in default rankings.
- Scores generated from provisional low-confidence stats must carry source confidence into ranking explanations and data quality warnings.
- Do not convert missing data to 0.

## Implementation Phases

### Phase 2A: Source Integration Baseline

- Add normalized schemas for cost/debt, admissions policies, and source review queue.
- Add source integration command.
- Read existing `data/source_tables/*.csv`.
- Populate safe normalized cost rows from AAMC patch candidates.
- Populate admissions stats candidate rows and conflict reports.
- Update source registry from source universe additions.
- Generate source integration report.
- Update workbook and site so the new layers are visible.
- Keep rankings conservative if applicant stats are missing.

### Phase 2B: Scoring and Explainability

- Add applicant-specific MCAT/GPA fit formulas.
- Add cost and debt scoring formulas.
- Add ranking explanation fields.
- Add site filters for stats present, cost present, source confidence, and review needed.

### Phase 2C: Review Resolution

- Work through source review queue.
- Add manual overrides for confirmed school matches or source selections.
- Add DO tuition import workflow.
- Promote reviewed source rows to higher confidence.

## Validation Rules

- Required source tables must exist before source integration runs.
- All generated normalized rows require stable `school_id`.
- MCAT must be blank or between 472 and 528.
- GPA must be blank or between 0 and 4.0.
- Dollar fields must be blank or numeric and nonnegative.
- Tuition rows require `tuition_year` or `academic_year`.
- Any value-bearing normalized row requires source metadata.
- Major GPA/MCAT conflicts create warnings and review queue entries.
- Unmatched source rows create warnings and review queue entries.
- Puerto Rico remains excluded from the active school universe unless the project decision changes.

## Workbook and Site Requirements

Workbook additions:

- `Cost and Debt`
- `Admissions Policies`
- `Letter Requirements`
- `Source Review Queue`
- `Source Integration Report`
- `Admissions Stats Candidates`
- `Admissions Stats Conflicts`
- `Cost and Debt Review`

Site additions:

- Show MCAT/GPA values, confidence, and source status in School Detail.
- Show cost/COA values and source status in School Detail.
- Add dashboard metrics for stats coverage, cost coverage, conflicts, and review queue size.
- Add Rankings filters for stats present, cost present, source confidence, and review needed.
- Preserve local-only behavior and embedded JSON for `file://` review.

## Required Commands

The headless implementation should add or preserve:

```bash
uv run med-school-integrate-sources
uv run med-school-build-all
uv run med-school-build-site
uv run med-school-validate
uv run pytest
```

`uv run med-school-build-all` should run validation, source integration, rankings, workbook, site, and bundle once the integration command exists.

## Definition of Done

Source integration is usable when:

- Safe AAMC tuition rows appear in `data/normalized/cost_and_debt.csv`.
- GPA/MCAT candidate/source rows and conflicts are visible without hiding uncertainty.
- `data/normalized/admissions_stats.csv` contains only values with source metadata and confidence labels.
- Review-needed rows are captured in `data/manual/source_review_queue.csv`.
- Workbook and site show the new layers.
- Rankings do not treat missing or low-confidence source data as zero.
- `uv run med-school-build-all` and `uv run pytest` pass.
