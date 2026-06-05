# Headless Execution Plan: Phase 1.5A Static Site Baseline

## Objective

Build the first-pass static local review site without human follow-up. The site should make the current school universe quickly reviewable in a browser while keeping the workbook as the edit/input artifact.

## Execution Mode

- Run non-interactively.
- Follow `docs/SITE_EXEC_PLAN.md` and `docs/site/*.md`.
- Make conservative assumptions from the docs.
- Do not ask follow-up questions.
- Do not scrape or populate GPA/MCAT values.
- Do not add real applicant/private data.
- Do not wire GitHub Pages deployment in this pass.
- Preserve current CSV/XLSX outputs and existing build commands.

## Repository

```text
/Users/justin/repos/med-school-ranker
```

Start from a clean commit.

## Phase 1.5A Scope

### 1. Site Builder Command

Add:

```bash
uv run med-school-build-site
```

Expected implementation location:

```text
src/med_school_ranker/site.py
```

Also add compatibility wrapper if useful:

```text
scripts/build_site.py
```

### 2. Site Output

Generate:

```text
outputs/site/index.html
outputs/site/data/school_master.json
outputs/site/data/calculated_rankings.json
outputs/site/data/applicant_profiles.json
outputs/site/data/admissions_stats.json
outputs/site/data/partner_inputs.json
outputs/site/data/admissions_source_queue.json
outputs/site/data/data_quality_report.json
outputs/site/data/project_subplans.json
```

### 3. Local File Rule

`outputs/site/index.html` must work when opened directly from the filesystem.

Do not rely on browser `fetch()` for required data in Phase 1.5A. Embed the generated JSON payload in `index.html`, for example:

```html
<script type="application/json" id="site-data">...</script>
```

Adjacent JSON files should still be generated for inspection and future hosted use.

### 4. Privacy Mode

Default mode:

```text
local_full
```

Rules:

- Include current non-private applicant profile template.
- Include current partner input template.
- Never include files from `data/manual/private` or `data/private`.
- Do not add real applicant/private data.
- No GitHub Pages deployment.

### 5. Derived Payload

Build a joined per-school payload keyed by `school_id`.

Required derived fields:

- `warning_count`
- `error_count`
- `partner_input_status`
- `partner_notes_indicator`
- `hard_no_flag`
- `admissions_stats_present`
- `source_queue_status`
- `suggested_next_action`

Derivation rules are in `docs/SITE_EXEC_PLAN.md`.

### 6. Views

Implement these static views in `index.html`:

- Dashboard
- Rankings
- School Detail
- Partner Review
- Admissions Sources
- Data Quality
- Plans

Dashboard is the default view.

Rankings is the highest-priority table. If tradeoffs are needed, polish Rankings first.

### 7. Minimum Interactions

Required:

- menu/view switching
- global search
- Rankings filters for degree, state, hard-no, data quality warning presence, and partner input status
- sortable Rankings table
- click school row/name to open school detail panel or section
- Data Quality filtering by severity
- Admissions Sources filtering by missing source URL

Deferred:

- comparison drawer
- in-browser editing
- URL-saved presets
- GitHub Pages workflow

### 8. Build-All Integration

Update:

```bash
uv run med-school-build-all
```

It must run:

1. validation
2. rankings
3. workbook
4. site
5. upload bundle

The upload bundle should include `outputs/site/`.

### 9. Tests

Add pytest coverage for:

- `med-school-build-site` generates `outputs/site/index.html`
- required JSON files are generated and parseable
- embedded data exists in `index.html`
- site active school count equals `data/school_master.csv`
- Puerto Rico remains excluded from site data
- private paths are not copied into `outputs/site`
- workbook/build-all still passes existing tests

## Required Verification

Run:

```bash
uv run med-school-build-site
uv run med-school-build-all
uv run pytest
```

Verify:

- `outputs/site/index.html` exists.
- Required JSON files exist.
- `index.html` includes embedded data payload.
- Active site school count is 233.
- Puerto Rico rows are 0.
- `med-school-ranker-upload.zip` includes `outputs/site/index.html`.
- No `data/manual/private` or `data/private` files are included in site output or upload bundle.

## Do Not Do

- Do not scrape admissions data.
- Do not infer GPA/MCAT.
- Do not add a dev server requirement.
- Do not add GitHub Pages workflow.
- Do not implement comparison drawer.
- Do not add real applicant data.

## Definition of Done

Phase 1.5A is done when:

- `uv run med-school-build-site` works.
- `uv run med-school-build-all` includes site generation.
- `uv run pytest` passes.
- `outputs/site/index.html` opens locally with embedded data.
- Rankings is usable as the highest-priority review table.
- Repo is committed with a clear Phase 1.5A implementation commit.
