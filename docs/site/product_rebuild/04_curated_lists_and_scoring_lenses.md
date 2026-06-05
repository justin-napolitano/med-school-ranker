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

## Readiness Gate

Before list pages make strong claims, each list must declare field readiness:

```text
required_fields
available_fields
missing_fields
readiness_label
confidence_label
```

Readiness labels:

- `ready`: required fields are present and reviewed.
- `partial`: some required fields are missing; list can render but must label missing-data caveats.
- `provisional`: core fields are missing; list may be used as a scaffold only.

Initial expected readiness:

- Best Low Cost: partial, because MD cost data exists but DO tuition coverage is incomplete.
- Best Admissions Realism: partial, because source-backed MCAT/GPA exists for a subset and AAMC grid is national context.
- Best Public Schools: provisional until `ownership_type` is populated.
- Best Private Schools: provisional until `ownership_type` is populated.
- Best Cities: provisional until city/region/setting facts and user city preferences are populated.
- Best Culture Fit: provisional until culture-fit evidence or partner-reviewed scores exist.
- Best Partner Fit: provisional until partner inputs are intentionally populated.

The UI must not call a provisional list "best" without showing the provisional status near the title. Acceptable copy: "Best Cities, provisional" or "City Fit Lens, missing city data."

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
2. Add field-readiness fields and validation rules.
3. Add validation rules for list IDs, slugs, JSON filters, and profile references.
4. Add default curated-list seed rows.
5. Add site payload for lists and scoring profiles.
6. Add `#/lists` index route.
7. Add `#/lists/:slug` detail route.
8. Add lens application to rankings.
9. Add tests for list generation, route rendering, readiness labels, and missing-data behavior.

## Done Criteria

- Curated lists are generated from data files.
- List pages render even when some facts are missing.
- A list can be applied to rankings as filter, boost, or replacement scoring.
- Every ranked list row explains why the school appears.
- Low-confidence lists are labeled honestly.
- Provisional lists do not present missing-field rankings as source-backed facts.
