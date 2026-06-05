# Headless Site Profile Node UI Adoption Plan

## Objective

Execute the first UI-consumption slice for generated JSON nodes: make school profile pages and a limited card preview in the existing static site consume `site_nodes` instead of relying primarily on raw joined payload rows.

This is a model-adoption slice, not a visual redesign.

## Required Read Order

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/SITE_PROFILE_NODE_UI_ADOPTION_EXEC_PLAN.md`
3. `docs/SITE_DATA_MODELING_EXEC_PLAN.md`
4. `docs/site/data_modeling/02_json_node_contracts.md`
5. `docs/site/data_modeling/03_card_surfaces_and_profile_sections.md`
6. `docs/site/profile_node_ui/01_node_contract_audit.md`
7. `docs/site/profile_node_ui/02_shared_card_components.md`
8. `docs/site/profile_node_ui/03_profile_route_node_consumption.md`
9. `docs/site/profile_node_ui/04_rankings_and_compare_preview.md`
10. `docs/site/profile_node_ui/05_admin_payload_compatibility.md`
11. `docs/site/profile_node_ui/06_visual_qa_and_validation.md`
12. `docs/site/profile_node_ui/CRITICAL_REVIEW.md`

## Starting Checks

Run from the repo root:

```bash
git status --short --branch
git status --short --ignored data/manual/private data/raw/aamc outputs/private
uv run pytest
uv run med-school-validate
uv run med-school-build-all
```

Start from a clean worktree unless the user explicitly says otherwise.

## Branch

Use a clean implementation branch:

```bash
git switch -c impl-profile-node-ui-adoption
```

If that branch already exists, inspect it before continuing. Do not overwrite unrelated work.

## Scope

### In Scope

- Audit generated node shape and update docs only when implementation reveals a real contract gap.
- Add JavaScript helpers in the generated static site for node lookup by `school_id` and `school_slug`.
- Add reusable node-backed rendering helpers for cards, metric rows, section blocks, chips, caveats, and missing fields.
- Update the school profile route to render main sections from `school_profile_nodes`.
- Keep existing browser-local reviewer actions working by `school_id`.
- Use card nodes in one limited rankings/profile/compare preview surface without broad route redesign.
- Add focused tests or generated-output checks for node-backed rendering and publish-safe exclusions.
- Regenerate public-safe generated outputs.

### Out of Scope

- Do not redesign the visual system.
- Do not migrate frameworks.
- Do not migrate to Postgres or Vercel.
- Do not change scoring formulas or rank semantics.
- Do not implement predictive admissions probability.
- Do not scrape/download new data.
- Do not remove current admin tables.
- Do not commit private data, private-derived outputs, or local applicant files.

## Implementation Steps

### Step 1: Baseline and Node Audit

- Confirm `payload.site_nodes` exists in `outputs/site/data/site_payload.json` after build.
- Confirm node files exist under `outputs/site/data/nodes/`.
- Check that active school counts align across school nodes, profile nodes, and card nodes.
- Identify profile fields missing from the node contract. Prefer adding missing generated fields in Python over pulling raw joined rows in JavaScript.

### Step 2: Add Node Lookup Helpers

Inside the static site generation code, add deterministic helpers for:

- `getNodeFamilies(payload)`;
- `indexNodesById(nodes)`;
- `indexNodesBySlug(nodes)`;
- `getSchoolProfileNode(schoolIdOrSlug)`;
- `getSchoolCardNode(schoolId)`;
- `getRankingCardNode(schoolId)`.

Keep these helpers small and side-effect free.

### Step 3: Add Shared Node Render Helpers

Add reusable render helpers for:

- card shell;
- metric card;
- fact table/list rows;
- readiness/status chip;
- missing-fields block;
- source/caveat block;
- profile section block.

Use existing site CSS classes where possible. Add minimal CSS only when necessary for node-backed sections to be readable.

### Step 4: Update Profile Route

Update school profile rendering so the primary path is:

```text
slug -> school_profile_node -> sections/cards/facts
```

Keep existing fallback behavior for defensive rendering, but mark fallback paths clearly in code comments or validation warnings.

Preserve:

- direct `#/schools/:slug` routes;
- links from rankings/search/compare pages;
- shortlist/application-list controls;
- compare controls;
- visibility controls;
- dossier edits/export behavior;
- source and methodology caveats.

### Step 5: Add Limited Card Preview Adoption

Adopt card nodes in one bounded visible surface, such as:

- profile snapshot cards;
- rankings row expanded preview;
- compare panel summary cards.

Do not broad-rebuild every table in this slice.

### Step 6: Tests and Validation

Add or update tests to confirm:

- `site_payload.json` includes `site_nodes`;
- generated profile node count matches active school count;
- profile routes render from node-backed data;
- publish-safe mode excludes admin status and reviewer/local-only node data;
- generated HTML still contains the site boot payload;
- private paths remain excluded from upload zip.

Run:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git diff --check
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

If a screenshot QA script exists and dependencies are already installed, run it after the build. Do not install new browser dependencies unless the user explicitly approves it.

## Suggested Headless Prompt

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/HEADLESS_SITE_PROFILE_NODE_UI_ADOPTION_PLAN.md end to end.

Follow docs/HEADLESS_WORKER_RUNBOOK.md first. Start from a clean status check and create branch impl-profile-node-ui-adoption from main if needed.

This is a UI-consumption slice for generated JSON nodes. Make the existing static site render school profile main sections from school_profile_nodes and add a limited visible card preview from generated card/ranking/compare nodes. Preserve current admin tables, workbook/CSV outputs, rankings table behavior, shortlist/application-list controls, compare controls, visibility controls, browser-local dossier edits, and publish-safe mode.

Do not perform a visual redesign. Do not migrate frameworks. Do not migrate to Postgres or Vercel. Do not change scoring formulas. Do not implement predictive admissions probability. Do not scrape or download data. Do not commit private data or private-derived outputs.

Prefer adding missing UI fields to the Python node builders with tests rather than rebuilding joins in JavaScript. Regenerate workbook, site, upload zip, and data quality outputs. Run uv run pytest, uv run med-school-validate, uv run med-school-build-all, git diff --check, the upload-bundle privacy check, and available screenshot QA if dependencies are already present. Commit only public-safe code/docs/data/generated outputs.
```

## Done Criteria

- School profile route main content renders from `school_profile_nodes`.
- At least one visible card/summary surface consumes generated card nodes.
- Existing local workflows remain working.
- Publish-safe output remains clean.
- Tests/build/validation pass.
- Work is committed with a clear message.

