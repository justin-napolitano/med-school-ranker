# Score Cards Simplification Executive Plan

## Objective

Turn Score Cards from an admin-heavy dossier table into an applicant-friendly school review surface.

The user should be able to browse all schools, open a school profile, mark list status, and compare schools without needing to understand source queues, missing-data workflows, or internal dossier terminology.

## Current Problem

The current Score Cards and profile routes expose too much internal machinery:

- research status;
- missing dossier/score-card sections;
- visibility state;
- export controls;
- source confidence details;
- local schema language;
- admin-like table density.

Those fields are useful, but they should not dominate the applicant-facing experience.

## Product Direction

Use these visible concepts:

- `Score Cards`
- `School Profile`
- `Data Details`

Keep internal `dossier` data contracts stable for now. Rename only visible UI language unless a separate migration plan exists.

## Scope

This plan covers:

- the `#/dossiers` Score Cards tab;
- individual `#/schools/:slug` score-card/profile pages;
- status controls for `None`, `Interested`, and `Applying`;
- collapsed details for data quality, sources, and exports.

## Non-Goals

- Do not rename `school_dossiers.csv` or `school_dossier_edits_v1`.
- Do not change ranking formulas.
- Do not change source normalization.
- Do not solve missing MCAT/GPA data coverage in this UI slice.
- Do not replace the static site architecture.

## Target Score Cards Tab

The Score Cards tab should become a user-facing school browser.

Primary columns:

- Decision Rank
- School
- Location
- Admissions Tier
- MCAT average
- GPA average
- In-state estimated cost
- Out-of-state estimated cost
- Status: `None / Interested / Applying`
- Actions: `Open`, `Compare`

Remove or collapse from the main table:

- research status;
- missing sections;
- visibility state;
- source confidence;
- CSV export controls;
- admin/source language.

Default behavior:

- show all schools by default;
- hide only hard-no schools from the primary view for now;
- do not show hidden or hard-no controls as a primary workflow in this slice.

Primary filters:

- status;
- admissions tier;
- state;
- degree;
- data quality.

## Target School Profile Page

Each school profile should be organized as:

1. Header
   - school name;
   - location;
   - degree;
   - source link when available;
   - `None / Interested / Applying` status switch;
   - compare action.

2. At a Glance
   - Decision Rank;
   - Admissions Tier;
   - MCAT average;
   - GPA average;
   - AAMC band;
   - in-state estimated cost;
   - out-of-state estimated cost;
   - data quality badge.

3. Why It Ranks Here
   - concise bullets;
   - avoid making it feel like a spreadsheet audit.

4. Review Controls
   - status switch: `None / Interested / Applying`;
   - compare action;
   - no notes UI in this slice.

5. Data Details
   - collapsed by default;
   - source-backed profile sections;
   - missing fields;
   - source links;
   - data-quality issues;
   - export actions.

## Admissions Stat Coverage Note

The site currently has two admissions-stat layers:

- approved canonical stats in `data/normalized/admissions_stats.csv`;
- candidate/source evidence in `outputs/admissions_stats_candidates.csv`.

Rankings only use the approved canonical layer. As of the current build, the active school universe has 233 schools and 190 have canonical MCAT/GPA values available for scoring. Review/no-match candidates are temporarily assumed correct when the matcher has a best school row, and those rows are labeled with `assumed_match_*` confidence values. The remaining schools do not currently have a candidate value in the source layer.

This Score Cards UI slice should not change source normalization. It should make the distinction clear:

- `Approved value` when the canonical file drives scoring;
- `Assumed candidate value` when source evidence exists but was promoted from a review/no-match best match;
- `No candidate value found` when no source-layer value exists.

## Work Slices

1. Score Cards Tab Simplification
   - Replace the current dossier table columns with the applicant-facing columns above.
   - Keep filters simple.
   - Keep status switch consistent with Rankings, Interested, and Applications.

2. Profile Header and At-a-Glance
   - Rework the school route header and snapshot cards into a clean profile summary.
   - Keep source and data confidence visible but secondary.

3. Review Controls
   - Keep status controls simple.
   - Do not add notes in this slice.
   - Move hard-no and export controls out of the first visible row.

4. Data Details Collapse
   - Put raw node sections, source refs, missing fields, data-quality issues, and exports inside collapsed details.
   - Keep the information accessible for transparency.

5. QA and Regression Check
   - Rebuild site.
   - Run tests and validation.
   - Verify score-card tab, school profile, status switches, compare actions, missing MCAT/GPA labels, and export access.

## Acceptance Criteria

- Score Cards tab no longer reads like an admin dossier table.
- User can mark a school `None`, `Interested`, or `Applying` from the Score Cards tab.
- School profile opens as an applicant-facing profile first, with source/admin details secondary.
- Missing MCAT/GPA values explain whether the gap is canonical approval, candidate-only evidence, or no candidate value found.
- Export and source details remain available but are not primary.
- Existing local edit exports still work.
- Tests and validation pass.

## Subplans

- [Score Cards Tab Simplification](site/score_cards_simplification/01_score_cards_tab.md)
- [School Profile Layout](site/score_cards_simplification/02_school_profile_layout.md)
- [Review Controls](site/score_cards_simplification/03_my_notes_panel.md)
- [Data Details and Transparency](site/score_cards_simplification/04_data_details_transparency.md)
- [QA and Regression](site/score_cards_simplification/05_qa_and_regression.md)
- [Critical Review](site/score_cards_simplification/CRITICAL_REVIEW.md)
