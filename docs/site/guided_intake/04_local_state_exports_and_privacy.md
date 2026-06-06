# Local State, Exports, and Privacy

## Purpose

Define how guided intake answers are stored, exported, imported, and kept out of public artifacts.

## Local Storage

Use a versioned key:

```text
med_school_ranker_intake_v1
```

Store:

- schema version;
- answers;
- derived context snapshot;
- updated timestamp.

The app must recover from:

- missing local storage;
- invalid JSON;
- old schema version;
- user clearing browser state.

## Export

Support a user-triggered JSON export in the first slice. CSV can be added later if needed.

The export should include:

- answer IDs;
- answer values;
- display labels;
- derived context summary;
- timestamp;
- schema version.

Do not auto-download or auto-upload.

## Import

Import can be implemented in a later slice if needed. If included now, it must validate schema version and controlled values before applying answers.

If import is not implemented, the UI should not show a disabled or decorative import control.

## Publish-Safe Privacy

Generated public artifacts must not include real private applicant answers.

Allowed in generated source:

- question schema;
- default options;
- public methodology text;
- generic example copy.

Not allowed:

- real saved intake answers;
- private local exports;
- partner-specific notes;
- private profile values not already approved for public-safe generated output.

## Automated Privacy Assertions

Implementation tests or smoke checks should assert:

- `site_payload.json` does not contain saved intake answer values;
- `med-school-ranker-upload.zip` contains no private path entries;
- local export files are not generated automatically by build commands;
- generated example/default answer values cannot be mistaken for real saved answers.

## Relationship To Existing Local Workflows

Guided intake state should coexist with:

- visibility state;
- shortlist/application-list state;
- compare state;
- dossier edits;
- research queue exports.

Do not break existing local storage keys.

## Acceptance Criteria

- Intake state is local-only by default.
- Export is explicit.
- Publish-safe output contains no saved intake answers.
- Existing local workflows keep working.
- Privacy checks include the upload zip and generated site payload.
