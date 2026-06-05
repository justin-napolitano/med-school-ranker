# Validation, Privacy, and QA

## Objective

Protect scoring transparency work from two failure modes:

- false transparency, where outputs look explanatory but do not match the model math;
- private leakage, where local applicant details enter public outputs.

## Required Validation

Add or preserve validation for:

- weights are positive numbers;
- referenced score columns exist;
- score values are blank or within 1-10 unless explicitly documented;
- component contributions reconcile to displayed scores within rounding tolerance;
- rank confidence is present when score coverage is incomplete;
- missing values are marked missing instead of scored as zero;
- hard-no rows are visible but excluded from rank;
- AAMC grid context is labeled as national aggregate MD data.

## Required Privacy Checks

Public outputs must not contain:

- real applicant profile IDs;
- real applicant names;
- private GPA/MCAT profile rows;
- private partner notes;
- private-derived rankings;
- private-derived contribution rows.

Private outputs must stay under:

```text
data/manual/private/
data/private/
outputs/private/
```

Upload bundle must exclude:

```text
data/manual/private/
data/private/
outputs/private/
```

## Required Commands

Run before commit:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
```

Run after private-output changes:

```bash
uv run med-school-build-private-rankings
git status --short --ignored data/manual/private data/private outputs/private
```

Inspect zip privacy:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
```

## QA Scenarios

Test cases should cover:

- applicant has MCAT/GPA/state;
- applicant is missing MCAT;
- applicant is missing GPA;
- school has missing MCAT/GPA;
- school has low-quality stats;
- same-state public school;
- out-of-state school with explicit OOS policy;
- hard-no school;
- tie score ranking;
- low coverage but high score;
- public build with template profile;
- private build with ignored local profile.

## Done Criteria

- Tests protect contribution math.
- Build commands remain deterministic.
- Private paths remain ignored.
- Upload bundle privacy check passes.
- Public site/workbook do not expose private profile-derived data.
