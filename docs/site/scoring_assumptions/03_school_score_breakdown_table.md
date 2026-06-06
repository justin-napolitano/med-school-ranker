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

Controls:

- searchable or standard dropdown for selecting another school;
- preserve selected school in local browser state if practical;
- fallback to first scored school when the selected school is filtered out.

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
- baseline attendance context.

Included rows should show a numeric score and weighted points.

Missing rows should show:

```text
Not included
```

and a plain reason.

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

## Rank Movement Table

Add a second table below or beside the breakdown:

```text
School
Your Rank
Baseline Rank
Your Score
Coverage
Biggest driver
Missing pieces
```

Start with the top 25 currently eligible schools.

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
