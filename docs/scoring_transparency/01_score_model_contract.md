# Score Model Contract

## Objective

Define the language and output contract for transparent ranking.

The core improvement is to make rank labels, score groups, components, weights, contribution math, and confidence labels understandable without reading code.

## Terms

Use these display terms:

- `decision_rank`: human-facing label for the main rank.
- `overall_rank`: compatibility column for existing outputs.
- `overall_school_value`: weighted model score used for the main rank.
- `admissions_score`: can-get-in fit score.
- `attendance_score`: want-to-attend score.
- `rank_band`: coarse bucket such as top application candidate, research seriously, watchlist, low priority, incomplete.
- `rank_confidence`: confidence in the rank based on coverage and source quality.
- `component_score`: normalized 1-10 score for a single factor.
- `component_weight`: weight used inside a score group or scenario.
- `weighted_contribution`: component score multiplied by its normalized weight.

## Required Labels

Exact ranks should be paired with broader labels:

```text
overall_rank
decision_rank_label
rank_band
rank_confidence
application_bucket
admissions_fit_tier
suggested_funnel_bucket
```

Suggested rank bands:

- `Top application candidate`
- `Research seriously`
- `Watchlist`
- `Low priority`
- `Incomplete data`
- `Excluded by hard-no`

## Confidence Labels

Suggested rank confidence:

- `high`: strong coverage and no severe source warnings.
- `medium`: enough scored components for directional use, but some missing or low-quality fields.
- `partial`: score exists but important components are missing.
- `provisional`: rank is mostly scaffolded or driven by a narrow subset of fields.
- `excluded`: row is intentionally kept visible but removed from ranking.

## Formula Transparency

Every score component should expose:

- raw applicant input where relevant;
- raw school input where relevant;
- formula note;
- normalized component score;
- score group;
- weight;
- weighted contribution;
- source name or manual input owner;
- source confidence;
- missing-data status.

## Backward Compatibility

- Keep `overall_rank` until workbook/site consumers no longer rely on it.
- Add `decision_rank` or `decision_rank_label` as display fields rather than renaming columns immediately.
- Keep existing scenario rank columns.
- Add explanation fields additively.

## Done Criteria

- A non-technical reviewer can distinguish exact rank, rank band, admissions fit, attendance preference, and confidence.
- Output names are stable enough for workbook/site implementation.
- Existing downstream outputs still build.
