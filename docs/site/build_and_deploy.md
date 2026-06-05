# Site Plan: Build and Deploy

## Objective

Define how the static review site is generated, verified, and prepared for GitHub Pages.

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
4. Generate or copy static site files.
5. Verify required output files exist.
6. Verify JSON parses.
7. Verify active school count matches `data/school_master.csv`.

## GitHub Pages Options

Option A: publish `outputs/site` manually.

Option B: add GitHub Actions workflow later:

- install `uv`
- run `uv run med-school-build-all`
- upload `outputs/site` as Pages artifact
- deploy Pages

Default first pass: local static generation only. Add GitHub Actions after the site shape is useful.

## Validation Rules

- No files from `data/manual/private` copied to site output.
- Site data JSON excludes private data paths.
- `index.html` references existing local files.
- Site output can be opened from the filesystem.

## Definition of Done

- `uv run med-school-build-site` generates a usable static site.
- The site can be opened locally without a dev server.
- Output is suitable for GitHub Pages.
- Tests verify required output files and JSON validity.
