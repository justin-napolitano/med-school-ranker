# Rankings and Compare Preview

## Objective

Use generated card nodes in one bounded visible surface without broad-rebuilding rankings, compare, or list-builder workflows.

## Candidate Surfaces

Choose one implementation target:

- profile snapshot cards;
- rankings expanded preview cards;
- compare panel summary cards;
- application-list school summary cards.

Prefer the smallest surface that proves the card contract.

## Guardrails

- Do not rebuild all tables in this slice.
- Do not change rank semantics.
- Do not remove current filters or sorting.
- Do not replace working local browser controls.
- Do not hide data-quality or source caveats.

## Done Criteria

- At least one visible UI surface consumes generated card/ranking/compare nodes.
- Existing rankings and compare workflows remain stable.
- The implementation demonstrates how later card grids can consume the same node families.

