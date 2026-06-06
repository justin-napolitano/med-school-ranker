# School Score Breakdown Table

## Objective

Show exactly how one selected school gets its `Your Score`.

The table should make the score auditable without requiring code or spreadsheet knowledge.

## Required Section

Section title:

```text
School score breakdown
```

## School Selection

Default selected school:

- current top `Your Rank` school after active filters and assumptions.
- only among active MD schools.

Controls:

- searchable or standard dropdown for selecting another school;
- preserve selected school in local browser state if practical;
- fallback to first scored school when the selected school is filtered out.
- exclude DO schools from the dropdown in this slice.

## Summary Header

Show:

```text
School name
City, state
Degree
Your Rank
Baseline Rank
Your Score
Coverage
```

## Required Table Columns

```text
Component
Applicant input
School value
Formula
Score
Weight
Weighted points
Included?
Reason
```

## Required Rows

One row per live component:

- MCAT fit;
- GPA fit;
- state/residency fit;
- cost fit;
- generated school context.
- if the generated school context weight is zero, keep the row visible and show `Not included: weight is 0`.

Included rows should show a numeric score and weighted points.

Missing rows should show:

```text
Not included
```

and a plain reason.

Zero-weight rows should show:

```text
Not included: weight is 0
```

Do not present zero-weight rows as missing data.

## Denominator Explanation

Add a visible line:

```text
Weighted points use present components only. Missing values are not treated as zero.
```

## Formula Labels

Formula labels should be compact:

```text
7 + (applicant MCAT - school MCAT) / 2
7 + (applicant GPA - school GPA) / 0.08
Same state or source-backed OOS context
Lowest applicable cost = 10, highest = 1
Generated attendance context score
```

Display label:

```text
Generated school context
```

The row may reference baseline attendance context in methodology, but user-facing table labels should use `Generated school context`.

## Rank Movement Table

Add a second table below or beside the breakdown:

```text
School
Your Rank
Baseline Rank
Rank movement
Your Score
Coverage
Why did this move?
Missing pieces
```

Start with the top 25 currently eligible MD schools.

`Why did this move?` must be deterministic. It should use:

- the largest weighted live contribution when the school moved up;
- the lowest weighted live contribution or largest missing component when the school moved down;
- `No meaningful movement from baseline` when ranks are equal or nearly equal.

Do not use generated freeform prose for this column.

## Sorting

Default sort:

1. `Your Rank`;
2. `Baseline Rank`;
3. school name.

Do not add complex sortable columns in the first pass unless it is already trivial in the existing frontend pattern.

## Done Criteria

- The selected school's `Your Score` can be manually reconciled from visible rows.
- Weighted points add up to the displayed score within rounding tolerance.
- Missing components are obvious.
- Rank movement is visible without reading cards one by one.
- DO schools are excluded from this first scoring table.
- `Why did this move?` is visible and deterministic.
