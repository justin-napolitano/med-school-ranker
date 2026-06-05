# Site Plan: Tables and Filters

## Objective

Define shared table behavior so all site pages feel consistent and are practical for dense review.

## Scope

Applies to:

- Dashboard tables
- Rankings table
- Partner review table
- Admissions source queue
- Data quality report
- Plans table

## Shared Table Behavior

- Sticky header when scrolling.
- Compact row height.
- Search within visible table.
- Sort by clicking column headers.
- Clear empty state.
- Show count of visible rows.
- Preserve unscored/missing values as blank or `Missing`, not zero.

## Shared Filters

Common filters:

- search text
- degree type
- state
- severity
- hard-no flag
- missing data flag

Filter behavior:

- Filters combine with AND logic.
- Each filter has a clear/reset control.
- Active filters are visible.

## Badges

Suggested badges:

- `MD`
- `DO`
- `Unscored`
- `Hard No`
- `Needs Source`
- `Warning`
- `Error`
- `Partner Missing`

## Accessibility and Usability

- Text must not overflow controls.
- Buttons and filters need visible labels.
- Color cannot be the only severity signal.
- Tables must remain usable on laptop-width screens.

## Definition of Done

- All tables share consistent filter/sort behavior.
- Missing data is visible but not misleading.
- Badges are consistent across pages.
- No table requires horizontal scrolling for the most important columns on desktop.
