# Route And Navigation Contract

## Objective

Add a product-quality school browser route without breaking the existing profile route.

## Routes

Add:

```text
/schools/       School Browser
```

Keep:

```text
/schools/:slug/ School Profile
```

Astro route files:

```text
frontend/src/pages/schools/index.astro
frontend/src/pages/schools/[slug].astro
```

The new index route should render `ProductAppShell` with:

```text
initialPath="/schools/"
```

## App Route Type

Extend the app route resolver with a school-browser route.

Suggested route type:

```ts
type AppRoute =
  | { kind: "build" }
  | { kind: "schools" }
  | { kind: "interested" }
  | { kind: "applying" }
  | { kind: "notInterested" }
  | { kind: "compare" }
  | { kind: "scoring" }
  | { kind: "methodology" }
  | { kind: "school"; slug: string }
  | { kind: "notFound"; path: string };
```

## Navigation

Add a shell nav item:

```text
Schools -> /schools/
```

Order:

```text
Build My List
Schools
Interested
Applying
Not Interested
Compare
Scoring
Methodology
```

## Header Contract

School browser header:

```text
Eyebrow: Directory
H1: Schools
Body: Browse the full school universe, open profiles, and apply optional browser-local scoring overrides.
```

Include the existing score caveat in the route body or nearby helper copy.

## Compatibility

The route resolver must distinguish:

- `/schools/` as school browser;
- `/schools/:slug/` as school profile.

Base-path handling must work for:

```text
/med-school-ranker/schools/
/med-school-ranker/schools/:slug/
```

## Acceptance Criteria

- `/schools/` builds statically.
- `/schools/` is reachable from shell nav.
- `/schools/:slug/` direct URLs still build and hydrate.
- Shell click interception handles `/schools/` and `/schools/:slug/`.
- `/admin/` remains outside the shell.

