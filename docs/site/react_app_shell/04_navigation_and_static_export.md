# Navigation And Static Export

## Objective

Keep static hosting compatibility while making applicant navigation feel instant.

## Astro Route Wrappers

Each applicant Astro page should render only:

- `ProductLayout`;
- a `ProductAppShell client:load`;
- route-specific `initialPath`.

Example:

```astro
<ProductLayout title="Interested / Applicant List" active="/interested/" shellNav={false}>
  <ProductAppShell client:load initialPath="/interested/" schools={payload.schools} caveat={caveat} ... />
</ProductLayout>
```

The exact prop name for hiding static nav can differ, but the static top nav should not fight the React shell nav.

## Layout Navigation

Two acceptable approaches:

1. Hide static `ProductLayout` nav for shell pages and render app nav inside React.
2. Keep static nav visible but intercept clicks from the app shell.

Preferred approach: render app nav inside React for shell pages.

Reason:

- active state updates without reload;
- shell can decide what to intercept;
- admin can stay out of normal applicant navigation;
- fewer stale active-link states.

Admin/Data should not appear as a normal applicant nav item in this slice. Direct `/admin/` access should still work.

`/recommendations/` should not appear as a nav item. Build My List is the canonical recommendation/list-building route.

## Base Path

All generated links must respect `ASTRO_BASE_PATH`.

Use existing `withBase()` or route utilities that wrap it. Do not hand-build root-relative paths in React components.

GitHub Pages deployment under `/med-school-ranker/` must not produce unprefixed links like:

```text
href="/interested/"
component-url="/src/..."
```

Smoke check already includes base-path assertions for build output. Extend it if new shell output changes the pattern.

## Link Interception Rules

Intercept only plain left-clicks on same-origin applicant links.

Do not intercept:

- `target="_blank"`;
- external URLs;
- source URLs;
- `mailto:`;
- `download`;
- modified clicks with cmd/ctrl/shift/alt;
- `/admin/`;
- visible `/recommendations/` workflow duplication;
- hash-only anchors unless intentionally handled.

## Back/Forward

The shell must listen for `popstate` and resolve the new path.

Back/forward should:

- update route content;
- preserve local state;
- preserve active nav state;
- not duplicate history entries.

## Scroll Behavior

On shell navigation:

- scroll to top for route changes;
- scroll to top for school profile links;
- do not scroll unexpectedly when a control changes filters or state.

## Static Export

Keep `output: "static"`.

Do not add server adapters, SSR-only APIs, or database calls.

## Acceptance Criteria

- GitHub Pages and Vercel static hosting remain viable.
- Direct URLs are available as static files.
- In-app route changes are History API changes, not full reloads.
- Admin/Data is hidden from normal applicant navigation.
