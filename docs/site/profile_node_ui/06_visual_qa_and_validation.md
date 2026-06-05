# Visual QA and Validation

## Objective

Verify that node-backed profile rendering works without introducing obvious layout, routing, privacy, or regression issues.

## Required Commands

Run:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git diff --check
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

Run screenshot QA only if the existing script and dependencies are already available. Do not install browser tooling in this slice unless the user approves it.

## Manual Review Checklist

- Open the local site.
- Visit rankings.
- Open at least three profile routes:
  - one high-ranked MD school;
  - one school with partial/missing data;
  - one school with cost or source caveats.
- Confirm profile sections render from node-backed data.
- Confirm shortlist, compare, hide/restore, and dossier edit controls still behave.
- Confirm publish-safe build does not expose admin/private fields.

## Done Criteria

- Required commands pass or failures are clearly documented.
- Screenshots/manual review do not reveal broken profile layout or missing route payloads.
- Private ignored paths remain ignored.

