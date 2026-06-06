# Astro React Product Frontend Executive Plan

## Objective

Add a contained Astro + React product frontend for applicants while preserving the current Python data/model generator and admin-oriented static site as the source of truth for this pass.

The product frontend must be a static export that can run on GitHub Pages or any static host. It consumes the publish-safe generated payload at `outputs/site/data/site_payload.json`, copied deterministically into `frontend/public/data/site_payload.json` before frontend builds.

## Product Contract

- Default route: Build My List at `/`.
- Product routes: `/`, `/interested`, `/applying`, `/not-interested`, `/schools/[slug]`, `/compare`, `/methodology`.
- Legacy route: `/recommendations` may exist as a handoff to Build My List, but it is not a distinct product tab.
- Admin route: `/admin`, visually and structurally separated from applicant routes.
- Product UI uses cards/lists by default. Tables remain admin-only or secondary fallback.
- Applicant actions are browser-local: Interested cap 50, Applying cap 25, Not Interested removal list, compare selection local state, JSON export.
- Routine visible Hide controls are not part of applicant cards.
- Score-fit labels are derived only from MCAT/GPA screen context and must always be caveated as not acceptance probability.

## Non-Goals

- Do not rewrite ranking formulas, source normalization, Python payload generation, or workbook outputs.
- Do not scrape new data.
- Do not add a runtime LLM, backend, predictive model, authentication, or non-deterministic ranking behavior.
- Do not claim guaranteed admission, school-specific admit chance, best/safest schools, public/private quality, residency placement superiority, or curated-list certainty unless generated data directly supports the claim with caveats.

## Static Data Flow

```bash
uv run med-school-build-site --site-mode publish_safe
cd frontend
npm run sync:data
npm run build
```

`npm run sync:data` copies `../outputs/site/data/site_payload.json` into `frontend/public/data/site_payload.json`. That frontend copy is generated and ignored to avoid duplicating the large tracked payload; `predev` and `prebuild` recreate it deterministically. The frontend imports the copied JSON at build time for static school routes and also serves it from `/data/site_payload.json` in the built output for traceability.

## Implementation Phases

### Phase 1: Scaffold

- Create `frontend/` with Astro, React, TypeScript, static output, and npm lockfile.
- Add scripts for `sync:data`, `build`, `dev`, `preview`, and `smoke`.
- Keep all frontend code inside `frontend/`.

### Phase 2: Product Shell

- Build a serious, dense applicant shell with restrained typography, semantic chips, accessible focus states, and mobile behavior.
- Make `/` the first screen and label it Build My List.
- Keep product name generic.

### Phase 3: Applicant Routes

- Build card/list routes for Build My List, interested list, applying list, not-interested list, school profiles, compare, methodology, and admin/data.
- Use generated fields for school identity, ranking context, MCAT/GPA context, cost, source confidence, and missing-data warnings.
- Derive "why it ranks here" bullets from generated rank summaries, top drivers, cost context, and missing-data/status fields.

### Phase 4: Local State

- Store Interested, Applying, compare selections, and profile preferences in browser local storage.
- Enforce Interested max 50 and Applying max 25 in deterministic UI logic.
- Support local export without writing private data back into the repo.

### Phase 5: Claim Safety And QA

- Add a frontend smoke check at `frontend/scripts/smoke-check.mjs`.
- Verify build output, route content, caveat language, unsupported-claim absence, absence of routine Hide button text, and admin route separation.
- Keep Python verification unchanged.

## Required Verification Before Commit

From repo root:

```bash
cd frontend
npm install
npm run build
npm run smoke
cd ..
uv run med-school-validate
uv run pytest
git diff --check
```

If a command fails, record the exact command and failure in the handoff. Do not claim it passed.

## Definition Of Done

- The Astro app builds statically from generated publish-safe JSON.
- `/` renders Build My List as a product onboarding/list-building surface.
- Build My List, local lists, profile, compare, methodology, and separated admin/data routes exist.
- Cards lead with school name, location, score-screen fit caveat, rank/context bullets, MCAT/GPA, cost when available, and Interested/Applying actions.
- Frontend smoke check passes.
- Existing Python validation and tests pass.
- Intended changes are committed without unrelated screenshot artifacts.
