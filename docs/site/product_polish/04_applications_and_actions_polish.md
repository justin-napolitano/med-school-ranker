# Applications And Actions Polish

## Objective

Make status actions and the application list feel simple, bounded, and trustworthy.

The workflow states are already decided:

- `None`
- `Interested`
- `Applying`

Do not add more states in this phase.

## In Scope

- Improve button hierarchy and labels.
- Make status chips consistent across intake, rankings, cards, score cards, and applications.
- Make limits visually obvious:
  - 50 Interested;
  - 25 Applying.
- Improve over-limit warnings.
- Improve empty states.
- Improve export/download control placement.
- Remove visible manual Hide buttons from product card/action areas.

## Behavior Rules

- Over-limit additions stay blocked.
- Warning copy tells the user what to remove.
- Status changes should be reversible.
- Hidden/hard-no schools should not disappear permanently.
- Hidden schools can still be restored from hidden-review contexts, but routine cards should not present Hide as a primary action.

## Done Criteria

- The user can understand list status at a glance.
- Limits are visible before and when reached.
- Application route feels like a working list, not a filtered table.
- Product card actions are limited to the current list/status workflow plus compare/open actions.
- Export controls remain available but not visually dominant.
