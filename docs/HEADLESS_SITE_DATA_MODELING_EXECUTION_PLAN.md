# Headless Site Data Modeling Execution Plan

## Objective

Implement the first data-modeling slice: generated JSON read-model nodes for school cards, school profiles, rankings, methodology, and admin status, while preserving existing CSV, workbook, and static-site behavior.

This is a contract and generator slice before visual redesign. It should make the next product-design pass safer by giving the UI stable card/profile nodes to consume.

## Required Read Order

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/SITE_DATA_MODELING_EXEC_PLAN.md`
3. `docs/site/data_modeling/01_canonical_domain_tables.md`
4. `docs/site/data_modeling/02_json_node_contracts.md`
5. `docs/site/data_modeling/03_card_surfaces_and_profile_sections.md`
6. `docs/site/data_modeling/04_admin_public_payload_separation.md`
7. `docs/site/data_modeling/06_validation_privacy_and_qa.md`
8. `docs/SITE_PRODUCT_REBUILD_EXEC_PLAN.md`
9. `docs/SCORING_TRANSPARENCY_EXEC_PLAN.md`

## Starting Checks

Run:

```bash
git status --short --branch
git status --short --ignored data/manual/private data/raw/aamc outputs/private
uv run pytest
uv run med-school-validate
uv run med-school-build-all
```

Start from a clean worktree unless the user explicitly says otherwise.

## Scope

### In Scope

- Add generated node output directory:

```text
outputs/site/data/nodes/
```

- Generate initial node files:

```text
school_nodes.json
school_card_nodes.json
school_profile_nodes.json
ranking_card_nodes.json
compare_card_nodes.json
list_nodes.json
methodology_nodes.json
admin_status_nodes.json
```

- Add node metadata:

```text
node_schema_version
generated_at
site_mode
source_tables
record_count
publish_safe
```

- Keep current `site_payload.json` and embedded HTML payload backward compatible.
- Add tests for node shape, stable IDs, counts, publish-safe exclusion, and private-path guardrails.
- Update workbook/site/upload generated artifacts.
- Update `data/project_subplans.csv` statuses after implementation.

### Out of Scope

- Do not visually redesign the site.
- Do not migrate to a frontend framework.
- Do not migrate to Postgres.
- Do not implement auth/login.
- Do not change scoring formulas.
- Do not implement predictive admissions probability.
- Do not scrape/download new data.
- Do not commit private applicant data or private-derived ranking outputs.
- Do not remove existing JSON files or CSV outputs.

## Implementation Steps

### Step 1: Branch and Baseline

Use a clean branch name:

```bash
git switch -c impl-site-data-modeling-nodes
```

If the branch exists, switch only when the worktree is clean or the existing changes are clearly the same task.

### Step 2: Add Node Builder Structure

Preferred implementation:

- keep joins in `src/med_school_ranker/site.py` if the change is small;
- or extract a focused helper module such as `src/med_school_ranker/site_nodes.py` if the node builder becomes large.

Do not duplicate large join logic in JavaScript.

### Step 3: Define Node Shapes in Code

Create deterministic dict builders for:

- school identity/fact node;
- school card node;
- ranking card node;
- comparison card node;
- school profile node with section array;
- methodology node;
- admin status node.

Every node should include:

- stable ID;
- schema version;
- display label fields;
- source/confidence fields where relevant;
- readiness/confidence label;
- missing-field list where relevant.

### Step 4: Write Node JSON Files

Write node files under:

```text
outputs/site/data/nodes/
```

For `publish_safe`, omit admin nodes and any local/private/reviewer-state nodes.

### Step 5: Preserve Existing Site Behavior

The first implementation may expose nodes in `site_payload.json`, but the current UI does not need to consume them yet.

Existing tests around:

- default route;
- publish-safe payload;
- profile routes;
- application list;
- compare;
- dossier/visibility exports;

must keep passing.

### Step 6: Verification

Run:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git diff --check
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
```

Also check:

```bash
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

## Suggested Headless Prompt

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/HEADLESS_SITE_DATA_MODELING_EXECUTION_PLAN.md end to end.

Follow docs/HEADLESS_WORKER_RUNBOOK.md first. Start from a clean status check and create a clean implementation branch if needed.

This is the first data-modeling implementation slice. Add generated JSON read-model nodes under outputs/site/data/nodes for school facts, school cards, school profiles, ranking cards, compare cards, list nodes, methodology nodes, and admin status nodes. Preserve current CSV/workbook/static-site outputs and keep site_payload.json backward compatible.

Do not perform a visual redesign. Do not migrate to Postgres. Do not change scoring formulas. Do not implement predictive admissions probability. Do not scrape or download data. Do not add backend persistence. Do not commit private data or private-derived outputs.

Add tests for node shape, stable IDs, counts, publish-safe exclusion, and private-path guardrails. Regenerate workbook, site, upload zip, and data quality outputs. Run uv run pytest, uv run med-school-validate, uv run med-school-build-all, git diff --check, and the upload-bundle privacy check. Commit only public-safe code/docs/data/generated outputs.
```

## Done Criteria

- Initial node files are generated deterministically.
- Current site still serves and existing routes still work.
- Publish-safe mode excludes admin/reviewer/private nodes.
- Tests cover the node contracts.
- Workbook/site/upload artifacts are regenerated.
- Work is committed with a clear message.
