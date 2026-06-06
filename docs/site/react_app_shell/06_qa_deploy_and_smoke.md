# QA Deploy And Smoke

## Objective

Verify the app shell preserves current behavior and remains static-deploy safe.

## Build Commands

Run:

```bash
cd frontend
npm run build
npm run smoke
cd ..
git diff --check
```

Run broader validation if non-frontend generated outputs or Python pipeline code change:

```bash
uv run med-school-validate
uv run pytest
```

## Static Route Smoke Requirements

Extend `frontend/scripts/smoke-check.mjs` to ensure:

- index output includes app shell and Build My List heading;
- interested output includes shell route content;
- applying output includes shell route content;
- not-interested output includes shell route content;
- compare output includes shell route content;
- scoring output includes required scoring text;
- methodology output includes required methodology text;
- at least one school profile output includes profile text;
- at least one school profile output includes local list action text;
- admin output remains distinct and not inside the applicant shell;
- admin is not present as a normal applicant nav item;
- recommendations is deprecated or aliases Build My List and does not duplicate a second workflow;
- unsupported claim checks still run across all HTML files.

Do not weaken existing claim-safety checks.

## Manual QA Checklist

In local dev server:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Check:

- hard refresh `/`;
- confirm first load can render defaults and then update from saved browser preferences;
- hard refresh `/interested/`;
- hard refresh `/scoring/`;
- hard refresh one `/schools/:slug/`;
- navigate via shell nav;
- navigate card Profile link;
- use profile Interested/Applying/Not Interested/Compare buttons;
- browser back/forward;
- add and remove Interested;
- add and remove Applying;
- add and remove Not Interested;
- add and remove Compare;
- edit MCAT and GPA;
- move scoring sliders;
- exclude Texas;
- exclude a city;
- clear filters;
- export local list JSON;
- open `/admin/` and confirm normal full page route.
- confirm Admin/Data is not visible in normal applicant navigation;
- confirm `/recommendations/` is not a primary workflow.

## Base Path QA

If practical, run:

```bash
cd frontend
ASTRO_BASE_PATH=/med-school-ranker npm run build
npm run smoke
```

If this is not run, report it as a limitation.

## Browser Automation

If existing browser QA tooling is available, use it. Do not install new browser dependencies without user approval.

The prior Chrome DevTools flow may fail in sandboxed environments. If it fails, report the failure and rely on build/smoke plus manual local review.

## Done Criteria

- Build passes.
- Smoke passes.
- App navigation works without full reload for shell routes.
- Direct URLs work.
- Claim safety checks still pass.
- No untracked screenshot files are committed by accident.
