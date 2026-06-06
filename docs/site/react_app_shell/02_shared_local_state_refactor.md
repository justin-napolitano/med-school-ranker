# Shared Local State Refactor

## Objective

Refactor applicant-facing React components so one `useLocalSchoolState()` instance can be shared across the shell.

## Current Problem

Several route components call `useLocalSchoolState()` internally. This causes state reads, localStorage normalization, and route-level recomputation to repeat on navigation.

## Required Contract

Export a local state type from:

```text
frontend/src/components/useLocalSchoolState.ts
```

Suggested type:

```ts
export type LocalSchoolState = ReturnType<typeof useLocalSchoolState>;
```

Route components should accept a `local` prop:

```ts
local?: LocalSchoolState;
```

During migration, components may still call `useLocalSchoolState()` only when no `local` prop is passed. This preserves standalone route component compatibility while letting the app shell pass shared state.

## Components To Refactor

```text
frontend/src/components/BuildMyListApp.tsx
frontend/src/components/RecommendationFeed.tsx
frontend/src/components/LocalListPage.tsx
frontend/src/components/CompareApp.tsx
frontend/src/components/ScoringAssumptionsApp.tsx
```

`SchoolCard.tsx` should not own local state. It should keep receiving action callbacks.

## State Readiness

Default preferences may render immediately on first load, then update from browser-local state.

Preferred behavior:

- the app shell mounts once;
- preferences load once from `localStorage`;
- routes use the same already-loaded state;
- first load should not block the page waiting for localStorage;
- after `local.ready` is true, route changes should not flash back to defaults.

Do not block the full page on localStorage forever. If localStorage is unavailable, defaults should work.

## Scoring Recompute Rules

Use `useMemo` at the route view level for:

- filtered school sets;
- scored school sets;
- selected local list school lookups;
- expensive derived rows.

Memo dependencies must include the specific state pieces used by the computation.

Do not memoize with incomplete dependencies just to silence recomputation.

## Acceptance Criteria

- There is one `useLocalSchoolState()` call inside `ProductAppShell` for applicant routes.
- Standalone route components still work if used directly during migration.
- Navigating among applicant routes does not reset menu values.
- First load can show defaults before saved browser state applies.
- Clicking controls still updates cards/tables.
