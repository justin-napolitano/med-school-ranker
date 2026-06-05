# Site Plan: Plans Page

## Objective

Expose the project execution plan index in the review site so planning and implementation status are visible alongside data review.

## Inputs

- `project_subplans.json`

## Primary Table

Columns:

- plan name
- plan type
- status
- priority
- phase
- owner
- reviewer
- current decision summary
- next action
- doc path

## Filters

- Status.
- Priority.
- Phase.
- Owner/reviewer.

## Interactions

- Click doc path to open local/GitHub doc link when hosted.
- Sort by priority and phase.

## Definition of Done

- All indexed plans appear.
- High-priority next actions are easy to identify.
- Site plans are included in the plan index once created.
