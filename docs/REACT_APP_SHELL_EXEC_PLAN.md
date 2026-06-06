# React App Shell Exec Plan

## Objective

Move the applicant-facing product experience into one persistent React app shell while keeping Astro static hosting.

The current site works, but each applicant route hydrates its own React island. That means browser-local preferences and derived scoring state can briefly reset or remount when moving between pages. The app shell should keep one mounted local-state layer across applicant-facing navigation.

## Product Intent

Keep the current proof-of-concept behavior and data model. Make the interaction model feel like a product app instead of separate spreadsheet-like pages.

The target outcome is:

- static Astro site still deploys to GitHub Pages and Vercel;
- no database, account system, or server persistence;
- one persistent browser-local state owner for applicant workflow routes;
- in-app navigation between applicant surfaces without full page reloads;
- direct URLs still work for applicant routes and school profiles;
- admin/data route remains separate from applicant workflow and hidden from normal applicant navigation.

## In Scope

- Add a React app shell for applicant-facing routes.
- Lift `useLocalSchoolState()` so it mounts once for the shell.
- Refactor existing React route components to accept a shared local-state object instead of each calling the hook independently.
- Add client-side route state using `history.pushState`, `popstate`, and base-path-safe URL helpers.
- Render Build My List, Interested, Applying, Not Interested, Compare, Scoring, Methodology, and school profile routes inside the shell.
- Preserve direct static routes by rendering the same app shell from existing Astro route files with an initial path.
- Keep `/admin/` as a separate Astro page, but remove it from visible applicant navigation in this slice.
- Deprecate `/recommendations/` as a normal product route. Build My List is the canonical recommendation/list-building route.
- Add Interested, Applying, Not Interested, and Compare actions to school profiles inside the app shell.
- Update smoke checks for the app shell.
- Preserve GitHub Pages base-path behavior.

## Out Of Scope

- No database.
- No accounts.
- No server-side applicant persistence.
- No predictive admissions model.
- No scoring formula changes.
- No source data changes or scraping.
- No visual redesign beyond shell/navigation changes required for the app shell.
- No removal of transparency/methodology caveats.
- No private applicant values committed to code, payloads, screenshots, or docs.

## Current Architecture Problem

Current applicant pages work like this:

1. Astro serves a page.
2. The page hydrates one React island.
3. That island calls `useLocalSchoolState()`.
4. The hook reads browser `localStorage` after mount.
5. Moving to another applicant page repeats the process.

This can create:

- menu value lag after navigation;
- brief default-state flashes;
- duplicated scoring/filter recomputation;
- interaction surfaces that feel like separate pages rather than one app.

## Target Architecture

Astro remains the static host.

React owns the applicant workflow:

```text
ProductLayout.astro
└── ProductAppShell client:load
    ├── app nav
    ├── route resolver
    ├── one useLocalSchoolState() instance
    ├── Build My List route
    ├── Interested route
    ├── Applying route
    ├── Not Interested route
    ├── Compare route
    ├── Scoring route
    ├── Methodology route
    └── School profile route
```

Each direct Astro route should render the same `ProductAppShell` with an `initialPath`:

```text
/
/interested/
/applying/
/not-interested/
/compare/
/scoring/
/methodology/
/schools/:slug/
```

`/admin/` should keep rendering `ProductLayout.astro` directly and should not be intercepted by the app shell.

`/recommendations/` should not appear in app-shell navigation. It may remain as a static compatibility/deprecation route that points users to Build My List, or it may render the Build My List shell route directly if that is simpler and does not duplicate product concepts. It should not become a second recommendation workflow.

## Required Files

Expected new files:

```text
frontend/src/components/ProductAppShell.tsx
frontend/src/components/AppMethodologyView.tsx
frontend/src/components/AppSchoolProfileView.tsx
frontend/src/lib/app-routing.ts
docs/site/react_app_shell/
```

Expected changed files:

```text
frontend/src/components/BuildMyListApp.tsx
frontend/src/components/RecommendationFeed.tsx
frontend/src/components/LocalListPage.tsx
frontend/src/components/CompareApp.tsx
frontend/src/components/ScoringAssumptionsApp.tsx
frontend/src/components/SchoolCard.tsx
frontend/src/components/useLocalSchoolState.ts
frontend/src/layouts/ProductLayout.astro
frontend/src/pages/index.astro
frontend/src/pages/interested.astro
frontend/src/pages/applying.astro
frontend/src/pages/not-interested.astro
frontend/src/pages/compare.astro
frontend/src/pages/scoring.astro
frontend/src/pages/methodology.astro
frontend/src/pages/schools/[slug].astro
frontend/src/styles/global.css
frontend/scripts/smoke-check.mjs
```

## Implementation Order

1. Add route utilities.
2. Add a typed local-state interface exported from `useLocalSchoolState.ts`.
3. Refactor route components to accept optional shared local state.
4. Add `ProductAppShell.tsx`.
5. Move applicant navigation into the shell or make top navigation shell-aware.
6. Convert existing applicant Astro pages to render the shell.
7. Add React methodology view.
8. Add React school profile view with local list action buttons.
9. Update internal links to use shell navigation for applicant routes.
10. Preserve direct URL behavior for all static routes.
11. Update smoke checks.
12. Run build, smoke, and local QA.

## Acceptance Criteria

- `npm run build` passes.
- `npm run smoke` passes.
- Direct URLs load correctly:
  - `/`
  - `/interested/`
  - `/applying/`
  - `/not-interested/`
  - `/compare/`
  - `/scoring/`
  - `/methodology/`
  - at least one `/schools/:slug/`
  - `/admin/`
- `/recommendations/` is absent from normal applicant navigation and does not duplicate Build My List as a second workflow.
- In-app navigation between applicant routes does not full reload.
- Browser back/forward works.
- Menu values remain stable when moving between applicant routes after browser-local state has updated from defaults.
- Interested/Applying/Not Interested/Compare state persists during app navigation.
- Scoring sliders and MCAT/GPA inputs update visible scoring outputs.
- School profile links open at the top of the profile route.
- School profile action buttons update the same local lists as cards.
- External school/source links still open as normal links.
- `/admin/` remains outside the shell and is not shown in normal applicant navigation.
- Build output remains static and GitHub Pages compatible.

## Non-Negotiable Claim Safety

The app shell must not introduce claims such as:

- guaranteed admission;
- safe school;
- best school;
- likely admitted;
- admission probability;
- school-specific admit chance.

Existing caveats must remain visible where scoring, MCAT/GPA fit, AAMC grid context, and rank movement are discussed.

## Completion Handoff

The implementation worker must report:

- branch name;
- commit hash;
- route files changed;
- component files changed;
- verification commands and results;
- whether browser back/forward was manually or automatically checked;
- whether GitHub Pages base path was checked;
- remaining limitations.
