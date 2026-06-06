# Guided Results and School Cards

## Purpose

Define the applicant-facing output after intake.

The result should be a grouped, card-first review surface with a clear path to advanced tables.

## Result Groups

Use these first groups:

- `Start Here`
- `Florida Options`
- `Reach Schools To Research`
- `Compare Next`
- `Need More Data`
- `Lower Priority Or Hidden`

Groups should be deterministic and derived from existing ranking/card data plus the intake context.

These labels describe review priority. They do not claim school-specific admissions probability.

Default disclosure behavior:

- show high-priority groups by default;
- collapse lower-priority groups until clicked;
- keep collapsed or expanded state local and reversible;
- at minimum, `Need More Data` and `Lower Priority Or Hidden` should start collapsed.

## Card Requirements

Each school card should show:

- school name and location;
- degree type;
- Decision Rank and rank band;
- admissions fit summary, labeled as deterministic fit context;
- MCAT/GPA context;
- cost/debt summary;
- source confidence or missing-data chips;
- top reason chips;
- top risk chips;
- next action;
- buttons for profile, compare, shortlist/apply, hide/restore.

## Explanation Requirements

Cards should answer:

1. Why is this here?
2. Why might it be good?
3. What should we worry about?
4. What is missing or low-confidence?
5. What should we do next?

The card should show enough reason/risk/missing-data context for first-pass review. Methodology must remain available for exact rules.

## Advanced Table Access

Keep a visible path to:

- full rankings table;
- compare;
- application list;
- dossiers;
- methodology.

The table is still valuable. It should no longer be the only first-pass way to understand the project.

## Empty And Edge States

Handle:

- no intake answers;
- no schools in a group;
- no local storage;
- all schools hidden;
- MD-only proof of concept with DO data present elsewhere;
- missing MCAT/GPA/cost fields.

No empty state should blame the user or imply the data is complete when it is not.

## Acceptance Criteria

- The first post-intake view is card/group based.
- A user can hide, restore, shortlist, compare, and open profiles from cards.
- Group labels and reason chips reflect intake context.
- Lower-priority groups start collapsed and can be expanded without changing school state.
- Advanced table access remains clear.
- Missing data remains visible.
- No card label implies school-specific acceptance odds.
