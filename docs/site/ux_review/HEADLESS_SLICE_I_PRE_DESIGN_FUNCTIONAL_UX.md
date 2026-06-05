# Headless Slice I: Pre-Design Functional UX Consolidation

## Objective

Make the review site functionally complete enough to begin visual design work.

This slice should consolidate the existing ranking, dossier, research queue, compare, and final application list workflows into a coherent applicant-review tool. It is a functional UX slice, not a full visual redesign.

## Why This Slice Exists

The site now has the core primitives:

- rankings;
- school visibility controls;
- school dossiers;
- browser export and CSV import for reviewer state;
- research queue;
- final application list route;
- deterministic final application list builder.

The remaining problem is workflow friction. A user can do the work, but too much of it requires jumping between views or understanding implementation boundaries. Before designing the site visually, the functional flows should be clear enough that design decisions are based on real behavior instead of placeholders.

## Prerequisites

The following should already be implemented and committed:

- static site product/admin route scaffold;
- visibility controls and export;
- school dossiers;
- dossier edit export and reviewer-state import;
- research queue;
- final application list route and `med-school-build-final-list`;
- generated workbook/site/upload bundle path.

Start from a clean worktree unless the user explicitly says otherwise.

## Controlling Context

Read in this order:

1. `docs/HEADLESS_WORKER_RUNBOOK.md`
2. `docs/SITE_UX_REVIEW_AND_RESEARCH_WORKFLOW_PLAN.md`
3. `docs/HEADLESS_SITE_UX_REVIEW_EXECUTION_PLAN.md`
4. `docs/site/product_rebuild/02_rankings_and_list_builder.md`
5. `docs/site/product_rebuild/03_school_profiles.md`
6. `docs/site/product_rebuild/06_visual_reporting_quality.md`
7. `src/med_school_ranker/site.py`
8. `src/med_school_ranker/final_list.py`
9. `tests/`

Use committed docs and code as the source of truth. Do not infer requirements from older chat context if it conflicts with committed files.

## Scope

Do:

- update plan/subplan status rows so the roadmap reflects implemented UX slices;
- improve Rankings and Application List so users can set review/application decisions without bouncing through profile pages;
- make Application List the working shortlist view for active, cut, and unselected schools;
- upgrade Compare into a real side-by-side school review surface;
- improve school profile pages into clearer dossier-style pages with action controls and decision-useful sections;
- keep browser edits in in-memory JavaScript state unless using existing CSV import/export paths;
- keep browser exports compatible with existing import tools and final-list builder;
- update tests for route rendering, controls, export schema, and final-list consistency;
- regenerate workbook, site, upload zip, and data quality report.

Do not:

- perform full visual redesign;
- add a framework migration;
- add backend storage, authentication, or database persistence;
- use `localStorage` or `sessionStorage` unless a visible privacy label and clear/reset control are included;
- scrape, download, or infer new school data;
- change deterministic scoring formulas;
- implement predictive admissions probability;
- remove MD or DO schools from the universe;
- commit private applicant data or private-derived outputs;
- overwrite manual reviewer notes without explicit preservation logic.

## Required Functional Outcomes

### 1. Plan Index Cleanup

Update `data/project_subplans.csv` so UX slice statuses do not mislead future workers.

At minimum:

- mark completed/implemented UX slices as implemented or completed;
- add this Slice I row;
- keep the next action for Slice I focused on functional UX, not visual polish.

Do not invent completed work that is not actually present in code.

### 2. Rankings Inline Review Controls

Rankings should support quick triage without requiring a profile-page visit for every school.

Required controls:

- hide/restore;
- application decision status;
- interest level if there is enough room without making the table unusable;
- open profile/dossier;
- optional add-to-compare control.

Required behavior:

- controls update browser in-memory dossier/visibility state;
- exports reflect changed state;
- filtering and global search continue to work;
- missing values remain blank or labeled `Missing`, never coerced to zero.

### 3. Application List as Working Shortlist

The Application List route should become the primary narrowing workspace.

Required improvements:

- show active shortlist, cut/excluded, and unselected views clearly;
- allow inline application decision changes;
- allow inline interest changes;
- expose target count progress toward 25-35 applications;
- keep download/export actions visible;
- keep the route understandable when the active list is empty.

The generated `data/final_application_list.csv` must still come from persisted CSV state through `uv run med-school-build-final-list`. Browser-only changes should remain export/import based unless a separate persistence design is approved.

### 4. Compare Page

Upgrade `#/compare` from a placeholder table into a useful side-by-side comparison tool.

Minimum acceptable behavior:

- user can select 2-4 schools from the current school universe;
- selected schools render side by side;
- comparison groups include identity, rank, admissions fit, MCAT/GPA, cost, research/dossier status, location, notes, and source confidence when available;
- each selected school links to its profile;
- missing values render as `Missing`;
- no private data appears in publish-safe mode.

Optional if simple:

- add from rankings/application list into compare state;
- preserve selected compare IDs in hash query state.

Do not block the slice on advanced comparison persistence.

### 5. School Profiles as Dossiers

Profile pages should be reorganized enough that a reviewer can understand and act from one screen.

Required sections:

- profile header with rank, degree, city/state, visibility, and application decision;
- quick action controls for hide/restore, research status, interest, and application decision;
- admissions fit and MCAT/GPA context;
- cost/debt context;
- source confidence and missing-data warnings;
- local dossier notes and subjective scores;
- final-list/research next action.

This is functional information architecture, not final styling.

### 6. Browser Export and CLI Alignment

The browser and CLI now share final-list concepts but implement them in different languages.

The worker must keep these aligned:

- active application statuses;
- excluded/cut statuses;
- priority labels;
- final application list export columns;
- application service derivation for MD/DO;
- rationale behavior.

If browser logic changes, update `src/med_school_ranker/final_list.py` and tests when relevant.

## Acceptance Criteria

- A reviewer can triage schools from Rankings without opening every profile.
- A reviewer can use Application List as the main shortlist/cut workspace.
- A reviewer can compare 2-4 selected schools side by side.
- A reviewer can make the key dossier/application decision updates from the profile page.
- Existing CSV export/import path still works.
- `uv run med-school-build-final-list` still produces deterministic output from persisted CSV state.
- Publish-safe mode still excludes admin/private payloads.
- Site builds and tests pass.
- The commit includes regenerated public artifacts when generated outputs changed.

## Verification Commands

Run before edits:

```bash
cd /Users/justin/repos/med-school-ranker
git status --short --branch
git status --short --ignored data/manual/private data/private outputs/private
uv run pytest
uv run med-school-build-all
```

Run after implementation:

```bash
uv run pytest
uv run med-school-validate
uv run med-school-build-all
uv run med-school-build-final-list
git diff --check
git status --short --ignored data/manual/private data/private outputs/private
```

Privacy check:

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('med-school-ranker-upload.zip'); bad=[n for n in z.namelist() if n.startswith(('data/manual/private/','data/private/','outputs/private/'))]; print(len(bad)); raise SystemExit(1 if bad else 0)"
```

Local server smoke check:

```bash
python3 -m http.server 8766 -d outputs/site
curl -sI http://localhost:8766/
```

If a server is already running on `8766`, reuse it or choose another local port and report the URL.

Manual/browser checks:

- `#/rankings`: inline controls work and exports update.
- `#/application-list`: active/cut/unselected filters are understandable.
- `#/compare`: 2-4 school selection and side-by-side rendering works.
- `#/schools/:slug`: dossier controls and grouped sections work.
- `#/admin` remains separate from product-facing routes.

## Suggested Branch and Commit

Suggested branch:

```bash
git switch -c impl-pre-design-functional-ux
```

If the branch already exists, switch to it only if the worktree is clean or the existing changes are clearly related.

Suggested commit message:

```text
Improve pre-design review workflows
```

## Headless Prompt

Use this prompt for the execution worker:

```text
You are working in /Users/justin/repos/med-school-ranker.

Execute docs/site/ux_review/HEADLESS_SLICE_I_PRE_DESIGN_FUNCTIONAL_UX.md end to end.

Start from a clean status check and create a clean implementation branch if needed. This is a functional UX consolidation slice before visual design. Improve Rankings inline review controls, Application List shortlist workflow, Compare side-by-side review, and school profile dossier actions. Update the plan index so implemented UX slices and Slice I status are accurate.

Do not perform a full visual redesign. Do not scrape or download data. Do not change scoring formulas. Do not implement predictive admissions probability. Do not add backend persistence or private data to committed outputs. Keep browser state export/import compatible with the existing reviewer-state and final-list builder paths.

Regenerate workbook, site, upload zip, and data quality outputs. Add or update tests. Run uv run pytest, uv run med-school-validate, uv run med-school-build-all, uv run med-school-build-final-list, git diff --check, and the upload-bundle privacy check. Commit only public-safe code/docs/data/generated outputs.
```

## Critical Review: Gaps and Drift Risks

### High: Browser state and persisted CSV state can diverge

Browser edits are in-memory until exported and imported. The Application List page can therefore show browser-current decisions that `data/final_application_list.csv` does not yet contain.

Mitigation:

- keep visible copy that the repo CSV is built from persisted reviewer-state CSVs;
- keep export buttons near inline controls;
- do not imply that browser-only edits have been written to the repo.

### High: Final-list logic is duplicated in JavaScript and Python

The site export and `med-school-build-final-list` both define active statuses, excluded statuses, priorities, and final-list columns.

Mitigation:

- update tests when changing either side;
- keep shared constants textually aligned;
- avoid new status labels unless both paths support them.

### High: Scope could drift into visual redesign

The user wants to talk design soon, but this slice exists to make flows complete before design.

Mitigation:

- only do layout polish needed to make controls understandable;
- defer typography, color system, and page-level visual redesign to the next design slice.

### Medium: Compare can become too ambitious

Compare could expand into scoring lenses, saved compare sets, notes editing, or route-persistent state.

Mitigation:

- implement only 2-4 selected schools and side-by-side decision fields;
- treat hash persistence as optional;
- no saved compare storage in this slice.

### Medium: Plan index drift can reappear

Generated site/workbook surfaces use `data/project_subplans.csv`; stale statuses can mislead the user and headless workers.

Mitigation:

- update statuses as part of this slice;
- regenerate site/workbook/upload artifacts after CSV changes.

### Medium: Publish-safe payload regressions are easy when adding richer profiles

More profile and compare data increases the chance of leaking admin/private fields into publish-safe output.

Mitigation:

- keep publish-safe tests;
- inspect payload groups;
- run privacy zip check before commit.

### Medium: Empty active application list can look broken

The current real repo may have no persisted active decisions yet.

Mitigation:

- design empty states explicitly;
- use tests/fixtures for active rows rather than committing fake real decisions.

### Low: MD/DO application service assumptions are useful but coarse

The builder maps MD to AMCAS and DO to AACOMAS. Campus-specific behavior may need later review.

Mitigation:

- keep existing application-unit assumptions visible;
- do not collapse campuses or alter school universe in this slice.

## Done Criteria

- Slice I plan has been followed.
- UX flows are functionally ready for a design discussion.
- Tests/build/privacy checks pass.
- Generated artifacts are refreshed.
- Commit is created with a concise summary and residual risks.
