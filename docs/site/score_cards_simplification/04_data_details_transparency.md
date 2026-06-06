# Data Details And Transparency

## Goal

Preserve transparency without making the default profile feel like an admin console.

## Collapse By Default

- raw profile node sections;
- missing fields;
- source references;
- data-quality issues;
- export controls;
- local schema details.

## Requirements

- Missing values remain explicit.
- Source links remain accessible.
- Data quality remains visible as a badge or summary in At a Glance.
- MCAT/GPA gaps distinguish approved canonical missingness from candidate-only evidence and no candidate value found.

## Admissions Stat Coverage Labels

Use source-normalization-neutral labels:

- `Approved value` when `data/normalized/admissions_stats.csv` supplies the scoring value;
- `Assumed candidate value` when `outputs/admissions_stats_candidates.csv` has source evidence promoted from a review/no-match best match;
- `No candidate value found` when the source layer has no value.

Do not promote candidate values or alter source normalization in this UI slice.
