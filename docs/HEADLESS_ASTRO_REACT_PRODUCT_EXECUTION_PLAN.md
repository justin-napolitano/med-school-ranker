# Headless Astro React Product Execution Plan

## Objective

Execute the Astro + React applicant product frontend build non-interactively from the current repository state.

This plan intentionally preserves the existing Python generator and admin static site. The worker creates a contained `frontend/` static app that consumes `outputs/site/data/site_payload.json`.

## Start State Audit

Run:

```bash
git status --short --branch
rg --files
sed -n '1,220p' README.md
sed -n '1,220p' docs/SITE_ASTRO_REACT_PRODUCT_EXEC_PLAN.md
node -e "const p=require('./outputs/site/data/site_payload.json'); console.log(p.meta, Object.keys(p), p.schools.length)"
```

If `outputs/site/data/site_payload.json` is missing, regenerate:

```bash
uv run med-school-build-site --site-mode publish_safe
```

Do not edit or commit unrelated untracked screenshots under `outputs/site_qa/screenshots`.

## Execution Steps

1. Read the Astro product plan and child docs in `docs/site/astro_product/`.
2. Confirm there is no existing frontend package manager choice. If none exists, use npm.
3. Scaffold `frontend/` with Astro static output and React integration.
4. Add deterministic data sync:

```bash
cd frontend
npm run sync:data
```

5. Implement routes:

```text
/
/recommendations
/interested
/applying
/schools/[slug]
/compare
/methodology
/admin
```

6. Implement card/list-first applicant views using generated JSON only.
7. Add local-state caps:

```text
Interested max: 50
Applying max: 25
```

8. Add `frontend/scripts/smoke-check.mjs` and wire `npm run smoke`.
9. Run the full verification set.
10. Commit all intended changes with a clear message. Do not push.

## Smoke Check Requirements

The smoke script must verify:

- `frontend/dist/index.html` exists after build.
- Build My List appears as the first/product route.
- Product output includes score-screen caveat language.
- Unsupported positive claims are absent in product output:
  - `guaranteed admission`
  - `acceptance probability`
  - `best school`
  - `safe school`
  - `sure thing`
- The smoke check may allow explicitly negated/caveated uses in methodology/caveat copy, but product cards must not present these as claims.
- Routine visible Hide button text is absent.
- `/admin/index.html` exists and contains admin/data separation copy.

## Required Verification

Run from repo root:

```bash
cd frontend
npm install
npm run build
npm run smoke
cd ..
uv run med-school-validate
uv run pytest
git diff --check
```

## Stop Conditions

Stop only if:

- the generated payload is missing and cannot be regenerated;
- npm install or build fails in a way that prevents creating a static app;
- existing dirty changes conflict with the required files;
- Python validation or tests fail for reasons that cannot be isolated and documented;
- claim-safety smoke checks cannot be made deterministic.

## Handoff Format

Close with:

- committed SHA and message;
- files changed at a high level;
- verification commands and pass/fail status;
- exact failures for any skipped or failing checks;
- residual risks.
