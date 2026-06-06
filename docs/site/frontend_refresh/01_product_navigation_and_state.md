# Product Navigation And State

## Objective

Make the route shell match the applicant workflow before deeper card and visual work.

## Desired Public Navigation

Primary public navigation:

- `Start`: `#/intake`
- `Rankings`: `#/rankings`
- `Schools`: `#/schools`
- `Applications`: `#/applications`
- `Methodology`: `#/methodology`

Secondary/local-admin navigation:

- `#/admin`
- `#/admin/sources`
- `#/admin/data-quality`
- `#/admin/plans`

In `publish_safe`, admin routes remain unavailable and omitted from the public route metadata.

## Required Behavior

- Unknown routes fall back to the applicant start route or rankings.
- Navigation labels avoid internal terms like payload, node, dossier, CSV, or source queue.
- Admin/build/source-health views are not first-class public navigation items.
- Current browser-local state remains compatible:
  - intake answers;
  - school status;
  - visibility/hide state;
  - compare selections;
  - score-card review fields.
- Deep links to existing school routes continue to open at the top of the page.

## Implementation Notes

- Prefer route aliases over deleting old routes.
- Keep old hash paths working when possible.
- Keep `DEFAULT_ROUTE` aligned with the applicant workflow.
- Avoid broad CSS redesign in this slice.

## Done Criteria

- Public nav reads like an applicant product, not an admin console.
- Existing rankings, school profile, application list, compare, and methodology routes still render.
- `publish_safe` has no admin route metadata.
- Tests cover default route and route fallback behavior.

