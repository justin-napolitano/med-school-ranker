# Visual Design and Reporting Quality

## Objective

Make the site feel like a credible, premium reporting product while staying dense, transparent, and useful for repeated school-review work.

The target is not a marketing landing page. The target is a polished research and ranking product.

## Design Principles

- First screen should provide utility immediately.
- Use data-dense layouts with strong hierarchy.
- Keep admin/status visuals separate from public product visuals.
- Use compact metric cards, badges, source panels, and tables.
- Avoid fake imagery and vague atmosphere.
- Use charts only when they clarify a decision.
- Keep source confidence visible.
- Treat missing data as a visible state, not a defect to hide.

## Product Visual System

Core UI elements:

- sticky route navigation;
- scoring lens segmented control;
- filter drawer or dense filter bar;
- sortable tables;
- source confidence badges;
- reason chips;
- shortlist controls;
- profile metric cards;
- compact comparison tables;
- risk flag panels;
- methodology callouts.

Color usage:

- neutral base;
- restrained accent for primary actions;
- green for strong/source-backed;
- amber for caution/missing/medium confidence;
- red for hard-no/error/high-risk;
- avoid one-note palettes.

Typography:

- clear hierarchy;
- compact table text;
- larger school/profile headings;
- no viewport-scaled type;
- no negative letter spacing.

## Reporting Quality

Every public-facing fact should be one of:

- source-backed;
- calculated from source-backed fields;
- explicit user/partner judgment;
- missing/unknown.

School profile pages should include:

- source and confidence context;
- methodology/caveat where the metric may be misunderstood;
- AAMC grid caveat for national aggregate MD data;
- no implied school-specific acceptance probability unless a future model is approved.

## Visual QA

Before considering the rebuild done:

- inspect desktop and mobile screenshots;
- verify rankings table does not overflow incoherently;
- verify profile cards do not overlap;
- verify filters are usable on mobile;
- verify admin routes remain usable but not prominent;
- verify publish-safe routes do not expose admin/private data.

## Implementation Steps

1. Define shared CSS tokens and components.
2. Rebuild rankings visual hierarchy.
3. Rebuild profile layout.
4. Add curated-list card/table templates.
5. Add admin-specific visual treatment.
6. Add screenshot/smoke checks.
7. Review source and methodology text for clarity.

## Done Criteria

- Rankings and profile pages feel polished enough to share.
- User-facing routes do not look like internal admin tooling.
- Tables are scannable and responsive.
- Source confidence is visible but not visually noisy.
- The site supports serious school selection work without requiring the workbook.
