# Architecture And Route Contract

## Objective

Define the static Astro plus persistent React shell architecture.

## Route Set

Applicant routes in the shell:

```text
/                         Build My List
/interested/              Interested local list
/applying/                Applying local list
/not-interested/          Not Interested local list
/compare/                 Compare selected schools
/scoring/                 Scoring assumptions workspace
/methodology/             Methodology and claim-safety explanation
/schools/:slug/           School profile
```

Non-shell route:

```text
/admin/                   Admin/Data static route
```

Deprecated compatibility route:

```text
/recommendations/         Not a primary route; points to or aliases Build My List
```

Build My List is the canonical recommendation/list-building route.

## App Shell Component

Add:

```text
frontend/src/components/ProductAppShell.tsx
```

Required props:

```ts
type ProductAppShellProps = {
  schools: ProductSchool[];
  caveat: string;
  aamcCaveat: string;
  methodology: Array<Record<string, any>>;
  initialPath: string;
};
```

The shell should:

- own `useLocalSchoolState()`;
- own current route state;
- resolve current path to a route;
- render the page header for each route;
- render one route body at a time;
- expose a link/navigation helper to child components where needed;
- keep admin links as normal page loads;
- omit Admin/Data from normal applicant navigation.

## Route Resolver

Add:

```text
frontend/src/lib/app-routing.ts
```

Responsibilities:

- normalize paths with and without `import.meta.env.BASE_URL`;
- preserve trailing slash expectations;
- detect shell route type;
- parse school slugs;
- generate base-path-safe hrefs;
- identify external URLs;
- identify admin URLs that should not be intercepted;
- identify deprecated `/recommendations/` URLs and route them to Build My List or a deprecation view that clearly points to Build My List.

Suggested route type:

```ts
type AppRoute =
  | { kind: "build" }
  | { kind: "interested" }
  | { kind: "applying" }
  | { kind: "notInterested" }
  | { kind: "compare" }
  | { kind: "scoring" }
  | { kind: "methodology" }
  | { kind: "school"; slug: string }
  | { kind: "notFound"; path: string };
```

## Direct URL Strategy

Existing Astro page files should render the same `ProductAppShell` with the route's initial path.

Do not rely only on client-side hash routing. Direct static URLs should keep working.

## App Navigation Strategy

Use real paths and the History API:

- `history.pushState` for in-app route changes;
- `popstate` for back/forward;
- document-level or shell-level click interception for internal applicant links;
- no interception for external links, modified clicks, download links, target links, source links, or `/admin/`.
- no visible applicant nav item for `/admin/`.

## Not Found Behavior

For unknown shell paths:

- show a small empty state inside the shell;
- link back to Build My List;
- do not make unsupported route claims.

## Acceptance Criteria

- One React island remains mounted during shell navigation.
- Route changes update visible route content and active nav state.
- Direct URLs still build as static pages.
- Admin route stays separate.
- Recommendations is deprecated as a separate route and does not duplicate Build My List.
