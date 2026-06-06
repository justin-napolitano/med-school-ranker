# Product Polish Critical Review

## High: Do Not Rebuild Completed Workflow

Risk: wasting work by re-planning intake, rankings, list builder, score cards, and deployment that already exist.

Resolution: this phase is polish only. Improve presentation, hierarchy, copy, responsiveness, and visual quality over the current workflow.

## High: Do Not Hide Methodology Behind Beauty

Risk: a prettier card UI could obscure missing data, assumed matches, low confidence, or deterministic methodology.

Resolution: cards and score cards must keep source confidence, missing data, and methodology links visible.

## High: Avoid New Workflow States

Risk: adding more statuses would make the product harder to use after the user explicitly simplified to None, Interested, and Applying.

Resolution: keep the existing status model. Polish it; do not expand it.

## High: Score Fit Can Be Misread As Acceptance Probability

Risk: labels like likely or unlikely can sound like admissions prediction if the UI does not constrain them.

Resolution: use score-fit wording and caveats. The signal can summarize MCAT/GPA alignment, but it must not claim school-specific acceptance probability or true admittance likelihood.

## Medium: Hide Buttons Add Noise

Risk: visible Hide actions make card review feel like triage/admin cleanup instead of application-list building.

Resolution: remove manual Hide buttons from product cards. Keep restore/review support for schools hidden by filters, state/dealbreaker rules, or existing local state.

## Medium: Keep Admin Available But Secondary

Risk: hiding admin/source views too aggressively would make the project less auditable.

Resolution: admin and data-quality views stay available in local/full mode but should not dominate public navigation.

## Medium: Styling Can Break Dense Data

Risk: larger cards and nicer spacing can reduce scan efficiency or create mobile overflow.

Resolution: every visible slice needs desktop/mobile checks and stable dimensions for repeated elements.

## Medium: Do Not Duplicate Joins In JavaScript

Risk: frontend polish might reassemble raw facts in browser code and drift from generated nodes.

Resolution: prefer existing generated fields and add node fields with tests only when necessary.

## Ready For Execution

The plan is ready when:

- it explicitly says workflow is already built;
- slices are polish-focused;
- branch names are concrete;
- verification includes publish-safe checks;
- the runbook points to this plan as the next headless phase.
