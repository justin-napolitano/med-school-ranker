# Site Guided Applicant Intake Executive Plan

## Objective

Turn the site from a spreadsheet-style review surface into a guided applicant decision tool.

The intake should ask applicant-readable controlled questions, translate answers into deterministic ranking context, and then show review groups/cards without requiring the user to understand weights, CSVs, or data modeling.

```text
Applicant answers controlled setup questions.
The site maps those answers to filters, ranking lenses, warnings, and list goals.
School cards explain why each school is shown.
Raw tables remain available as advanced/admin surfaces.
```

This is not a new scoring model. It is a product layer over the existing deterministic scoring, node-backed profiles, local school selection, and publish-safe site outputs.

## Current State

The project already has:

- deterministic scoring for an applicant profile;
- profile-aware rankings and rank explanations;
- generated JSON nodes for school, profile, card, ranking, compare, list, methodology, and admin surfaces;
- school profiles rendered from `school_profile_nodes`;
- reversible hide/restore, shortlist, compare, application-list, dossier, and research-queue workflows;
- browser-local review state and CSV export patterns;
- publish-safe output guardrails.

The remaining product problem is accessibility of the decision model:

- the first-use experience still feels like a data workbook;
- rankings expose many facts before asking what the applicant wants;
- users need to understand filters, rank bands, and score context too early;
- there is no guided way to turn "I am in Florida, MD only, urban preferred, 509 MCAT, 3.85 GPA, balanced list" into a reviewable school list.

## Scope

### In Scope

- Add a guided `#/intake` route as the applicant-facing entry point.
- Make intake the applicant-facing start route once implemented, while keeping Rankings and admin views reachable.
- Ask controlled questions grouped by applicant profile, strategy, geography, lifestyle, cost sensitivity, career optionality, school environment, and dealbreakers.
- Store intake answers in browser-local state with export support. Import is optional in this slice.
- Map intake answers deterministically to:
  - existing MCAT/GPA/state/profile selectors;
  - degree-type and geography filters;
  - local ranking/list lenses;
  - warning chips and school-card explanation chips;
  - target list buckets.
- Add an intake summary route or panel that answers:
  - what profile is being used;
  - what preferences are shaping the view;
  - what filters are active;
  - what remains uncertain or manually reviewable.
- Update the rankings/list-builder view to consume the intake context without hiding advanced controls.
- Keep all personal/intake answers local-only unless the user exports them.
- Add tests for mapping determinism, privacy, and generated-site route presence.

### Out of Scope

- Do not change the core scoring formulas in this slice.
- Do not implement school-specific predictive admissions probability.
- Do not migrate to React, Next, Vercel, Postgres, or server persistence.
- Do not scrape or download new data.
- Do not remove the current admin/raw table views.
- Do not require a login.
- Do not commit private applicant answers or private-derived outputs.
- Do not make the intake copy gimmicky or youth-slang-oriented.

## Target User Experience

The first screen should communicate:

```text
Tell us what kind of application list you are building.
We will group schools for review, explain why, and keep every exclusion reversible.
```

The first implementation should keep required intake short enough for first-use review:

- no more than 12 required fields;
- optional fields can be skipped without blocking results;
- each answer must either affect the current view or be visibly labeled as awareness-only.

The resulting view should show:

- `Start Here`;
- `Florida Options`;
- `Reach Schools To Research`;
- `Compare Next`;
- `Need More Data`;
- `Lower Priority Or Hidden`.

These are review-group labels, not admissions probability labels.

Every school card should answer:

1. Why is this school showing up?
2. What makes it attractive?
3. What are the risks?
4. What data is missing or low-confidence?
5. What action should the user take next?

## Product Principles

### Intake Is A Lens, Not A Black Box

The site must show how answers changed the view. Every intake-derived rule should be visible in plain language.

### Deterministic First

The same answers and same source data must produce the same school buckets. No opaque probability, AI inference, or hidden recommender behavior belongs in this slice.

### Truth In Labels

Avoid labels that imply acceptance likelihood unless they come from existing deterministic fit fields and are explained. Prefer "review group," "fit signal," and "research priority" over "recommended" when the UI is not making an admissions prediction.

### Reversible Exclusions

Intake can hide or de-emphasize schools, but the user must be able to view hidden schools and restore them.

### Personal Data Stays Local

Answers live in browser storage and exports. Public/generated artifacts must not contain real private applicant answers.

### Advanced Controls Stay Available

Spreadsheet-like tables, weights, methodology, and raw source review remain available for power users and admin review.

## Architecture

```text
src/med_school_ranker/site.py
  generates static site and embedded/public payload

site JavaScript
  intake schema
  intake answer state
  answer -> ranking context mapping
  grouped result/card rendering
  local export/import

outputs/site/data/nodes/
  school_card_nodes.json
  school_profile_nodes.json
  ranking_card_nodes.json
  compare_card_nodes.json
  methodology_nodes.json
```

The first implementation can keep the intake schema in generated site JavaScript. If it grows, move it to a generated JSON node family later, but do not migrate persistence in this slice.

## Implementation Sequence

### Phase 0: Intake Contract

- Define the question schema, answer IDs, option values, defaults, and local storage key.
- Keep copy direct and applicant-centered.
- Avoid asking for fields that do not affect the current view.
- Define which answers are required for first results and which are optional.

### Phase 1: Answer Mapping

- Map intake answers to deterministic context:
  - profile selectors;
  - MD-only filter;
  - state/geography filters;
  - urban/suburban/rural preferences;
  - strategy list targets;
  - cost sensitivity labels;
  - dealbreaker visibility state.
- Document all mappings in methodology text.
- Send unsupported or weakly sourced preferences to awareness chips/research prompts instead of score changes.

### Phase 2: Intake Route

- Add `#/intake` with progress, sections, save/reset, and continue-to-results actions.
- Persist answers locally.
- Add a compact intake summary.

### Phase 3: Guided Results

- Add grouped results powered by existing rankings/card nodes.
- Use school cards instead of raw table rows as the primary review mode.
- Keep rankings table available as `Advanced table` or similar.

### Phase 4: Local State, Exports, and Privacy

- Add intake export. Import is optional and should only be implemented if it can validate schema version and controlled values.
- Keep exports explicit and user-triggered.
- Confirm publish-safe output does not include private answers.

### Phase 5: QA and Handoff

- Add tests for route presence, mapping determinism, privacy, and local-state schema stability.
- Run build, validation, and screenshot QA if available.
- Update project subplan statuses.

## Final First-Slice Product Decisions

These decisions are locked for the first guided-intake build slice:

- Use MCAT and GPA band selectors only. Do not add exact-score entry to the first applicant-facing intake slice.
- Show `states_to_avoid` as a visible optional control. It should create reversible hide/flag behavior, not destructive deletion.
- Collapse lower-priority guided result groups by default until clicked. Keep high-priority groups visible by default.

## Acceptance Criteria

- `#/intake` exists and works without server persistence.
- A first-time user can answer controlled questions and land on grouped school-review cards.
- Intake answers visibly explain the active lens.
- School cards show reasons, risks, missing data, and next action.
- Lower-priority groups are collapsed by default and can be expanded without losing local state.
- Existing rankings, profiles, compare, shortlist, hide/restore, application-list, dossier, and research workflows remain usable.
- Personal answers are browser-local and exportable.
- Publish-safe artifacts do not contain private answer values.
- Tests/build/validation pass.

## Child Plans

- [Intake Question Contract](site/guided_intake/01_intake_question_contract.md)
- [Answer To Ranking Context Mapping](site/guided_intake/02_answer_to_rank_context_mapping.md)
- [Guided Results and School Cards](site/guided_intake/03_guided_results_and_school_cards.md)
- [Local State, Exports, and Privacy](site/guided_intake/04_local_state_exports_and_privacy.md)
- [Admin Compatibility and Methodology](site/guided_intake/05_admin_compatibility_and_methodology.md)
- [QA and Validation](site/guided_intake/06_qa_and_validation.md)
- [Critical Review](site/guided_intake/CRITICAL_REVIEW.md)
