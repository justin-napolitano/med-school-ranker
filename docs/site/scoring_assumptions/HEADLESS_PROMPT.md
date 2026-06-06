# Headless Prompt: Scoring Assumptions Workspace

Use this prompt for a future `codex exec` implementation run.

```text
You are in /Users/justin/repos/med-school-ranker.

Read and execute docs/SCORING_ASSUMPTIONS_WORKSPACE_EXEC_PLAN.md and all subplans under docs/site/scoring_assumptions/.

Goal:
Add an applicant-facing /scoring/ page that helps users understand the current browser-local score. It must show assumptions in use, weights and formulas, selected-school score breakdown, and rank movement, using the same local state and live scoring engine as Build My List.

Hard requirements:
- Do not change the default scoring formulas unless needed only to expose existing contribution math.
- Do not create a predictive admissions model.
- Do not use "safe school", "likely admitted", "guaranteed", "best school", or uncaveated admissions-probability language.
- Do not commit private applicant values.
- Do not add server writeback, database, scraping, or new data ingestion.
- Do not score DO schools on /scoring/ in this slice; explain that DO scoring needs a separate flow.
- Do not stage untracked screenshot artifacts under outputs/site_qa/screenshots.

Implementation:
1. Extend live scoring outputs so each component can render:
   component label, applicant input label, school value label, formula label, score, weight, present weight sum, weighted points, included status, reason.
2. Add /scoring/ and nav item "Scoring".
3. Build an Assumptions in use table using existing browser-local preferences, with scoring universe shown as MD schools only.
4. Build a Weights and formulas table using current live scoring metadata.
5. Build a School score breakdown table for the selected MD school, defaulting to the current top MD Your Rank school.
6. Build a rank movement table for the top currently eligible MD schools.
7. Include deterministic "Why did this move?" text based on contribution data.
8. Relabel baseline attendance context as "Generated school context", keep it visible, and support weight 0 as "Not included: weight is 0".
9. If all weights are zero, disable scoring visibly instead of falling back to defaults.
10. Update /methodology/ to link to the Scoring page and document formulas, weights, denominator basis, missing-data policy, zero-weight policy, MD-only scope, DO future flow, movement explanation, and local-state privacy.
11. Extend frontend smoke checks for /scoring/, assumptions table, breakdown table, denominator language, Why did this move, MD-only/DO-scope copy, Your Rank/Baseline Rank, and claim safety.

Verification:
cd frontend && npm run build
cd frontend && npm run smoke
uv run med-school-validate
uv run pytest
git diff --check

Commit:
Commit the implementation with a concise message. Do not push.

Final summary:
Report changed files, verification results, commit hash, and any remaining risks.
```
