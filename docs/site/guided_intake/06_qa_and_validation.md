# QA and Validation

## Purpose

Define verification for the guided intake slice.

## Required Checks

Run:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git diff --check
```

Run upload-bundle privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
```

Check ignored private paths:

```bash
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

## Test Coverage

Add tests for:

- generated HTML includes `#/intake` route support;
- intake schema has stable IDs and controlled values;
- answer mapping is deterministic;
- empty/corrupt local storage fallback exists;
- publish-safe output excludes saved answers;
- existing profile/rankings routes still render;
- upload bundle excludes private paths.
- applicant-facing copy does not include probability-implying labels such as `Safe`, `Likely Admit`, or `Chance`.

## Browser QA

If the screenshot script and dependencies are already present, capture:

- intake desktop;
- intake mobile;
- guided results desktop;
- guided results mobile;
- school card expanded state;
- advanced table link/state.

Do not install browser dependencies unless the user approves it.

## Manual Review Checklist

- Can a non-technical user complete intake without understanding weights?
- Does the result explain why schools appear?
- Are exclusions reversible?
- Are missing data and low confidence visible?
- Can the user still reach advanced tables?
- Does mobile feel like a first-class path?
- Does any label overstate what the deterministic data can prove?
- Are unsupported preferences clearly marked as awareness-only or research prompts?

## Acceptance Criteria

- All required commands pass.
- Intake route works with and without saved answers.
- Public artifacts are private-answer free.
- Existing local workflows remain intact.
- The final handoff states any screenshot limitations clearly.
- Probability-like language is absent unless explicitly framed as non-predictive deterministic fit context.
