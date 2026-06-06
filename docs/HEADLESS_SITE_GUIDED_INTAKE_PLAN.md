# Headless Guided Applicant Intake Plan

## Objective

Execute the first guided-intake slice: add an applicant-facing intake route that converts controlled setup answers into deterministic ranking context and grouped school-review cards, while preserving the existing static site, node-backed profiles, and local/admin workflows.

## Required Read Order

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/SITE_GUIDED_INTAKE_EXEC_PLAN.md`
3. `docs/SITE_PROFILE_NODE_UI_ADOPTION_EXEC_PLAN.md`
4. `docs/SITE_VISUAL_DIRECTION_PLAN.md`
5. `docs/SITE_DATA_MODELING_EXEC_PLAN.md`
6. `docs/site/guided_intake/01_intake_question_contract.md`
7. `docs/site/guided_intake/02_answer_to_rank_context_mapping.md`
8. `docs/site/guided_intake/03_guided_results_and_school_cards.md`
9. `docs/site/guided_intake/04_local_state_exports_and_privacy.md`
10. `docs/site/guided_intake/05_admin_compatibility_and_methodology.md`
11. `docs/site/guided_intake/06_qa_and_validation.md`
12. `docs/site/guided_intake/CRITICAL_REVIEW.md`

## Starting Checks

Run from repo root:

```bash
git status --short --branch
git status --short --ignored data/manual/private data/raw/aamc outputs/private
uv run pytest
uv run med-school-validate
uv run med-school-build-all
```

Start from a clean branch unless the user explicitly says otherwise.

## Branch

Use:

```bash
git switch -c impl-guided-applicant-intake
```

If the branch already exists, inspect it first and do not overwrite unrelated work.

## Scope

### In Scope

- Add `#/intake` as a guided applicant entry route.
- Make intake the applicant-facing start route, while keeping Rankings and admin/review views reachable.
- Add a deterministic intake question schema in the generated static site.
- Store answers in local browser state using a versioned key.
- Map answers to profile selectors, filters, school grouping, chips, warnings, and target-list context.
- Add guided result groups using existing ranking/card/profile node data.
- Add intake summary and "what changed the view" explanation.
- Keep the advanced rankings table and methodology accessible.
- Add user-triggered export for intake answers. Import is optional only if schema validation is implemented.
- Add focused tests and regenerate public-safe outputs.

### Out of Scope

- Do not change core scoring formulas.
- Do not implement school-specific predictive probability.
- Do not scrape/download new data.
- Do not add server persistence, login, Postgres, Vercel, React, or Next.
- Do not remove current admin/source/raw table surfaces.
- Do not commit private applicant answers or private-derived outputs.
- Do not hide schools irreversibly.
- Do not use labels or copy that imply school-specific admission probability.

## Execution Quality Standards

Follow these standards while implementing:

- Make instructions and UI labels concrete enough that a reviewer can test them.
- Prefer controlled values over free text for any answer that changes output.
- Keep mapping functions deterministic and side-effect free.
- Separate facts, derived fit context, local user choices, and UI copy.
- Add tests for the actual behavior, not only for the presence of text.
- Name limitations directly in methodology and handoff notes.
- Do not claim personalization unless an answer changes a visible rule, group, chip, target, or next action.

## Implementation Steps

### Step 1: Contract Audit

- Confirm generated site payload includes ranking/card/profile nodes.
- Confirm existing profile selectors and local visibility state can be reused.
- Identify which intake answers can affect the current UI without scoring changes.
- Do not invent mappings for unavailable data; show them as "tracked for awareness" or future.
- Reject empty implementation claims. If a preference only creates a chip or prompt, name it as awareness-only in the UI and methodology.

### Step 2: Intake Schema

Add a compact question schema with stable IDs:

- academic profile;
- application strategy;
- geography;
- lifestyle;
- cost sensitivity;
- career optionality;
- school environment;
- dealbreakers.

Use controlled option values. Avoid free-text as a ranking input in this slice, except notes that are stored but not scored.

Required first-slice fields:

- `degree_goal`;
- `applicant_state`;
- `mcat_band`;
- `gpa_band`;
- `application_strategy`;
- `target_application_count`;
- `urbanicity_preference`;
- `cost_sensitivity`.

Optional first-slice fields:

- `states_to_avoid`;
- `career_optionality`;
- `school_environment_preferences`;
- `dealbreakers`.

Use band selectors only for MCAT and GPA in this slice. Do not add exact-score intake fields.

Show `states_to_avoid` as a visible optional control. State avoid behavior must be reversible through the same local hide/restore model used elsewhere in the site.

### Step 3: Local State

Add versioned browser-local state:

```text
med_school_ranker_intake_v1
```

Include:

- answers;
- updated timestamp;
- schema version;
- derived context preview.

The site must work if storage is empty, corrupted, or unavailable.

### Step 4: Answer Mapping

Implement a pure deterministic mapping function:

```text
answers -> intakeContext
```

The context should include:

- selected MCAT/GPA/state values;
- degree-type filter;
- strategy label and target application count;
- geography preference chips;
- lifestyle/cost/career awareness chips;
- hard avoid/dealbreaker rules;
- grouped review criteria;
- methodology text.

Do not mutate school data in this function.

### Step 5: Intake Route

Add `#/intake` with:

- sectioned questions;
- progress or completed-section state;
- save locally;
- reset;
- continue to guided review;
- link to advanced rankings table.

The copy should be plain and direct. Do not use technical language like weights, nodes, or payload.

### Step 6: Guided Results

Add an applicant-facing results view or section that groups schools into:

- Start Here;
- Florida Options;
- Reach Schools To Research;
- Compare Next;
- Need More Data;
- Lower Priority Or Hidden.

Use existing ranking/card node fields for reasons, risks, confidence, missing data, and next action.

Show high-priority groups by default. Collapse lower-priority groups by default until clicked, especially `Need More Data` and `Lower Priority Or Hidden`.

Treat these as review groups, not admissions-probability groups.

Keep all exclusions reversible and keep hidden-school review available.

### Step 7: Methodology and Advanced Controls

Expose:

- intake summary;
- active rules;
- what is not scored yet;
- link to methodology;
- link to advanced table.

Advanced controls can still expose tables, selectors, and source details.

### Step 8: Tests and Validation

Add or update tests for:

- generated HTML contains the intake route and schema;
- answer mapping is deterministic;
- empty/corrupt local storage fallback;
- publish-safe payload has no private answer values;
- upload zip excludes private paths;
- existing profile/rankings routes still render.

Run:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
git diff --check
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
git status --short --ignored data/manual/private data/raw/aamc outputs/private
```

Run screenshot QA if the existing script and dependencies are already available. Do not install new browser dependencies without user approval.

## Suggested Headless Prompt

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/HEADLESS_SITE_GUIDED_INTAKE_PLAN.md end to end.

Follow docs/HEADLESS_WORKER_RUNBOOK.md first. Start from a clean status check and create branch impl-guided-applicant-intake if needed.

Add a guided applicant intake route to the existing static site. The intake should ask controlled applicant-readable questions, store answers locally, map them deterministically to existing profile selectors, filters, review-group criteria, explanation chips, and list targets, then show grouped school-review cards. Preserve existing rankings, profile, compare, shortlist, visibility, application-list, dossier, research, admin, workbook, CSV, and publish-safe workflows.

Do not change core scoring formulas. Do not implement predictive admissions probability. Do not scrape/download data. Do not migrate frameworks or persistence. Do not commit private applicant answers or private-derived outputs. Do not use review labels that imply school-specific acceptance odds.

Regenerate workbook, site, upload zip, and data quality outputs. Run uv run pytest, uv run med-school-validate, uv run med-school-build-all, git diff --check, the upload-bundle privacy check, and available screenshot QA if dependencies are already present. Commit only public-safe code/docs/data/generated outputs.
```

## Done Criteria

- `#/intake` exists and maps answers to deterministic guided review groups.
- User can review why the view changed.
- School cards show reasons, risks, missing data, and next actions.
- Exclusions remain reversible.
- Advanced/admin surfaces remain available.
- Personal answers remain local/exported only.
- Tests/build/validation pass.
- Work is committed with a clear message.
