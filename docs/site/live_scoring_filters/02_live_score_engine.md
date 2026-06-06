# Live Score Engine

## Objective

Compute a browser-local `Your Rank` from current applicant inputs and weights.

This is a deterministic fit-ranking model, not an admissions prediction model.

## New Module

```text
frontend/src/lib/live-scoring.ts
```

## Inputs

Use:

- normalized school payload;
- applicant MCAT;
- applicant GPA;
- home state;
- live component weights;
- excluded state/city/ownership filters;
- Not Interested list.

Do not use data-confidence/source-confidence as a filter input. Missing-data and source-quality fields can affect coverage warnings only when explicitly displayed as transparency.

## Required Outputs

For each school:

```text
baselineRank
baselineScore
yourRank
yourScore
liveAdmissionsScore
liveAttendanceScore
liveCoverage
liveContributions[]
liveWarnings[]
```

## Formula Baseline

Reuse Python-equivalent formulas:

```text
mcat_fit = clamp(1, 10, 7 + (applicant_mcat - school_mcat) / 2)
gpa_fit = clamp(1, 10, 7 + (applicant_gpa - school_gpa) / 0.08)
```

## Component Candidates

Admissions side:

- MCAT fit;
- GPA fit;
- state/OOS fit;
- existing generated admissions score fallback when no live component is available.

Attendance side:

- cost fit;
- ownership filter context if source-backed ownership exists;
- location preference where available;
- existing generated attendance score fallback when no live component is available.

## Cost Fit

Cost fit should use the applicable cost basis:

- in-state estimated cost when school state equals applicant state;
- out-of-state estimated cost otherwise;
- fallback to whichever estimated cost is available;
- missing cost lowers coverage and adds warning, not a zero.

Convert cost to a 1-10 score by percentile across available applicable costs:

```text
lowest cost => 10
highest cost => 1
missing cost => null
```

## State Fit

Initial deterministic rule:

```text
same state => 10
school has known OOS-friendly/policy signal => use generated OOS score if present
unknown OOS context => null with warning
```

If no generated OOS score is available in the normalized frontend object, the implementation may add the field from the payload normalization.

## Weighting

Missing components are excluded from the denominator.

Weights should default to a conservative simple model:

```text
MCAT fit: 25
GPA fit: 25
State/OOS fit: 20
Cost fit: 15
Baseline attendance context: 15
```

These are not final admissions beliefs. They are first-pass product defaults.

## Available Component Controls

Expose first:

- MCAT fit;
- GPA fit;
- state/residency fit;
- cost fit;
- baseline attendance context.

Available but should remain secondary until data quality improves:

- research strength;
- match outcomes;
- curriculum;
- culture;
- prestige;
- specialty optionality;
- four-year happiness;
- regret index.

Reason: many of these exist as fields in the data model but are often blank, manually entered, or lower-confidence in the current payload.

Ownership should start as a filter, not a score component, unless source-backed ownership labels are populated and a clear user preference is defined.

Data-confidence/source-confidence should not be a score component or filter in this slice.

## Sorting

If at least one live component is present, sort Build My List by:

1. `yourRank`;
2. baseline rank;
3. school name.

If no live component is present, sort by baseline rank.

## Done Criteria

- Live scores recompute instantly in React.
- Sorting changes when meaningful weights or inputs change.
- Missing values lower coverage and add warnings instead of becoming zero.
- Existing baseline rank stays visible.
