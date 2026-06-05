# Validation, Privacy, and QA

## Objective

Protect the data-modeling work from three risks:

- node contracts drift from canonical data;
- publish-safe outputs leak admin/private/reviewer data;
- card surfaces imply confidence that the data does not support.

## Required Validation

Node generation tests should verify:

- every active school has a school node;
- every active school has a school card node;
- every active school has a school profile node;
- every ranking card references an existing school;
- every compare card references an existing school;
- list nodes reference existing schools;
- methodology nodes include AAMC caveat text;
- node schema versions are present;
- required fields are present;
- missing values render as missing or blank, not zero.

## Determinism

Repeated builds should produce stable node ordering:

- sort schools by `school_id` or `school_name`;
- sort card arrays deterministically;
- sort source refs deterministically;
- do not embed nondeterministic object key ordering beyond normal JSON serialization;
- keep generated timestamps at file metadata level where practical.

## Privacy Checks

Run after every node implementation:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

Publish-safe checks should verify:

- no admin node files;
- no reviewer-state node files;
- no private applicant fields;
- no private-derived ranking/card nodes;
- no source review queue detail;
- no local file paths.

## Visual QA After Node Adoption

When the UI starts consuming card nodes, capture desktop and mobile screenshots for:

- rankings;
- school card grid/list;
- school profile;
- compare;
- application list;
- admin overview;
- publish-safe output.

Check:

- no overlapping card text;
- card heights are stable enough for scanning;
- missing-data states are visible;
- source/confidence badges are clear;
- admin routes are not prominent in product mode.

## Required Commands

For implementation slices:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git diff --check
```

For site-serving slices:

```bash
curl -sI http://localhost:8766/
```

or start a local static server and report the URL.

## Done Criteria

- Node tests cover shape, counts, references, and publish-safe exclusions.
- Existing tests continue passing.
- Upload bundle privacy check reports `0`.
- Data quality validation reports no structural errors.
- Any remaining warnings are known data-completeness work, not model-shape failures.
