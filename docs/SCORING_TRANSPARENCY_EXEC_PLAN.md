# Scoring Transparency and Rollup Executive Plan

## Objective

Make every ranking easier to understand, audit, and explain without turning the scorer into a black box or destabilizing the current working pipeline.

This plan improves the scoring matrix in two directions:

- Explainability: show raw inputs, normalized scores, weights, weighted contributions, sources, confidence, missing data, and plain-English rank reasons.
- Data shape: move toward normalized domain tables with one generated rollup table used by workbook, site, and ranking outputs.

The goal is not to change the applicant strategy yet. The goal is to make the current deterministic score more transparent and easier to trust before changing its weighting or scope.

## Current Problem

The current rank is technically explainable in code, but not easy enough for a human reviewer.

Pain points:

- `overall_rank` sounds more authoritative than it is.
- A school can have a numeric rank without an obvious "why this rank?" trail.
- Component columns are wide and hard to inspect in `school_master` or `calculated_rankings`.
- Missing data and low confidence are visible, but not yet summarized as rank confidence.
- The master/rollup surface is getting too wide for long-term maintenance.
- School facts, normalized source data, scoring projections, and generated output are not separated clearly enough for future work.

## Non-Goals

- Do not implement predictive school-specific admissions probability.
- Do not migrate the full data model in one pass.
- Do not make `school_master.csv` the canonical home for MCAT, GPA, cost, curriculum, match, or personal-fit facts.
- Do not commit private applicant data or private-derived outputs.
- Do not hide missing data by filling it with zero.
- Do not change the current admission strategy or weights unless the user explicitly asks.

## Design Principles

- Every rank must be decomposable into weighted component contributions.
- Every component must identify whether it came from a source-backed fact, manual input, derived formula, or missing value.
- Wide rollups are generated outputs, not source-of-truth tables.
- Normalized tables should remain narrow, domain-specific, and source-traceable.
- Exact rank should be paired with rank bands and confidence labels.
- Backward compatibility matters: keep existing output columns until downstream workbook/site usage is migrated.

## Target User Experience

For any ranked school, the reviewer should be able to answer:

- What is the current decision rank?
- What rank band is it in?
- Which components helped most?
- Which components hurt most?
- Which raw inputs produced the MCAT/GPA/cost/location scores?
- How much did each component contribute to the final score?
- Which source or manual input supports each component?
- Is this rank high confidence, partial, provisional, or low coverage?
- Would the rank materially change under Admissions Realist, Financial, Lifestyle, or Prestige lenses?

## Target Data Shape

Future generated layers should look like this:

```text
data/
  normalized/
    school_identity.csv
    admissions_stats.csv
    cost_and_debt.csv
    admissions_policies.csv
    curriculum.csv
    match_outcomes.csv
    city_context.csv
    hidden_curriculum.csv
  manual/
    partner_inputs.csv
    source_review_queue.csv
    private/
      applicant_profiles.local.csv
outputs/
  school_decision_rollup.csv
  calculated_rankings.csv
  score_contributions.csv
  score_explanations.csv
  private/
    calculated_rankings.private.csv
    score_contributions.private.csv
```

`school_decision_rollup.csv` is the single wide review table. It is generated from normalized/manual inputs and can feed the workbook and site. It is not edited by hand.

## Phase Sequence

### Phase 0: Contract and Guardrails

- Document scoring terminology.
- Preserve `overall_rank` for compatibility, but expose a clearer label such as `decision_rank`.
- Define component contribution columns and long-form contribution output.
- Define rank confidence labels.
- Define private/public output rules before generating any private explainability files.

### Phase 1: Score Contributions Output

- Generate `outputs/score_contributions.csv`.
- Generate `outputs/private/score_contributions.private.csv` only for private runs.
- Each row represents one component for one profile-school pair.
- Include raw input, normalized score, weight, contribution, source, confidence, missing-data status, and formula note.

### Phase 2: Rank Explanations

- Generate concise explanation fields:
  - `rank_summary`
  - `top_positive_contributors`
  - `top_negative_contributors`
  - `missing_or_low_confidence_drivers`
  - `rank_confidence`
- Keep explanations deterministic and source-aware.

### Phase 3: Generated Rollup Table

- Introduce `outputs/school_decision_rollup.csv` as the wide generated review surface.
- Keep normalized tables as source-of-truth inputs.
- Keep `school_master.csv` stable while downstream code transitions.
- Do not remove existing workbook/site columns until replacements are verified.

### Phase 4: Site and Workbook Audit Views

- Add a "Why This Rank?" detail panel.
- Add a scoring audit table in the workbook.
- Show raw input, score, weight, contribution, source, and confidence.
- Show exact rank and rank band together.

### Phase 5: Deeper Normalization

- Move additional domain fields out of master-style wide surfaces only after contribution outputs and audit views work.
- Normalize curriculum, match outcomes, hidden curriculum, city context, and personal-fit inputs incrementally.
- Keep migrations reversible and covered by tests.

## Subplans

- [Score Model Contract](scoring_transparency/01_score_model_contract.md)
- [Score Contributions Output](scoring_transparency/02_score_contributions_output.md)
- [Rollup Tables and Normalization](scoring_transparency/03_rollup_tables_and_normalization.md)
- [Rank Explanation Views](scoring_transparency/04_rank_explanation_views.md)
- [Validation, Privacy, and QA](scoring_transparency/05_validation_privacy_and_qa.md)

## Headless Execution

Headless execution details live in [Headless Scoring Transparency Execution Plan](HEADLESS_SCORING_TRANSPARENCY_EXECUTION_PLAN.md).

Use this plan only after the current deterministic scoring implementation is stable and committed.

## Acceptance Criteria

- A reviewer can explain any rank from generated outputs without reading Python code.
- Component contributions sum transparently to score values, accounting for missing-data coverage.
- Private contribution outputs stay under ignored private paths.
- Public build artifacts contain no private profile IDs or private-derived ranks.
- `uv run pytest` passes.
- `uv run med-school-validate` reports no structural errors.
- Existing rank outputs remain backward compatible unless a migration is explicitly approved.
