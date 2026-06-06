# Per-School Override Model

## Objective

Allow a user to adjust scoring emphasis for one school without corrupting the global scoring model.

The model must be deterministic, transparent, browser-local, and reversible.

## Core Rule

Global preferences remain the source of `Your Score`.

Per-school overrides produce a separate `Adjusted Score`.

Do not silently replace global scoring.

## Local State

Extend `useLocalSchoolState` with:

```ts
type SchoolWeightOverride = {
  schoolSlug: string;
  weights: Partial<ScoringWeights>;
  updatedAt: string;
};
```

Add state/actions:

```ts
schoolWeightOverrides: Record<string, SchoolWeightOverride>;
getSchoolWeightOverride(slug: string): SchoolWeightOverride | null;
setSchoolWeightOverride(slug: string, weights: Partial<ScoringWeights>): void;
removeSchoolWeightOverride(slug: string): void;
clearSchoolWeightOverrides(): void;
```

Persist under a versioned local-storage key.

## Score Derivation

Add pure helpers, preferably near live scoring:

```ts
scoreSchoolWithOverride(school, schools, globalPreferences, override)
scoreSchoolsWithOverrides(schools, globalPreferences, overrides)
```

Output should include:

```ts
type SchoolAdjustedScore = {
  slug: string;
  globalScore: LiveSchoolScore;
  adjustedScore: LiveSchoolScore | null;
  overrideApplied: boolean;
  adjustedRank: number | null;
};
```

`adjustedScore` is null when no override exists.

## Override Editor

First implementation can use an inline panel or modal. It must show:

- global weights;
- editable override weights;
- component preview;
- validation;
- apply button;
- reset button.

Validation:

- weights must be finite numbers;
- weights cannot be negative;
- all-zero override is invalid;
- missing components still do not count as zero.

## Comparability Warning

When an override exists, show:

```text
Override applied. Adjusted Score uses school-specific weights, so compare it alongside Global Score.
```

This is not legal/medical fine print. It is product clarity.

## Ranking Behavior

In the school browser:

- default sort uses global rank/global score;
- if user selects adjusted-score sort, schools with overrides sort by adjusted score and schools without overrides sort by global score;
- show an `Adjusted sort` indicator when active.

In Build My List:

- do not change the default ranking order in this slice unless the implementation adds a visible toggle;
- if adjusted values appear there, label them clearly.

In profiles:

- show global score and adjusted score when override exists;
- expose reset/edit override actions.

## Acceptance Criteria

- Applying an override changes only that school's adjusted score.
- Global score remains unchanged.
- Reset removes adjusted score display.
- Missing data policy remains the same.
- Zero-weight policy remains the same.
- Override state survives route changes and page refreshes.

