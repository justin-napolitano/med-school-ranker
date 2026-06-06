# School Card System

## Objective

Create a reusable applicant-facing school card that can power rankings, schools, intake results, applications, and compare previews.

## Card Requirements

Each school card should show, without requiring a table:

- school name and degree;
- location with city/state;
- decision rank or rank status;
- MCAT/GPA fit context when available;
- in-state and out-of-state cost labels when available;
- top reasons it appears in the current view;
- risks or caveats;
- missing or low-confidence data;
- current local status: None, Interested, Applying;
- actions: Interested, Applying, None, Compare, Open Score Card.

## Layout Rules

- Cards must not overflow text on mobile or desktop.
- Avoid nested cards.
- Use compact metric groups instead of long columns.
- Use chips for fit/confidence/reason labels.
- Collapse raw/source detail behind a small disclosure.
- Use full labels for user-facing fields:
  - `Out-of-state cost`, not `OOS Cost`;
  - `In-state cost`, not `IS Cost`;
  - `Total cost of attendance`, not `COA`.

## Data Rules

- Use generated card/profile/ranking nodes when available.
- Do not reimplement joins in frontend code if the node builder can supply the field.
- Missing values render as `Missing`, not `0`.
- Source confidence remains visible when it affects trust.

## Done Criteria

- One shared renderer or renderer family is used by at least two surfaces.
- Cards render in desktop and mobile without overflow.
- Status actions work consistently from cards.
- Existing table views still work.

