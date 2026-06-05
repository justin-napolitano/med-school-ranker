# School Universe Plan

## Objective

Maintain a complete, auditable universe of U.S. MD and DO schools, including campus/site distinctions where they affect application or attendance decisions.

## Scope

This plan covers LCME MD programs, AOA/COCA DO schools and sites, application-unit assumptions, parent school relationships, and school identity stability. Puerto Rico, Canada, Caribbean programs, and developing/candidate schools are excluded for the current default universe.

## Inputs

- LCME Accredited Programs directory.
- AOA Osteopathic Medical Schools directory.
- AACOM school dashboard as a cross-check source where useful.
- Manual overrides for naming and application-unit interpretation.

## Outputs

- `data/normalized/school_universe.csv`
- Current aggregate: `data/school_master.csv`
- Source summary in workbook.
- Data quality report for duplicates, inactive rows, and ambiguous campuses.

## Schema

Core fields:

- `school_id`
- `school_name`
- `degree_type`
- `application_unit_type`
- `parent_school_name`
- `campus_name`
- `city`
- `state`
- `state_abbrev`
- `country_or_territory`
- `website`
- `accreditation_status`
- `campus_type_note`
- `application_unit_assumption`
- source metadata fields

## Source Policy

- LCME is canonical for MD program universe and accreditation status.
- AOA/COCA directory is canonical for DO school/site universe.
- AACOM can cross-check DO facts but should not silently override AOA/COCA without a note.
- Manual campus collapsing must be explicit, not automatic.
- Puerto Rico rows are excluded by default with a documented filter, not deleted from raw source snapshots.

## Implementation Steps

1. Convert current scrape logic into dedicated source adapters.
2. Store source snapshots in `data/raw/lcme` and `data/raw/aoa_coca` where practical.
3. Normalize source rows into `school_universe.csv`.
4. Apply a documented default filter excluding Puerto Rico, Canada, Caribbean, and candidate/developing programs.
5. Add manual overrides for display names and application-unit notes.
6. Generate `school_master.csv` from the normalized universe.

## Validation Rules

- `school_id` is unique.
- `degree_type` is one of `MD` or `DO`.
- `active_in_universe` is explicit.
- Excluded schools require `manual_exclusion_flag=TRUE` and `exclusion_reason`.
- Branch/additional location rows must have a parent school or a note explaining why not.

## Open Questions

- Should Canadian MD schools be added later or remain out of scope?
- Should DO additional locations be ranked separately or grouped by application behavior?

## Definition of Done

- The full school universe is reproducible.
- Counts can be compared to source page counts.
- Application-unit assumptions are reviewable in the workbook.
- No school is hidden from the initial universe without a documented reason.
