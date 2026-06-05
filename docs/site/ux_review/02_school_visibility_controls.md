# School Visibility Controls

## Objective

Let users remove schools from their current working view without deleting them or losing transparency.

This solves the practical workflow problem: once a school is clearly not relevant, the applicant should not have to keep seeing it in the main table.

## Product Rules

- Hiding is reversible.
- Hiding is in-memory browser state in the first pass.
- Hiding is not the same as hard-no or source exclusion.
- Hidden schools remain in the full universe.
- Hidden decisions can be exported as CSV.
- A hidden count should be visible.
- Users should be able to review and restore hidden schools.
- Persistent storage is future scope unless a privacy label and clear/reset control are implemented.

## Controls

Rankings row actions:

- hide from current view;
- restore if hidden;
- mark hard-no if supported by existing data;
- open dossier.

Global filters:

- visible only;
- all schools;
- hidden only;
- hard-no;
- shortlisted/research candidates if available.

## Suggested State Fields

Browser-local/export fields:

```text
school_id
school_name
export_schema_version
exported_at
visibility_state
visibility_reason
hidden_at
updated_at
source
notes
```

Controlled `visibility_state` values:

- `visible`
- `hidden`
- `hard_no`
- `shortlist`
- `research`
- `applied`

For the first pass, implement `visible` and `hidden`; other values can be displayed as future states if already present in data.

## CSV Export

Export file:

```text
school_visibility_export.csv
```

The export should include every school with non-default visibility state.

Required export schema version:

```text
export_schema_version = site_visibility_v1
```

## Done Criteria

- User can hide a school from the working view.
- User can restore a hidden school.
- Hidden schools are reviewable.
- Hidden state survives while the page is open.
- Hidden state can be exported.
- Full universe is still accessible.
