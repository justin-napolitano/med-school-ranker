# Local Storage, Export, Reset, And Privacy

## Objective

Keep school-specific overrides private, recoverable, and easy to reset.

## Local Storage

Use a versioned key:

```text
med-school-ranker:school-weight-overrides:v1
```

Keep the state browser-local.

Do not write overrides into:

- generated payloads;
- static JSON assets;
- repo files;
- URL query strings.

## Reset Controls

Support:

- reset one school to global weights;
- reset all school overrides.

Reset all should require a simple confirmation because it can remove several manual decisions.

## Export

Export is useful but can be second-pass.

If included in this slice, export a local JSON or CSV file with:

```text
school_slug
school_name
mcat_weight
gpa_weight
state_weight
cost_weight
context_weight
updated_at
```

Do not include private MCAT/GPA applicant inputs in the school-override export unless the user explicitly chooses a broader full-settings export in a later slice.

## Import

Import is out of scope for the first implementation.

## Privacy Copy

Use:

```text
Overrides are stored in this browser only.
```

Avoid vague claims like:

```text
secure
encrypted
private forever
```

The static site cannot guarantee those claims.

## Acceptance Criteria

- Overrides survive refresh.
- Reset one school works.
- Reset all works.
- No override data appears in built static payload files.
- Privacy copy is accurate and modest.

