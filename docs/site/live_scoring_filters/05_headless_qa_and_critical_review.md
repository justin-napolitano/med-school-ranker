# Headless QA And Execution

## Headless Worker Requirements

The worker must:

- preserve current uncommitted UI work;
- not stage untracked screenshot artifacts;
- add live scoring in contained frontend modules;
- update docs and smoke checks;
- run full frontend and Python verification;
- commit intended changes only;
- not push.

## Required Commands

```bash
cd frontend
npm run build
npm run smoke
cd ..
uv run med-school-validate
uv run pytest
git diff --check
```

## Manual Review Targets

After implementation, review:

- default Build My List;
- changing MCAT/GPA;
- changing home state to Florida;
- excluding Florida;
- excluding a city;
- changing weight sliders;
- marking Not Interested;
- Not Interested tab;
- Methodology.
- confirm no data-confidence/source-confidence filter appears.

## Stop Conditions

Stop and report if:

- live rank cannot be computed without misleading missing-data behavior;
- payload lacks enough fields for state/cost fit and fallback behavior is unclear;
- smoke checks cannot distinguish caveated methodology text from unsupported claims;
- existing UI changes conflict with live scoring work.
- data-confidence filtering is required by old docs or tests; update those stale references instead of keeping the filter.

## Done Criteria

- Headless worker can execute from this plan.
- Verification passes.
- Handoff reports exact command results and remaining risks.
- Data-confidence/source-confidence is transparency-only and not a filter.
