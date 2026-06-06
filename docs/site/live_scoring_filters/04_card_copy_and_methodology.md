# Card Copy And Methodology

## Objective

Make live scoring transparent and prevent users from confusing it with admissions probability.

## Card Copy

Cards should display:

```text
Your Rank #12
Baseline Rank #34
Your Score 8.1
Coverage partial
```

Suggested labels:

- `Your Rank`
- `Baseline Rank`
- `Your Score`
- `Live fit factors`
- `Missing from live score`

Avoid:

- `Admit chance`
- `Acceptance probability`
- `Safe`
- `Likely admitted`
- `Best`

## Explanation Bullets

Live explanation bullets should be deterministic:

- MCAT fit helped/hurt;
- GPA fit helped/hurt;
- in-state relation helped;
- cost helped/hurt;
- missing cost/stat fields lowered coverage;
- baseline rank remains available.

Example:

```text
MCAT fit and in-state status help this live rank. Cost is missing, so it is excluded from the live score. Baseline Rank remains #34 from generated data.
```

## Methodology Additions

Methodology must include:

- live scoring formulas;
- default weights;
- available live weight controls;
- public/private ownership filter data status;
- data-confidence/source-confidence status as transparency only, not a filter;
- missing-data policy;
- distinction between `Your Rank` and `Baseline Rank`;
- statement that this is not admissions probability.

## Claim Safety

Smoke check should fail if the built output includes uncaveated:

- `guaranteed admission`;
- `acceptance probability`;
- `admit chance`;
- `safe school`;
- `sure thing`;
- `best school`;
- `likely admitted`.

## Done Criteria

- A reviewer can tell which score is live and which is generated.
- No card implies acceptance likelihood.
- Methodology backs up every live label.
