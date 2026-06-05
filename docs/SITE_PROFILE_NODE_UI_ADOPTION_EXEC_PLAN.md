# Site Profile Node UI Adoption Executive Plan

## Objective

Make the existing static review site consume the generated JSON node layer for school profiles and reusable cards before the larger visual-design pass.

This is the bridge between the completed data-modeling slice and the future product-style card/site redesign:

```text
CSV/source tables remain canonical.
Generated JSON nodes remain the site read model.
The current site becomes the first UI consumer of school_profile_nodes and card nodes.
Admin tables stay available for local review.
```

The goal is not to polish the site visually yet. The goal is to prove that applicant-facing pages can render from stable node contracts instead of ad hoc joined payload rows.

## Current State

The repo already has:

- generated node files under `outputs/site/data/nodes/`;
- `site_nodes` embedded in `outputs/site/data/site_payload.json`;
- school fact, card, profile, ranking, compare, list, methodology, and admin-status node families;
- local-full and publish-safe site modes;
- current school dossier/profile routes;
- browser-local visibility, dossier notes, shortlist/application list, compare, and research queue workflows;
- deterministic scores, rank explanations, and source/data-quality caveats.

The remaining problem is consumption:

- the site still primarily renders from the larger route payload and joined school rows;
- profile route rendering does not yet treat `school_profile_nodes` as the source contract;
- reusable card rendering is not centralized around node-shaped data;
- future design work could drift if the UI keeps depending on raw payload shapes.

## Scope

### In Scope

- Audit the generated node files against the profile/card UI needs.
- Add lightweight frontend read helpers that index `site_nodes` by `school_id` and `school_slug`.
- Add reusable rendering helpers/components for node-backed metric cards, fact rows, status chips, section blocks, and source/caveat panels.
- Move the school profile route to render its main sections from `school_profile_nodes`.
- Keep current reviewer-state controls, visibility controls, shortlist actions, compare actions, and dossier note editing working.
- Add a small rankings/compare preview that reads from card nodes where practical, without rebuilding the whole rankings page yet.
- Preserve `site_payload.json` compatibility and existing workbook/CSV outputs.
- Add tests or smoke checks that confirm the generated site has node-backed profiles, publish-safe mode excludes admin-only nodes, and profile links still resolve.

### Out of Scope

- Do not perform a full visual redesign.
- Do not migrate to React, Astro, Next, Vercel, or Postgres.
- Do not change scoring formulas.
- Do not implement school-specific predictive admissions probability.
- Do not scrape or download new school data.
- Do not remove existing admin routes or tables.
- Do not add authentication or hosted persistence.
- Do not commit private applicant data or private-derived outputs.

## Target User Experience

After this slice, the user should be able to open a school profile and see sections rendered from generated profile nodes:

- overview;
- applicant fit;
- admissions stats;
- cost and debt;
- requirements and policies;
- source confidence;
- methodology;
- local reviewer state where allowed.

Each section should show missing data honestly. Partial sections should remain visible and clearly labeled rather than disappearing.

The existing site can still look like an admin/workbench product. The value of this slice is that the profile page data model becomes clean enough for a later card-based visual pass.

## Architecture

```text
src/med_school_ranker/site.py
  generates site_payload.json
  embeds site_nodes
  renders index.html

outputs/site/data/nodes/
  school_profile_nodes.json
  school_card_nodes.json
  ranking_card_nodes.json
  compare_card_nodes.json
  methodology_nodes.json
  admin_status_nodes.json

site JavaScript
  indexes payload.site_nodes
  renders profile sections from school_profile_nodes
  keeps admin tables on existing payload until migrated deliberately
```

Do not re-create joins in JavaScript. If a profile needs a field, prefer adding it to the generated node builder in Python with a test instead of stitching raw arrays together in the browser.

## Implementation Sequence

### Phase 0: Contract Audit

- Inspect `site_nodes` and `outputs/site/data/nodes/*.json`.
- Compare generated fields against the profile-page subplan.
- Identify missing fields as explicit follow-up work rather than silently pulling from raw joined rows.

### Phase 1: Node Index and Rendering Helpers

- Add browser-side helpers for:
  - `schoolNodesById`;
  - `schoolProfileNodesById`;
  - `schoolProfileNodesBySlug`;
  - `schoolCardNodesById`;
  - `rankingCardNodesById`;
  - `compareCardNodesById`.
- Add shared render helpers for:
  - card shell;
  - metric rows;
  - status/readiness chips;
  - missing-field lists;
  - source/caveat panels.

### Phase 2: Profile Route Consumption

- Update `#/schools/:school_slug` rendering to use the school profile node as its primary data source.
- Render profile sections generically from node section arrays where possible.
- Keep existing action buttons and local reviewer-state controls attached by stable `school_id`.
- Preserve direct route resolution by slug and existing profile links.

### Phase 3: Card Preview Adoption

- Use school card/ranking card nodes in at least one visible list/card preview surface.
- Do not broad-rebuild every table in this slice.
- Keep rankings table behavior and filters stable.

### Phase 4: Publish-Safe and Admin Compatibility

- Confirm publish-safe payloads can render node-backed profile pages.
- Confirm admin-only node families remain excluded from publish-safe mode.
- Confirm local-full mode still exposes admin status and reviewer workflows.

### Phase 5: QA and Handoff

- Run generated-site tests and source validation.
- Run screenshot QA if the repository already has a script for it.
- Update `data/project_subplans.csv` statuses.
- Regenerate workbook/site/upload artifacts.
- Commit only public-safe artifacts.

## Acceptance Criteria

- Every active school still has a working profile route.
- School profile main content is driven by `school_profile_nodes`.
- Missing or partial profile sections render honestly.
- Existing shortlist, compare, visibility, dossier notes, and local browser workflows still work.
- Publish-safe output does not include admin-only node families or private paths.
- Tests/build/validation pass.
- The next design pass can style node-backed cards without understanding raw CSV joins.

## Child Plans

- [Node Contract Audit](site/profile_node_ui/01_node_contract_audit.md)
- [Shared Card Components](site/profile_node_ui/02_shared_card_components.md)
- [Profile Route Node Consumption](site/profile_node_ui/03_profile_route_node_consumption.md)
- [Rankings and Compare Preview](site/profile_node_ui/04_rankings_and_compare_preview.md)
- [Admin Compatibility and Publish-Safe Guardrails](site/profile_node_ui/05_admin_payload_compatibility.md)
- [Visual QA and Validation](site/profile_node_ui/06_visual_qa_and_validation.md)
- [Critical Review](site/profile_node_ui/CRITICAL_REVIEW.md)

