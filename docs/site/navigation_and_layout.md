# Site Plan: Navigation and Layout

## Objective

Define the shell, navigation, and shared layout for the static review site.

## Scope

This plan covers top-level menu items, global search, filter placement, responsive layout, and shared UI regions.

## Inputs

- Generated JSON data files in `outputs/site/data/`.
- Site page configuration.

## Menu Items

Primary navigation:

- Dashboard, default first screen
- Rankings, highest-priority table view
- School Detail
- Partner Review
- Admissions Sources
- Data Quality
- Plans

Secondary controls:

- Global search box
- Degree filter: All, MD, DO
- State filter
- Setting filter: urban, suburban, rural, unknown
- Data quality severity filter
- Hard-no filter

## Layout

Desktop layout:

- Top app bar with project name, build timestamp, and global search.
- Left or top navigation with menu items.
- Main content region.
- Optional right-side detail drawer for selected school.

Mobile layout:

- Top app bar.
- Collapsible menu.
- Full-width stacked filters.
- Tables remain horizontally scrollable if needed.

## Interactions

- Menu switches views without page reload where practical.
- Global search filters school-centric pages.
- Table row click opens school detail.
- URL hash or query params may preserve current view/filter in a later pass.
- School comparison is not part of the first implementation pass.

## Non-Goals

- No user accounts.
- No writeback to CSV.
- No external API calls.
- No private applicant data.

## Definition of Done

- Every primary menu item routes to a visible view.
- Dashboard is the default/home view.
- Global search filters relevant tables.
- Selected school can be inspected from school-centric tables.
- Layout works at desktop and mobile widths without overlapping controls.
