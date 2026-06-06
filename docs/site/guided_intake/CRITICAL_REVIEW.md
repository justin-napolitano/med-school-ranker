# Critical Review: Guided Applicant Intake

## Finding 1: Intake Could Become A Hidden Recommender

The largest risk is making the site feel simple by hiding rules and quietly changing rankings.

Mitigation:

- Treat intake as a visible lens over deterministic scoring.
- Show active rules and grouped-result criteria.
- Keep methodology and advanced table access available.

## Finding 2: Questions Could Outrun Available Data

Lifestyle, culture, curriculum, and career optionality are valuable, but source coverage is incomplete.

Mitigation:

- Mark unsupported answers as awareness-only or research prompts.
- Do not score unavailable fields as zeros.
- Show missing-data chips near affected schools.

## Finding 3: The Flow Could Still Feel Like A Spreadsheet

If intake only sets filters and returns the same large table, the product problem remains.

Mitigation:

- Make grouped school cards the default post-intake result.
- Keep tables as advanced review, not the primary first-use surface.

## Finding 4: Personal Answers Could Leak Into Public Artifacts

Intake collects private preference information. It must not enter generated publish-safe outputs.

Mitigation:

- Store answers only in browser local state unless explicitly exported.
- Add upload-bundle privacy checks.
- Do not commit local exports or private answers.

## Finding 5: Dealbreakers Could Remove Too Much Too Quietly

Applicants may change their mind. Hard exclusions should not silently erase options.

Mitigation:

- Use reversible hide/restore behavior.
- Keep hidden-school review visible.
- Explain every exclusion reason.

## Finding 6: Strategy Labels Could Be Misread As Admissions Probability

Safer List, Balanced List, and Reach-Heavy List are list-building lenses, not acceptance odds.

Mitigation:

- Use language like "list strategy" and "review group."
- Avoid probability claims.
- Link to the future predictive model document only as out-of-scope context.

## Finding 7: "Personalized" Could Become An Empty Claim

If the intake only records answers but does not change grouping, chips, or next actions, the product still requires spreadsheet interpretation.

Mitigation:

- Every required answer must affect a visible rule, chip, group, target count, or next action.
- Optional awareness-only answers must be labeled that way.
- The intake summary must show which answers changed the current view.

## Go/No-Go Assessment

This slice is ready for headless execution after the profile-node UI adoption work is merged or included in the worker branch.

The build should prioritize:

1. controlled intake route;
2. deterministic answer mapping;
3. grouped card results;
4. local privacy/export;
5. methodology and QA.
