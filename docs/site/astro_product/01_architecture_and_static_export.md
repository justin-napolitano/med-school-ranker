# Architecture And Static Export

## Scope

The Astro product app lives under `frontend/` and is independent from the Python package layout.

## Data Source

Source of truth:

```text
outputs/site/data/site_payload.json
```

Frontend copy:

```text
frontend/public/data/site_payload.json
```

The copy is deterministic and performed by:

```bash
cd frontend
npm run sync:data
```

The frontend copy is generated and ignored rather than committed. The static build imports the public copy for route generation and serves it as a build artifact for inspection.

## Hosting

The app must use Astro static output only. GitHub Pages remains viable because no server runtime, private data, LLM call, scraping job, database, or API route is required.

Required build commands:

```bash
cd frontend
npm install
npm run build
npm run smoke
```

## Directory Contract

```text
frontend/
  astro.config.mjs
  package.json
  package-lock.json
  public/data/site_payload.json
  scripts/sync-data.mjs
  scripts/smoke-check.mjs
  src/
    components/
    layouts/
    lib/
    pages/
    styles/
```

## Determinism

- Ranking order comes from generated payload fields.
- Applicant preference controls filter/reorder only through deterministic client-side logic.
- Local state remains in browser storage and export files only.
- No runtime network dependency is allowed for product behavior.
