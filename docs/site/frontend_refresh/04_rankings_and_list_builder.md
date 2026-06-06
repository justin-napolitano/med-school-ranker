# Rankings And List Builder

## Objective

Turn Rankings and Applications into a simple decision queue.

The user should be able to move schools between `None`, `Interested`, and `Applying` without understanding old shortlist buckets.

## Current Product Rules

- `Interested` limit: 50 schools.
- `Applying` limit: 25 schools.
- Show a hard warning when a limit is reached.
- Do not silently add beyond the limit.
- User must remove a school before adding another over the limit.
- Hidden or hard-no schools should sit at the bottom and be collapsed by default.

## Rankings Route

Rankings should show:

- intake menu/selector on the side when space allows;
- card-first results or compact rows with expandable cards;
- status chip: None, Interested, Applying;
- actions: Interested, Applying, None, Open Score Card;
- `Why this rank?` as a compact disclosure;
- advanced table mode available.

Avoid:

- showing too many score internals in the default view;
- duplicate partner/local columns;
- legacy action labels that imply more workflow states than the user needs right now.

## Applications Route

Applications should show:

- Applying list first;
- Interested list second;
- counts against limits;
- empty states with clear next action;
- export controls;
- score-card links.

## Done Criteria

- A user can build a 25-school application list from rankings cards.
- Limit warnings are visible and blocking.
- Status is easy to change from every relevant surface.
- Existing local export schemas remain compatible or are versioned.

