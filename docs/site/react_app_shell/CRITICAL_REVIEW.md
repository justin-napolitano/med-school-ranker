# Critical Review

## Summary

The React app shell is a good next step because it addresses route-level remounting without requiring a backend. The main risks are routing/base-path regressions, accidentally losing current route features, and weakening claim-safety smoke checks.

## Critical Findings To Guard Against

### 1. Shell Navigation Can Break GitHub Pages Base Paths

Risk: React route links may accidentally use root-relative paths that work locally but fail under `/med-school-ranker/`.

Mitigation:

- centralize route generation in `frontend/src/lib/app-routing.ts`;
- use `withBase()` or equivalent for all hrefs;
- run base-path build/smoke when practical.

### 2. Direct URLs Must Still Work

Risk: a pure client-only route could work from `/` but fail on hard refresh for `/interested/` or `/schools/:slug/`.

Mitigation:

- keep static Astro wrappers for existing direct routes;
- render the app shell from every applicant route with an `initialPath`;
- keep static school profile pages generated.

### 3. Multiple Local State Owners Would Defeat The Purpose

Risk: route components continue calling `useLocalSchoolState()` internally even inside the shell.

Mitigation:

- export `LocalSchoolState`;
- pass shared local state from `ProductAppShell`;
- allow fallback hook calls only for standalone compatibility;
- inspect final code for route-owned hook calls.

### 4. Static Top Nav Could Fight Shell Nav

Risk: ProductLayout nav stays active based on initial page and causes full reloads or stale active states.

Mitigation:

- prefer React-owned app nav on shell pages;
- keep `/admin/` as a direct route, but hide it from normal applicant navigation;
- hide static nav on shell pages or make it explicitly non-authoritative.

### 5. School Profile Links Could Scroll Poorly

Risk: profile links preserve prior scroll position or open below the top.

Mitigation:

- shell navigation should call `window.scrollTo(0, 0)` on route changes;
- avoid scroll-to-top on filter/control-only updates.

### 6. Methodology Could Lose Important Caveats

Risk: migrating methodology from Astro to React drops the missing-data, zero-weight, DO-scope, or privacy explanations.

Mitigation:

- copy existing methodology content into `AppMethodologyView`;
- smoke check for required phrases.

### 7. App Shell Does Not Solve First Load

Risk: expectations drift toward instant first render even though payload size remains large.

Mitigation:

- document that app shell improves route changes and state remounts, not initial payload cost;
- consider payload splitting later if first load becomes a major issue.

### 8. Browser Automation May Be Unavailable

Risk: headless Chrome may fail in local sandbox, leaving click behavior unverified.

Mitigation:

- keep smoke checks strong;
- manually review local dev server;
- report browser automation failure explicitly instead of pretending coverage exists.

## Decision Points Already Resolved

- No database in this slice.
- No accounts in this slice.
- Static Astro hosting remains.
- `/admin/` remains separate and hidden from normal applicant navigation.
- Applicant routes move into the shell.
- Direct URLs must keep working.
- Use real paths, not hash-only routing.
- `/recommendations/` is deprecated as a product workflow; Build My List is canonical.
- First load can render defaults and then update from browser-local state.
- School profiles should include Interested, Applying, Not Interested, and Compare actions.

## Remaining Questions For User

No product-blocking questions remain for the first app-shell implementation pass.
