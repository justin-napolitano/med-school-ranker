# Scoring Terms And Contracts

## Objective

Define the scoring vocabulary and data contracts before changing UI.

The user problem is not only that the score is opaque. It is that score labels can imply more certainty than the model supports.

## Required Terms

Use these names consistently:

```text
Your Rank
Your Score
Baseline Rank
Coverage
Component Score
Current Weight
Weighted Points
Assumption
Missing From Score
```

## Definitions

`Your Rank`

Browser-local rank after current user assumptions, filters, exclusions, and weights.

`Your Score`

Weighted 1-10 score computed from available live components.

`Baseline Rank`

Generated rank from the Python pipeline payload. It is useful context, but it does not automatically reflect the current browser assumptions.

Baseline Rank must remain visible as audit context wherever `Your Rank` appears on the Scoring page. It is not itself a live scoring component.

`Coverage`

How many configured components were available for a school. Coverage is not a probability.

`Weighted Points`

The component contribution after normalizing the denominator to present components only.

Example:

```text
component_score = 8
component_weight = 25
present_weight_sum = 80
weighted_points = 8 * 25 / 80 = 2.5
```

`Assumption`

Any user-controlled or defaulted value used to compute `Your Rank`, such as applicant MCAT, applicant GPA, home state, excluded geography, cost basis, or scoring weights.

## Live Components In Scope

The first scoring assumptions workspace should expose only current live components:

- MCAT fit;
- GPA fit;
- state/residency fit;
- cost fit;
- generated school context.

`generated school context` is the display label for the existing baseline attendance context component. It is experimental/optional because the underlying payload score is less intuitive than MCAT, GPA, state, or cost. It must stay visible in the breakdown and weights table, and users must be able to set its weight to zero.

## School Universe In Scope

The first scoring assumptions workspace is MD-only.

DO schools must not appear in `/scoring/` rank movement tables, selected-school dropdowns, or selected-school breakdowns in this slice.

Reason:

- current MCAT/GPA and AAMC-band interpretation is primarily MD-context;
- DO schools may need different source assumptions and applicant-pool framing;
- mixing MD and DO in one scoring table would make the assumptions harder to trust.

Build My List can continue to display MD and DO schools. This scope applies only to the Scoring assumptions workspace.

## Live Components Out Of Scope

Do not add new ranking power yet for:

- DO-specific scoring;
- prestige;
- research;
- match outcomes;
- curriculum;
- culture;
- four-year happiness;
- specialty optionality;
- hidden curriculum;
- regret index.

Those components can be listed as future assumptions, but they should not affect `Your Rank` until their data and methodology are source-backed or explicitly user-entered.

## Data Contract

Extend or adapt `LiveSchoolScore` to support display-ready contribution rows:

```text
component_key
component_label
component_group
applicant_value_label
school_value_label
formula_label
score_value
weight
present_weight_sum
weighted_points
included
not_included_reason_type
reason
source_label
confidence_label
```

Implementation should prefer deriving these from existing scoring internals instead of duplicating formula logic in components.

## Missing Data Contract

Missing data must:

- set `included = false`;
- set `not_included_reason_type = missing_data`;
- display a reason;
- not add zero points;
- not increase denominator;
- lower coverage;
- appear in the school breakdown table.

## Cost Data Contract

Cost scoring must treat non-positive currency values as missing.

Rules:

- `0`, blank, negative, or unparsable cost values are not valid costs;
- a missing in-state cost can fall back to a positive out-of-state or tuition value;
- a missing out-of-state cost can fall back to a positive in-state or tuition value;
- if only one positive residency cost is available, label it as a single listed cost fallback;
- do not score a missing cost side as zero;
- do not infer source-backed ownership status from missing cost shape.

The first implementation should avoid calling this fallback `private school` unless a source-backed `ownership_type` field is present. The transparent label is `single listed cost`.

Zero-weight components must:

- set `included = false`;
- set `not_included_reason_type = zero_weight`;
- display `Not included: weight is 0`;
- not lower data coverage when the underlying data exists;
- remain visible in the school breakdown table.

If all component weights are zero, scoring must be disabled with a visible validation message. Do not silently fall back to default weights.

## Privacy Contract

The page may show exact MCAT/GPA values typed into the browser by the user, but committed code and public payloads must not prefill private applicant values.

No exact private profile values should be written to:

- repo files;
- generated public payloads;
- GitHub Pages artifacts;
- server logs, because there is no server in this slice.

## Claim Safety

Every page or table that shows personalized rank should preserve the caveat:

```text
MCAT/GPA score-screen fit only; not acceptance probability or a school-specific admit chance.
```

Avoid claims that a school is safe, likely, guaranteed, best, or predictive.
