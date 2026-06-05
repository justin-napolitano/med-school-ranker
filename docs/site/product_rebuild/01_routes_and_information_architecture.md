# Routes and Information Architecture

## Objective

Restructure the site around applicant-facing value routes, with admin and build-health surfaces separated into an admin route family.

## Current Problem

The existing static site opens to a dashboard and mixes source/build/admin status with user-facing ranking and school-review workflows. That was acceptable for the baseline review site, but it is not the right default for a product-grade applicant experience.

## Route Requirements

Public routes:

```text
#/rankings
#/lists
#/lists/:list_slug
#/compare
#/schools/:school_slug
#/methodology
#/sources
```

Admin routes:

```text
#/admin
#/admin/sources
#/admin/data-quality
#/admin/build
```

Default behavior:

- Opening `outputs/site/index.html` should land on `#/rankings`.
- Unknown routes should fall back to rankings or a lightweight not-found page with links back to rankings and lists.
- Admin routes should not be shown as primary navigation in publish-safe mode.

## Navigation Model

Primary public navigation:

- Rankings
- Curated Lists
- Compare
- Methodology
- Sources

School profiles are reached from rankings, lists, compare, and source links rather than a giant nav menu.

Admin navigation:

- Admin Overview
- Source Review
- Data Quality
- Build Status

## Payload Requirements

Each school needs:

- stable `school_id`;
- generated `school_slug`;
- display name;
- degree;
- city/state;
- ranking row;
- admissions stats row;
- cost row;
- policy/LOR rows;
- derived flags and quality fields.

The route layer should not reimplement joins. It should consume a route-ready payload from the site builder.

## Implementation Steps

1. Add slug generation in the site builder.
2. Add `route` state driven by `window.location.hash`.
3. Replace tab-only view switching with hash-route rendering.
4. Set default hash to `#/rankings`.
5. Move dashboard/status/data-quality/source-review admin tables to `#/admin/*`.
6. Keep direct school/profile links stable across rebuilds.
7. Add route tests for default route, school route, list route, and admin route.

## Done Criteria

- `outputs/site/index.html` opens to rankings.
- Browser back/forward works across rankings, list, profile, and admin routes.
- Ranking rows and curated-list rows deep-link to school profiles.
- Admin routes are separated from public navigation.
- Publish-safe mode does not include admin route payloads.
