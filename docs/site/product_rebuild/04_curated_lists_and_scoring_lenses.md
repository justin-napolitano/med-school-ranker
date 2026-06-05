# Curated Lists and Scoring Lenses

## Objective

Create curated school lists that can be browsed as editorial/data pages and applied to rankings as scoring lenses.

Curated lists should be more than saved filters. Each list should define eligibility, scoring, reason chips, and confidence.

## Initial Curated Lists

Priority lists:

- Best Cities
- Best Culture Fit
- Best Public Schools
- Best Private Schools
- Best Low Cost
- Best Admissions Realism
- Best Partner Fit

Optional future lists:

- Best In-State Value
- Best DO Options
- Best MD Options
- Best Emergency Medicine Optionality
- Lowest Application Friction
- Strongest Source Confidence

## Data Model

Add:

```text
data/curated_lists.csv
```

Columns:

```text
list_id
slug
title
category
description
route_enabled
eligibility_filter_json
scoring_profile_id
default_apply_mode
source_confidence
methodology_notes
missing_data_behavior
```

Add:

```text
data/scoring_profiles.csv
```

Columns:

```text
scoring_profile_id
label
metric
weight
direction
normalization
notes
```

Optional:

```text
data/curated_list_overrides.csv
```

Columns:

```text
list_id
school_id
override_action
reason
reviewed_by
reviewed_date
```

## Required Field Backlog

Curated lists need these fields to be reliable:

- `ownership_type`: public, private, public-private partnership, unknown;
- `region`;
- city/setting fields;
- culture and partner-fit scores;
- cost fields;
- source-confidence fields;
- LOR burden fields.

Until ownership/culture/city facts are source-backed or manually reviewed, lists depending on those fields should show lower confidence.

## List Page UX

Each list page should include:

- list title and short description;
- methodology summary;
- controls: apply as filter, apply as boost, replace ranking, add top N to shortlist;
- top school cards;
- full ranked table;
- reason chips;
- source-confidence/missing-data notes;
- links to school profiles.

## Lens Application UX

Supported apply modes:

- `filter_only`: restrict rankings to eligible schools;
- `scoring_boost`: use list scoring profile as extra weights;
- `replace_scoring`: rank by the list scoring profile only.

The active lens should be visible in the rankings header.

## Implementation Steps

1. Add curated-list and scoring-profile schemas.
2. Add validation rules for list IDs, slugs, JSON filters, and profile references.
3. Add default curated-list seed rows.
4. Add site payload for lists and scoring profiles.
5. Add `#/lists` index route.
6. Add `#/lists/:slug` detail route.
7. Add lens application to rankings.
8. Add tests for list generation, route rendering, and missing-data behavior.

## Done Criteria

- Curated lists are generated from data files.
- List pages render even when some facts are missing.
- A list can be applied to rankings as filter, boost, or replacement scoring.
- Every ranked list row explains why the school appears.
- Low-confidence lists are labeled honestly.
