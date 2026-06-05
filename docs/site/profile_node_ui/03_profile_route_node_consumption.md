# Profile Route Node Consumption

## Objective

Make `#/schools/:school_slug` render its main profile sections from `school_profile_nodes`.

## Route Contract

The primary render path should be:

```text
route slug -> school_profile_node -> section blocks -> cards/facts/caveats
```

Fallback to existing payload rows is allowed only for defensive compatibility and should not become the normal path.

## Required Sections

First pass:

- overview;
- applicant fit;
- admissions stats;
- cost and debt;
- requirements and policies;
- source confidence;
- methodology;
- reviewer state in `local_full` only.

Future sections can remain placeholders:

- curriculum;
- match outcomes;
- location context;
- student life;
- hidden curriculum;
- specialty optionality.

## Compatibility Requirements

Preserve:

- direct links to school routes;
- rankings/profile navigation;
- compare actions;
- application-list and shortlist controls;
- visibility controls;
- browser-local dossier edits and exports;
- source/methodology caveats;
- publish-safe rendering.

## Done Criteria

- Every active school has a node-backed profile route.
- Missing sections render clearly.
- Existing local review workflows still work from the profile page.
- Profile route tests or smoke checks cover at least one complete and one partial school profile.

