# Critical Review

## Findings To Address Before Build

1. Per-school weights can make ranking less comparable.

Mitigation:

- keep `Global Score` visible;
- label `Adjusted Score`;
- show `Override applied`;
- avoid silently reordering Build My List.

2. `/schools/` can collide conceptually with `/schools/:slug/`.

Mitigation:

- route resolver must explicitly handle `/schools/` before `/schools/:slug/`;
- Astro should use `pages/schools/index.astro` plus existing `[slug].astro`;
- smoke checks must cover both direct URLs.

3. A directory showing all schools can overwhelm users.

Mitigation:

- use a compact card grid;
- add text search, state filter, degree filter, status filter, and sort;
- support load-more or pagination if the full grid feels heavy.

4. Override editor could become too much UI on every card.

Mitigation:

- cards show a button and summary;
- editor can open as a focused inline details panel or modal;
- compare cards should not include full editors in the first slice.

5. Local override data can be mistaken for shared application data.

Mitigation:

- use clear browser-local copy;
- avoid implying server sync or account storage;
- do not put override data in URLs or payload files.

6. Adjusted-score sorting can confuse users.

Mitigation:

- default to global sorting;
- make adjusted sorting an explicit sort option;
- show an `Adjusted sort` indicator when active.

7. The profile payload is already large.

Mitigation:

- avoid adding more serialized payload fields;
- derive override state in the client from local storage;
- keep first implementation local and deterministic.

8. Claim safety can regress when adding adjusted score language.

Mitigation:

- reuse existing caveat;
- update smoke checks for unsafe phrases;
- avoid words such as likely, safe, guaranteed, or probability unless caveated as not being used.

## Open Product Decisions

These decisions are safe to default for the first build:

- Default sort should remain global rank/global score.
- Per-school override editor should start as an inline panel or lightweight modal.
- Override state should be local-storage only.
- Build My List should not silently reorder from per-school overrides in the first slice.

## Recommended First Build

Build the route and override model conservatively:

- `/schools/` directory;
- cards with status/actions/profile links;
- per-school override editor;
- adjusted score display;
- reset controls;
- profile visibility;
- smoke and browser QA.

Leave richer export/import and adjusted Build My List ranking toggles for a later pass.

