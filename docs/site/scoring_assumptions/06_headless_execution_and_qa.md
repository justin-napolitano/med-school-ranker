# Headless Execution And QA

## Objective

Make the implementation executable by a headless Codex worker without needing new product decisions.

## Files Likely To Change

Expected frontend files:

```text
frontend/src/lib/live-scoring.ts
frontend/src/lib/school-utils.ts
frontend/src/components/useLocalSchoolState.ts
frontend/src/components/PreferenceControls.tsx
frontend/src/components/ScoringAssumptionsApp.tsx
frontend/src/pages/scoring.astro
frontend/src/pages/methodology.astro
frontend/src/layouts/ProductLayout.astro
frontend/src/styles/global.css
frontend/scripts/smoke-check.mjs
```

Expected docs:

```text
docs/SCORING_ASSUMPTIONS_WORKSPACE_EXEC_PLAN.md
docs/site/scoring_assumptions/
```

## Implementation Order

1. Extend live scoring contribution data without changing existing score outputs.
2. Add reusable label/format helpers.
3. Add `/scoring/` route and nav item.
4. Build assumptions table from existing local preference state.
5. Build weights/formulas table from current live scoring metadata.
6. Build selected-school breakdown table.
7. Build rank movement table for top currently eligible MD schools.
8. Add deterministic `Why did this move?` labels from contribution data.
9. Update methodology.
10. Extend smoke checks.
11. Run verification.

## QA Checklist

Manual or Playwright/screenshot QA should verify:

- desktop Scoring page layout;
- mobile Scoring page layout;
- changing MCAT changes score breakdown;
- changing GPA changes score breakdown;
- changing home state changes state/residency row where data exists;
- changing a weight changes weighted points;
- selected school dropdown works;
- selected school dropdown excludes DO schools;
- Build My List still works;
- Interested/Applying/Not Interested still work;
- Scoring page explains that DO scoring is separate/future scope;
- generated school context appears and can be set to weight 0;
- all-zero weights disable scoring visibly;
- rank movement table includes `Why did this move?`;
- no horizontal overflow hides table content on mobile.

## Required Commands

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

## Commit Rules

- Commit only intentional source/docs changes.
- Do not stage untracked screenshot artifacts under `outputs/site_qa/screenshots`.
- Do not push unless explicitly requested.

## Done Criteria

- Headless worker can implement the slice from `HEADLESS_PROMPT.md`.
- Verification commands pass.
- Any remaining risks are recorded in the final worker summary.
