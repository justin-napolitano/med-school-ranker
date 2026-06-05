# Headless Execution Plan: Scoring Transparency and Rollup

## Objective

Implement scoring explainability and generated rollup-table improvements in small, auditable slices.

This plan is for a Codex headless worker. It should not change the admissions strategy, scrape new sources, or perform a broad data-model migration in the first pass.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

## Required Context

Read these first:

- `docs/HEADLESS_WORKER_RUNBOOK.md`
- `docs/SCORING_TRANSPARENCY_EXEC_PLAN.md`
- `docs/scoring_transparency/01_score_model_contract.md`
- `docs/scoring_transparency/02_score_contributions_output.md`
- `docs/scoring_transparency/05_validation_privacy_and_qa.md`

Read these only as implementation context:

- `docs/HEADLESS_SCORING_EXECUTION_PLAN.md`
- `docs/plans/scoring_engine.md`
- `src/med_school_ranker/rankings.py`
- `src/med_school_ranker/site.py`
- `src/med_school_ranker/workbook.py`
- `src/med_school_ranker/bundle.py`

## Execution Rules

- Run non-interactively.
- Do not fetch network data.
- Do not scrape school pages.
- Do not implement predictive admissions probability.
- Do not commit private applicant data or private-derived outputs.
- Do not remove existing output columns unless the plan explicitly says the migration is complete.
- Do not treat missing values as zero.
- Do not make `school_master.csv` the canonical home for imported facts.
- Prefer additive outputs first.

## Phase Order

### Phase 0: Preflight and Contract

Tasks:

- Confirm clean or understandable git state.
- Inspect current ranking headers and scorer formulas.
- Add or refine field definitions for rank/explainability terminology if needed.
- Decide exact output names before editing code:
  - `outputs/score_contributions.csv`
  - `outputs/private/score_contributions.private.csv`
  - `outputs/score_explanations.csv` if separate explanations are clearer than adding fields to rankings.
- Confirm private path exclusion in upload bundle remains intact.

Verification:

```bash
uv run pytest
uv run med-school-validate
```

### Phase 1: Long-Form Score Contributions

Tasks:

- Add a generated long-form contribution output.
- One row per applicant profile, school, score group, scenario, and component where appropriate.
- Include the columns specified in `02_score_contributions_output.md`.
- Public build uses public/template profiles only.
- Private build writes contribution rows only under `outputs/private/`.
- Add tests proving contribution math and private-output placement.

Verification:

```bash
uv run med-school-build-rankings
uv run med-school-build-private-rankings
uv run pytest
```

Expected result:

- Public contribution CSV exists and contains no private profile rows.
- Private contribution CSV exists only locally under ignored `outputs/private/` when private command is run.
- Weighted contribution sums are explainable and stable.

### Phase 2: Rank Confidence and Explanation Fields

Tasks:

- Add rank confidence labels to ranking output.
- Add deterministic explanation fields from contribution rows:
  - `rank_summary`
  - `top_positive_contributors`
  - `top_negative_contributors`
  - `missing_or_low_confidence_drivers`
- Keep copy concise and formula-driven.
- Add tests for high coverage, partial coverage, missing MCAT/GPA, hard-no excluded rows, and tie behavior.

Verification:

```bash
uv run med-school-build-rankings
uv run pytest
```

### Phase 3: Site and Workbook Audit Views

Tasks:

- Add "Why This Rank?" to the local review site detail panel.
- Add contribution/audit table data to the site payload.
- Add workbook tab or section for scoring audit.
- Show exact rank, rank band, confidence, and top contributors.
- Keep private contribution payloads out of public site builds.

Verification:

```bash
uv run med-school-build-site
uv run med-school-build-workbook
uv run pytest
```

If browser tooling is available, smoke-test the local site:

```bash
curl -I http://localhost:8000
```

### Phase 4: Generated Rollup Scaffold

Tasks:

- Add a generated `outputs/school_decision_rollup.csv` only after contributions and explanations are stable.
- Treat it as a wide review surface assembled from normalized/manual data.
- Keep existing `data/school_master.csv` and `outputs/calculated_rankings.csv` behavior stable.
- Add tests that the rollup is generated from inputs and is not required as source input.

Verification:

```bash
uv run med-school-build-all
uv run pytest
```

### Phase 5: Incremental Normalization

Tasks:

- Move one domain at a time into normalized/manual layers only when the rollup can preserve downstream output.
- Start with low-risk manual/judgment domains before touching identity or admissions stats:
  - city context
  - curriculum
  - hidden curriculum
  - match outcomes
  - partner fit
- Add source/provenance columns before moving fields.

Verification:

```bash
uv run med-school-build-all
uv run med-school-validate
uv run pytest
```

## Required Final Checks

Before committing:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git status --short --ignored data/manual/private data/private outputs/private
```

Inspect the upload bundle:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
```

## Stop Conditions

Stop and report instead of guessing if:

- Existing scoring tests fail before changes and the failure is unrelated.
- Private files would need to be committed to verify behavior.
- A required migration would break existing workbook/site outputs in the same pass.
- Contribution math cannot be reconciled with current weighted-score behavior.
- A normalized-table migration requires a policy decision about source-of-truth ownership.

## Handoff Format

Report:

- files changed;
- generated outputs changed;
- tests run;
- private paths checked;
- remaining risks;
- next recommended phase.
