# School Card Grid And Search

## Objective

Create a school browser view that shows the complete school universe as approachable cards.

This route should be easier to browse than the ranked list. It should feel like a directory with decision context, not a spreadsheet.

## Component

Add:

```text
frontend/src/components/SchoolBrowserView.tsx
```

Props:

```ts
type SchoolBrowserViewProps = {
  schools: ProductSchool[];
  caveat: string;
  local: LocalSchoolState;
};
```

## Card Content

Each card should show:

- school name;
- degree;
- city and state;
- global score or global rank context;
- adjusted score if override exists;
- MCAT/GPA when present;
- in-state and out-of-state cost when present;
- status chip: None, Interested, Applying, Not Interested, Compared;
- override chip when applied;
- profile link;
- action buttons: Interested, Applying, Compare, Not Interested;
- override button.

Avoid dense table-like card bodies.

## Search And Filters

Minimum first slice:

- text search across school name, city, and state;
- degree filter: MD, DO, all;
- state filter;
- status filter;
- override filter: all, override applied, no override;
- sort by school name, global rank, global score, adjusted score.

Default view:

```text
All schools, sorted by global rank/global score when available.
```

## All Schools Rule

The route should show the full payload universe by default.

Not Interested schools should remain visible here because this is the directory. They should be visually labeled, not removed.

Build My List can remain a filtered/ranked working surface. Schools is the complete browsing surface.

## Layout

Desktop:

- left utility rail for search, filters, sort;
- right responsive card grid.

Mobile:

- filters stack above the cards;
- cards one column;
- no text overflow;
- action buttons wrap cleanly.

## Empty States

If filters return no schools:

- show a concise empty state;
- offer a clear `Reset filters` button.

## Acceptance Criteria

- User can find a school by name, city, or state.
- User can open a profile from any card.
- User can apply list actions from any card.
- Not Interested schools are visible with status labels.
- Cards do not overflow on mobile.
- Search/filter state can be browser-local or component-local; it does not need to persist in this slice.

