# Admin Separation and Publish-Safe Mode

## Objective

Separate admin/build/source-health workflows from applicant-facing product routes and add a publish-safe site mode that omits private/admin data.

## Admin Routes

```text
#/admin
#/admin/sources
#/admin/data-quality
#/admin/build
```

Admin overview should show:

- build timestamp;
- active school count;
- source table count;
- raw AAMC file count;
- admissions stats coverage;
- cost coverage;
- open source reviews;
- data quality counts;
- payload row counts.

Source admin should show:

- source-review queue;
- source conflicts;
- tuition candidate/review rows;
- LOR/policy parse coverage;
- manual overrides.

Data quality admin should show:

- validation issues;
- errors/warnings/info;
- affected file/row/field;
- suggested fixes.

Build admin should show:

- generated files;
- site payload counts;
- workbook/zip status;
- publish-safe/private-data checks.

## Privacy Modes

### `local_full`

Use for local review.

May include:

- admin routes;
- applicant profile template;
- partner inputs;
- source review queues;
- data quality report;
- build status.

Must still exclude:

- `data/manual/private`;
- `data/private`;
- any real private applicant data not explicitly approved.

### `publish_safe`

Use before GitHub Pages or public sharing.

Must exclude:

- admin routes;
- partner inputs;
- private applicant data;
- source review queues if they contain local notes;
- build/internal file paths unless intentionally public;
- data/manual/private and data/private.

Can include:

- public rankings;
- school profiles;
- curated lists;
- methodology;
- public source summaries;
- source names and URLs that are safe to publish.

## Phase 0 Scaffold

Publish-safe scaffolding should be created before the full product UI is rebuilt:

- Define payload groups as `product_public`, `product_local`, and `admin_local`.
- Generate `local_full` from all non-private allowed groups.
- Generate `publish_safe` only from `product_public`.
- Add a simple mode indicator to generated metadata.
- Add exclusion tests before any public deployment work.

This prevents later route work from accidentally treating hidden admin views as safe.

## Implementation Steps

1. Add site mode argument or environment setting.
2. Split payload into product-safe and admin-local sections.
3. In `publish_safe`, generate only product-safe payload.
4. Move dashboard/status/admin tables under admin routes.
5. Add tests that publish-safe output does not contain private/admin strings.
6. Add README command examples.

## Done Criteria

- `local_full` has admin routes and local review data.
- `publish_safe` omits admin routes and private/local payloads.
- Admin data is not merely hidden in CSS or navigation.
- Tests verify private/admin data exclusion.
- Public routes still render in publish-safe mode.
