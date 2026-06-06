# QA, Claim Safety, And Deploy

## Objective

Verify the school browser and override behavior without introducing route, scoring, or claim-safety regressions.

## Static Smoke Checks

Update `frontend/scripts/smoke-check.mjs` to check:

- `/schools/index.html` exists;
- `/schools/` output includes the app shell;
- `/schools/` includes `Schools`;
- `/schools/` includes school-browser route marker text or attribute;
- applicant shell nav includes `Schools`;
- applicant shell nav still excludes `Admin/Data`;
- applicant shell nav still excludes `Recommendations`;
- `/schools/:slug/` profile still includes profile content;
- `/admin/` does not include the app shell;
- unsafe claims remain absent.

## Build Commands

Run:

```bash
cd frontend
npm run build
npm run smoke
ASTRO_BASE_PATH=/med-school-ranker npm run build
ASTRO_BASE_PATH=/med-school-ranker npm run smoke
```

Run from repo root:

```bash
git diff --check
```

## Browser QA

Use local dev server and a browser automation pass if available.

Check:

- open `/schools/`;
- search by a school name;
- filter by state;
- open a profile from a card;
- back button returns to `/schools/`;
- mark a school Interested from `/schools/`;
- verify status appears on Interested route;
- apply a school-specific override;
- refresh page and confirm override remains;
- open profile and confirm adjusted score/chip appears;
- reset override and confirm chip disappears;
- direct refresh `/schools/`;
- direct refresh `/schools/:slug/`;
- verify `/admin/` remains separate;
- verify `/recommendations/` still aliases Build My List.

## Claim Safety

Do not add copy that implies:

- admission certainty;
- school-specific admission probability;
- safety;
- guaranteed outcomes;
- predictive admissions model.

Required caveat should remain visible on scoring-related surfaces:

```text
MCAT/GPA score-screen fit only; not acceptance probability or a school-specific admit chance.
```

## Performance Review

The school browser may render many cards.

First slice can use simple pagination or load-more behavior.

Watch for:

- slow hydration;
- card grid jank;
- oversized school profile payloads;
- mobile overflow;
- sticky filter rail scroll issues.

## Acceptance Criteria

- Static and base-path builds pass.
- Smoke checks pass.
- Browser QA passes.
- No unrelated screenshot artifacts are staged.
- The branch has a focused commit.

