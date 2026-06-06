# QA and Accessibility

## Purpose

Verify the site is readable, stable, and keyboard/browser friendly after text and layout changes.

## Required Checks

- Run unit tests.
- Run project validation.
- Rebuild generated site outputs.
- Run screenshot QA when browser tooling is available.
- Manually or automatically verify key route interactions:
  - clicking a school score-card link opens at top;
  - intake left pane scrolls independently;
  - state-exclude checkbox changes do not jump the left pane;
  - mobile card text wraps cleanly;
  - compare cards stay inside columns.

## Accessibility Notes

- Full labels improve screen-reader clarity and reduce acronym ambiguity.
- Buttons and links should keep clear visible text.
- Missing values should remain explicit.
- Focus behavior should not be disrupted by same-route rerenders.

## Known Follow-Up

Missing MCAT/GPA coverage requires a separate data coverage plan. This formatting plan should make missingness visible, not solve the source coverage problem.

