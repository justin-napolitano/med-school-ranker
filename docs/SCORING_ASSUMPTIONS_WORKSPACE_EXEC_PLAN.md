# Scoring Assumptions Workspace Executive Plan

## Objective

Make the current score understandable enough that a non-technical reviewer can see what assumptions are in force, change those assumptions, and immediately understand why the school order changed.

This is an explainability and control slice. It should not change the meaning of `Your Rank` unless the user deliberately changes visible inputs or weights.

## Product Outcome

The applicant should be able to answer:

```text
What assumptions are driving this rank, what score did each assumption produce, and what happens if I change one of them?
```

The current Build My List score is deterministic, but it is too compressed. The new surface should expose:

- the applicant/profile assumptions currently in use;
- the component weights currently in use;
- how each component is scored;
- whether each component is included or missing;
- the weighted contribution each component makes;
- the resulting `Your Score`, `Your Rank`, and `Baseline Rank`.

## Current State

- The Astro frontend computes browser-local `Your Rank` and `Your Score` in `frontend/src/lib/live-scoring.ts`.
- Build My List already has MCAT, GPA, state, filters, exclusions, weight presets, sliders, cards, and local list actions.
- Cards show live factor bullets, but they do not expose a full contribution table.
- Methodology explains formulas, but it is not interactive and does not show the user's current assumptions in one place.
- Missing values are excluded from the denominator and shown as coverage warnings.
- The site is public and static. User-entered assumptions must remain browser-local.

## Product Contract

- Add an applicant-facing scoring workspace, tentatively `/scoring/` with nav label `Scoring`.
- The page uses the same browser-local state as Build My List.
- Changing assumptions on this page updates the same local state used by Build My List.
- The page must include an assumptions table before the school results.
- The page must include a school score breakdown table.
- The page must keep `Your Rank` distinct from `Baseline Rank`.
- The page must state that the score is a deterministic fit ranking, not admissions probability.
- The page must not commit private applicant values or write anything to a server.
- The page must not use data-confidence/source-confidence as a ranking control unless a later plan explicitly changes that.

## Non-Goals

- No predictive admissions model.
- No school-specific acceptance probability.
- No "likely admitted," "safe," "guaranteed," or "best school" language.
- No server, database, account system, or writeback.
- No scraping or new data ingestion.
- No new scoring components beyond current live-scoring components in the first slice.
- No hidden changes to default weights.
- No AI-generated rank explanations.

## Proposed UX

### Page 1: Scoring

The page should have three sections:

1. `Assumptions in use`
   - table rows for applicant MCAT, applicant GPA, home state, cost basis, degree filter, excluded states, excluded cities, ownership filter status, and active weight preset/custom weights;
   - every row has `Assumption`, `Current value`, `Used by`, `Can change?`, and `Notes`;
   - edit controls appear inline where safe.

2. `Weights and formulas`
   - table rows for MCAT fit, GPA fit, state/residency fit, cost fit, and baseline attendance context;
   - columns: `Component`, `Formula`, `Current weight`, `When missing`, `What a high score means`;
   - sliders/presets can remain visually compact, but the table must make the current weights readable.

3. `School score breakdown`
   - selectable school or default top-ranked school;
   - rows for each live scoring component;
   - columns: `Component`, `Applicant input`, `School value`, `Score`, `Weight`, `Weighted points`, `Included?`, `Reason`;
   - show denominator basis: `present components only`;
   - show `Your Score` as sum of weighted points.

### Secondary Table: Rank Movement

Add a compact table comparing current rank to baseline rank for top schools:

```text
School | Your Rank | Baseline Rank | Your Score | Coverage | Biggest driver | Missing pieces
```

This should be sortable or at least ordered by `Your Rank`.

## Terminology

Use these labels:

- `Your Rank`: rank computed in the browser from current local assumptions.
- `Your Score`: weighted 1-10 score from current local assumptions.
- `Baseline Rank`: generated pipeline rank from source-derived payload data.
- `Coverage`: how many configured components were available for the score.
- `Weighted points`: component score multiplied by normalized present-component weight.
- `Assumption`: a value chosen by the user or defaulted in the browser.

Avoid:

- `admit chance`;
- `probability`;
- `safety`;
- `prediction`;
- `best`;
- `model confidence` unless explicitly about data coverage.

## Execution Slices

1. Define scoring assumption contracts and labels.
2. Extend live-scoring outputs with display-ready contribution rows.
3. Add the Scoring page and route.
4. Add assumptions and weights tables.
5. Add school score breakdown and rank movement tables.
6. Add methodology and smoke coverage.
7. Run headless QA and critical review.

## Required Subplans

- [Scoring Terms And Contracts](site/scoring_assumptions/01_scoring_terms_and_contracts.md)
- [Assumptions Table UX](site/scoring_assumptions/02_assumptions_table_ux.md)
- [School Score Breakdown Table](site/scoring_assumptions/03_school_score_breakdown_table.md)
- [Scenario And Weight Experiments](site/scoring_assumptions/04_scenario_and_weight_experiments.md)
- [Methodology And Claim Safety](site/scoring_assumptions/05_methodology_and_claim_safety.md)
- [Headless Execution And QA](site/scoring_assumptions/06_headless_execution_and_qa.md)
- [Critical Review](site/scoring_assumptions/CRITICAL_REVIEW.md)

## Default Decisions For First Build

- Route: `/scoring/`.
- Nav label: `Scoring`.
- Use existing local state; do not create a second state store.
- Show all degree types by default, but keep degree filter visible.
- Do not prefill private applicant values in committed code.
- If the user has entered MCAT/GPA locally, show those exact local values in their browser.
- If no value is entered, show `Not entered` and exclude that component from the denominator.
- Default school breakdown target is the current top `Your Rank` school.
- User can choose another school from a dropdown.
- Export is optional for the first implementation. Do not block on it.

## Verification

Run:

```bash
cd frontend
npm run build
npm run smoke
cd ..
uv run med-school-validate
uv run pytest
git diff --check
```

Smoke checks should verify:

- `/scoring/` exists.
- The page includes `Assumptions in use`.
- The page includes `Weights and formulas`.
- The page includes `School score breakdown`.
- The page includes `present components only`.
- The page does not include unsupported admissions-probability claims.
- The page includes both `Your Rank` and `Baseline Rank`.

## Done Criteria

- A user can see the exact assumptions currently driving the score.
- A user can change MCAT, GPA, state, and component weights from the scoring workspace.
- A user can inspect one school and see component scores, weights, denominator, and weighted contribution.
- A user can compare live rank against baseline rank in a compact table.
- Missing data is obvious and not silently counted as zero.
- The implementation can be executed by a headless Codex worker without new product decisions.
