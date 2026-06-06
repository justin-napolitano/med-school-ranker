# Critical Review

## Risks

- The generated payload still contains broad admin-era aggregate fields. The frontend must select product-safe fields deliberately and avoid exposing table-first source surfaces to applicants.
- MCAT/GPA fit can be misread as admit likelihood. Every score-screen label needs a visible caveat.
- Missing applicant MCAT/GPA inputs are common in the current generated data. The product must show useful cards without pretending the fit screen is complete.
- Static school routes depend on copied generated JSON. If `npm run sync:data` is skipped, frontend builds may use stale payloads.
- Local browser state is useful but not durable across devices. Export should be available and clearly local.
- Admin route existence is not data security. Publish-safe payload generation remains the Python builder's responsibility.

## Required Mitigations

- Keep Build My List as `/` and keep admin under `/admin`.
- Use cards/lists first; avoid public ranking tables as the main surface.
- Include generated caveat copy on cards, profiles, compare, and methodology.
- Add headless smoke checks for unsupported claims and routine Hide button text.
- Document exact commands in README and headless plan.

## Out Of Scope For This Pass

- Replacing Python build outputs.
- Changing ranking formulas.
- Building a backend account system.
- Adding predictive admissions modeling.
- Scraping or enriching data.
- Deploying `frontend/dist` to GitHub Pages.
