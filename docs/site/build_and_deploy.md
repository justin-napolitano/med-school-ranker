# Site Plan: Build and Deploy

## Objective

Define how the static review site is generated, verified, and deployed to GitHub Pages.

The legacy generated site remains usable locally from `outputs/site/index.html`, and the public deployment path always builds the `publish_safe` payload before compiling the Astro frontend and uploading the Pages artifact.

## Inputs

- CSV source files.
- Generated ranking and validation outputs.
- Site source files.

## Outputs

```text
outputs/site/data/site_payload.json
frontend/dist/index.html
frontend/dist/_astro/
frontend/dist/schools/*/index.html
```

Local rule:

- `index.html` must embed the data payload needed for the site to run from `file://`.
- Adjacent JSON files are generated for inspection and hosted use.

## Commands

Required command:

```bash
uv run med-school-build-site
```

Public-safe command:

```bash
uv run med-school-build-site --site-mode publish_safe
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

## GitHub Pages Flow

Workflow file:

```text
.github/workflows/deploy-pages.yml
```

The workflow runs on pull requests, pushes to `main`, and manual dispatch.

Build steps:

- install `uv`
- run `uv sync --locked --dev`
- run `uv run med-school-integrate-sources`
- run `uv run med-school-build-rankings`
- run `uv run med-school-build-site --site-mode publish_safe`
- run `uv run med-school-validate`
- run `uv run pytest`
- install Node dependencies in `frontend/`
- run `npm run build`
- run `npm run smoke`
- upload `frontend/dist` as Pages artifact
- deploy Pages, except on pull requests

Repository settings must use GitHub Actions as the Pages source. The workflow publishes only the generated Astro `frontend/dist` directory. The workflow sets `ASTRO_BASE_PATH` from the repository name so project-page links resolve under `/<repo>/` after deployment.

## Validation Rules

- No files from `data/manual/private` copied to site output.
- Site data JSON excludes private data paths.
- `index.html` references existing local files.
- `index.html` includes embedded data, avoiding required `fetch()` calls for local review.
- Site output can be opened from the filesystem.

## Definition of Done

- `uv run med-school-build-site` generates a usable static site.
- The legacy site can be opened locally without a dev server.
- The Astro product frontend builds to `frontend/dist` and passes smoke checks.
- GitHub Pages deployment is available through the `Deploy Public Site` workflow.
- Tests verify required output files and JSON validity.
