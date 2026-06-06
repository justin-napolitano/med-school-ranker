# Plan Critical Review

## Review Scope

Reviewed on 2026-06-05 after Phase 1 infrastructure, Phase 1.5A static site, Phase 2A source integration, AAMC MCAT/GPA bands, and future-scope predictive admissions model documentation were added.

This review treats the plans as execution material for a headless worker, not as brainstorming notes.

## Verdict

The project has enough structure to continue headlessly, but the next phase must be narrowed to deterministic scoring. The repo already has repeatable build commands, normalized source data, a workbook, and a static site. The remaining risk is that a worker could interpret "scoring" too broadly and accidentally implement predictive probability, scrape new data, or generate committed outputs from private applicant data.

## Critical Findings

### 1. Next Executable Phase Was Not Explicit Enough

Severity: high.

The executive plan says to improve scoring and add profile-specific rankings, but the next worker needs a concrete phase document with inputs, formulas, output columns, privacy rules, and verification commands.

Resolution: add `docs/HEADLESS_SCORING_EXECUTION_PLAN.md` as Phase 2B. This makes deterministic scoring the next executable unit and keeps predictive modeling out of scope.

### 2. Private Profile Handling Needed A Stronger Contract

Severity: high.

The repo correctly ignores `data/manual/private/`, and the user's real profile is local-only. However, future scoring could accidentally write private GPA/MCAT-derived results into committed public outputs.

Resolution: document that committed builds use only public/template profiles by default. Local private scoring outputs must go under ignored `outputs/private/` and must not enter the upload bundle or publishable site.

### 3. Multi-Profile Ranking Is Promised But Not Implemented Yet

Severity: high.

The plans say "multiple profiles," but current `outputs/calculated_rankings.csv` is one row per school and is still driven mostly by `data/school_master.csv` score columns.

Resolution: Phase 2B should introduce profile-aware scoring outputs while preserving the existing default workbook/site path.

### 4. Admissions Tiers Currently Mix Admissions Risk And Desire

Severity: medium.

The current tier logic labels a school `Dream` only when admissions score is low and attendance score is high. That is useful as an application-basket label, but admissions realism should also have its own admissions-only tier.

Resolution: Phase 2B should add an admissions-only tier and keep the desire-aware basket label separate.

### 5. Scoring Formulas Were Under-Specified

Severity: high.

The scoring plan defines components but not enough formula details for MCAT/GPA fit, OOS friendliness, cost, source quality, or partner-entered fit fields.

Resolution: Phase 2B defines deterministic first-pass formulas. These are not probabilities and should be labeled as fit scores.

### 6. Source Integration Is Strong Enough For First-Pass Scoring

Severity: low.

The current source layer has 190 canonical averaged GPA/MCAT rows, including temporarily assumed review/no-match candidates, AAMC acceptance-rate bands for filtering, 151 safe cost rows, and preserved conflict/review queues. This is enough for first-pass deterministic scoring, as long as low-confidence and assumed-match rows remain visible and filterable.

Resolution: do not collect more data before implementing first-pass scoring.

### 7. Plan Statuses Were Stale

Severity: medium.

Several execution plans were still marked as ready/seeded even though their work has been implemented. That makes the project harder for a worker to sequence.

Resolution: update `data/project_subplans.csv` to mark completed execution phases and add the next Phase 2B scoring execution plan.

### 8. Predictive Admissions Modeling Is Correctly Out Of Scope

Severity: low.

The future-scope predictive model plan is the right place for logistic/Bayesian/ML probability work. It should not be mixed into the current deterministic ranking engine.

Resolution: keep predictive modeling as future scope until deterministic scoring, validation, calibration data, and privacy controls are complete.

### 9. Product-Site Rebuild Should Wait For Phase 2B Scoring

Severity: medium.

The product-site rebuild plans are strong: they correctly move the site toward rankings, curated lists, school profiles, admin separation, and publish-safe mode. But the product surface depends on scoring fields that do not exist yet.

Resolution: keep the product-site rebuild drafted and queued after deterministic scoring. The site should not be polished around placeholder rankings.

## Coverage Assessment

| Area | Current Coverage | Headless Readiness | Notes |
| --- | --- | --- | --- |
| Executive scope | Good | Ready | Decisions are clear: exclude Puerto Rico, target 25 apps, keep private profile local. |
| Data architecture | Good | Ready | Raw, normalized, manual, private, and generated layers are documented. |
| Source integration | Good | Ready | Existing source drop is integrated with review queues and quality bands. |
| Static site | Good | Ready | Site is generated locally and can display source status. |
| Workbook | Good | Ready | Workbook is a review artifact, not source of truth. |
| Admissions scoring | Partial | Not ready until Phase 2B plan exists | Needs deterministic formulas and profile-aware output contract. |
| Attendance scoring | Partial | Partially ready | Partner inputs exist but are not yet projected into scores. |
| Multi-profile support | Partial | Not ready | Templates exist; ranking engine must become profile-aware. |
| Private profile safety | Good base | Needs Phase 2B guardrails | Ignored input path exists; ignored private output path now documented. |
| Predictive probability | Future only | Not executable | Correctly out of current scope. |
| Product-site rebuild | Drafted | Blocked by scoring | Good plan, but should follow Phase 2B scoring. |

## Recommended Next Step

Execute Phase 2B: deterministic scoring.

The headless worker should implement school fit scores from existing normalized data and applicant profile values. It should not scrape, train a model, or produce school-specific acceptance probabilities.

Required primary docs for the worker:

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/HEADLESS_SCORING_EXECUTION_PLAN.md`
3. `docs/plans/scoring_engine.md`
4. `docs/plans/admissions_probability.md`

Product-site rebuild docs should be treated as downstream context, not the next work order, until Phase 2B scoring outputs exist.

## Out Of Scope For The Next Worker

- No new web scraping.
- No predictive probability model.
- No ad hoc GitHub Pages publishing outside the checked-in publish-safe workflow.
- No committed private profile data.
- No raw AAMC cache changes.
- No subjective score invention for culture, curriculum, prestige, match, or happiness.
