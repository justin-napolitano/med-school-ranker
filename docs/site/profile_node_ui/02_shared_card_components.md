# Shared Card Components

## Objective

Add simple reusable rendering helpers so profile pages and later card surfaces render node-shaped data consistently.

## Component Targets

- card shell;
- compact metric card;
- fact row/list;
- readiness/status chip;
- rank/confidence chip;
- missing-fields block;
- source/caveat block;
- profile section block.

## Implementation Guidance

- Keep the current static site architecture.
- Prefer small functions over a framework migration.
- Use existing CSS tokens/classes where possible.
- Add only minimal CSS needed for readable sections.
- Keep cards dense and utilitarian. This is still an admin/workbench UI until a design pass happens.

## Required Behaviors

- Missing values render as missing, not zero.
- Partial sections remain visible.
- Source caveats remain visible near facts they qualify.
- Action buttons keep using stable `school_id`.
- Publish-safe mode does not render admin-only values.

## Done Criteria

- Profile rendering uses shared helpers rather than one-off markup for each section.
- The helper API accepts node-shaped inputs.
- The next design pass can style the helpers without changing data access patterns.

