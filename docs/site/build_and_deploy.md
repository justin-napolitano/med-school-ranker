# Site Plan: Build and Deploy

## Objective

Define how the static review site is generated, verified, and prepared for GitHub Pages.

First implementation is local-only. GitHub Pages remains a later publishing step after the user confirms the local review site is useful.

## Inputs

- CSV source files.
- Generated ranking and validation outputs.
- Site source files.

## Outputs

```text
outputs/site/index.html
outputs/site/assets/
outputs/site/data/*.json
```

Phase 1.5A local rule:

- `index.html` must embed the data payload needed for the site to run from `file://`.
- Adjacent JSON files are generated for inspection and future hosted use.

## Commands

Required command:

```bash
uv run med-school-build-site
```

Full build should eventually run:

```bash
uv run med-school-build-all
```

Verification command:

```bash
uv run pytest
```

## Build Steps

1. Validate project.
2. Build rankings.
3. Convert selected CSVs to JSON.
4. Build a joined per-school payload with derived fields.
5. Generate or copy static site files.
6. Embed site data into `index.html`.
7. Verify required output files exist.
8. Verify JSON parses.
9. Verify active school count matches `data/school_master.csv`.

## GitHub Pages Options

Option A: publish `outputs/site` manually.

Option B: add GitHub Actions workflow later:

- install `uv`
- run `uv run med-school-build-all`
- upload `outputs/site` as Pages artifact
- deploy Pages

Default first pass: local static generation only. Add GitHub Actions after the site shape is useful.

Current decision: do not wire GitHub Pages deployment in Phase 1.5A.

## Validation Rules

- No files from `data/manual/private` copied to site output.
- Site data JSON excludes private data paths.
- `index.html` references existing local files.
- `index.html` includes embedded data, avoiding required `fetch()` calls for local review.
- Site output can be opened from the filesystem.

## Definition of Done

- `uv run med-school-build-site` generates a usable static site.
- The site can be opened locally without a dev server.
- Output is suitable for GitHub Pages later, but deployment is not required in the first pass.
- Tests verify required output files and JSON validity.
