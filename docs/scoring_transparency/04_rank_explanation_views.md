# Rank Explanation Views

## Objective

Expose scoring explanations in the site and workbook so the model can be reviewed quickly by the user and partner.

## Site UX

Add a "Why This Rank?" section to the school detail view.

Required display:

- decision rank and rank band;
- rank confidence;
- admissions score;
- attendance score;
- overall school value;
- top positive contributors;
- top negative contributors;
- missing or low-confidence drivers;
- scenario rank comparison;
- contribution table with raw value, score, weight, contribution, source, and confidence.
- local/private-derived badge when selector values are active.

First proof-of-concept interactive controls:

- AAMC MCAT band selector.
- AAMC GPA band selector.
- Applicant state selector.
- Active MD schools only.
- Browser-local state only.
- CSV export/download for selected assumptions and current ranked MD rows.
- No tie-breaking beyond existing shared-rank behavior.

The table should be filterable by:

- score group;
- scenario;
- missing status;
- confidence;
- source type.

## Workbook UX

Add a scoring audit tab or detail section.

Recommended tabs:

- `Score Contributions`
- `Score Explanations`
- `Decision Rollup`

The workbook should be reviewable even if the site is not used.

## Explanation Text

Generate deterministic short text, not AI-written prose.

Example:

```text
Strong GPA fit and Florida residency help this school. MCAT fit is below school average. Rank confidence is partial because curriculum and culture inputs are missing.
```

Rules:

- Mention no more than three positive drivers.
- Mention no more than three negative or missing drivers.
- Label AAMC grid context as national aggregate MD data, not school-specific probability.
- Do not imply certainty where coverage is low.

## Scenario Comparison

Show:

- Balanced rank.
- Admissions Realist rank.
- Lifestyle rank.
- Financial rank.
- Prestige rank.
- Specialty Optionality rank.

Highlight schools that remain strong across scenarios, but do not overclaim if scenario coverage is low.

## Done Criteria

- A reviewer can inspect one school and understand why it ranked where it did.
- The site and workbook use the same generated explanation data.
- Private explanation data stays local unless a local-private mode is intentionally selected.
