# Headless Prompt

Use this prompt for the live scoring and filter-controls `codex exec` run.

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/LIVE_SCORING_FILTERS_EXEC_PLAN.md and its subplans under docs/site/live_scoring_filters/.

Context:
- The branch may already contain uncommitted frontend/product-app work. Preserve it.
- Do not stage untracked screenshot artifacts under outputs/site_qa/screenshots.
- The current user decisions are: city exclusion via dropdown, state-first filtering, Texas quick exclude, public/private filter only when source-backed ownership data exists, Not Interested as a simple card button plus local page, Your Rank primary, Baseline Rank secondary, and no data-confidence/source-confidence filters for now.

Implementation requirements:
1. Finish current UI cleanup:
   - Recommendations is not a primary nav tab.
   - Build My List is the recommendation surface.
   - Not Interested exists as a browser-local page/list and card action.
   - Not Interested removes schools from Build My List and from Interested/Applying/Compare.
   - Remove any remaining Hide action from applicant-facing cards.
   - Remove data-confidence/source-confidence filter state, controls, copy, and tests. Confidence/source-quality fields may remain visible only as transparency.

2. Add stronger Build My List filters:
   - state exclusion multi-select/chips;
   - city exclusion dropdown/chips using payload city/state pairs;
   - Texas quick exclude;
   - ownership dropdown only if source-backed ownership labels are available; otherwise Unknown-only/disabled with plain copy;
   - clear controls;
   - transparent counts: shown / eligible / total.

3. Add browser-local live scoring:
   - create a contained live scoring module;
   - compute deterministic Your Score and Your Rank from applicant MCAT, GPA, home state, cost basis, baseline attendance context, and user weights;
   - keep Baseline Rank visible from generated payload;
   - missing components are excluded from denominator and surfaced as coverage warnings, never treated as zero;
   - changing inputs/weights must update ordering live.

4. Add compact weight controls:
   - MCAT fit, GPA fit, state/residency fit, cost fit, baseline attendance context;
   - reset weights;
   - neutral presets only if useful: Balanced, Cost-aware, Academic-screen focused, Florida-first, State-first.
   - Do not use Safety, Likely Admit, Admit Chance, Best School, or similar claimy labels.

5. Update cards and methodology:
   - show Your Rank, Baseline Rank, Your Score, coverage, and deterministic live factor bullets;
   - methodology explains formulas, defaults, missing-data policy, live vs baseline distinction, ownership data status, and that this is not admissions probability.

Safety rules:
- No predictive admissions model.
- No school-specific acceptance probability.
- No scraping/download/new source ingestion.
- No database or persistence beyond browser localStorage.
- No private applicant data committed.
- No inference of public/private ownership from school names.
- Do not make quality claims about public/private ownership.

Verification:
- cd frontend && npm run build && npm run smoke
- cd .. && uv run med-school-validate && uv run pytest && git diff --check
- Add or update smoke checks for Your Rank, Baseline Rank, Not Interested route, no routine Hide controls, no data-confidence filter, and no unsupported admissions claims.

Commit intended changes only. Do not push.
Final handoff must include changed areas, verification results, commit hash, and remaining data risks.
```
