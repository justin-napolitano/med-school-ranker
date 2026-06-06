# Performance And Loading UX

## Objective

Reduce perceived delay without hiding real data state or adding misleading loading behavior.

## First Load

The school payload is large. The app shell does not eliminate first-load cost.

Required behavior:

- show meaningful page structure quickly;
- render default preferences immediately if needed;
- update from browser-local preferences as soon as localStorage has loaded;
- avoid showing default preferences again after localStorage has loaded and the user navigates inside the shell;
- avoid large blocking synchronous work before first visible render when practical.

## Navigation

Applicant route changes should be cheap because:

- payload is already in memory;
- local state is already mounted;
- route components receive shared local state;
- history changes do not reload the document.

## Recompute Strategy

Use focused `useMemo` for expensive derivations:

- filtered school arrays;
- score arrays;
- local selected-school lookups;
- movement rows.

Do not memoize source data normalization in components if it is already done in `loadProductPayload()`.

## Avoid Debounce As Default

Do not debounce all controls globally.

Reason:

- debouncing can make sliders, selects, and buttons feel less responsive;
- the main issue is remount/reload and broad synchronous recomputation, not uncontrolled rapid typing.

Use deferred updates only if a specific text input creates visible typing lag. If used, document it.

## Loading State

If `local.ready` is false on first load:

- it is acceptable to render defaults immediately;
- saved browser preferences should update the shell as soon as they are available;
- do not block the whole route with a loading state only for localStorage.

Do not add marketing or instructional text.

## Runtime Safety

The shell should be resilient to:

- missing localStorage;
- malformed localStorage;
- unknown route path;
- deleted school slug;
- unavailable source URL;
- empty selected local lists.

## Acceptance Criteria

- Page-to-page menu values feel stable.
- First load can render defaults and then update once.
- Control clicks update visible state without page reload.
- Initial load remains static-site compatible.
