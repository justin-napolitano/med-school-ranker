# Site UX Review and School Research Workflow Plan

## Objective

Improve the static site from a technically useful review surface into a practical applicant workflow:

- visually review the site with screenshots;
- fix obvious layout, clarity, and interaction problems;
- make it easy to hide or restore schools from the working view without deleting them;
- create school dossier/profile surfaces so applicants can review and fill structured school research in one place;
- keep all user edits transparent, reversible, and exportable.

## Current Context

The site now has:

- rankings;
- deterministic scoring methodology;
- score contribution audit rows;
- an MD-only AAMC-band selector proof of concept;
- school detail/audit surfaces.

The next issue is usability. The site needs a disciplined visual QA loop and an applicant-friendly research workflow.

## Non-Goals

- Do not add a backend.
- Do not add login/authentication.
- Do not silently delete schools from the universe.
- Do not write local browser edits back to source CSVs in the first pass.
- Do not implement predictive admissions probability.
- Do not scrape new data for this phase.
- Do not include private profile data in public outputs.

## Design Principles

- Keep the full school universe auditable.
- Hiding a school is a reversible view preference, not a data deletion.
- Every hidden/excluded school should retain a reason and be restorable.
- A school dossier should combine precomputed data with structured fields that applicants can fill over time.
- Missing dossier fields should become research prompts, not empty unexplained cells.
- Browser-local changes should be exportable as CSV.
- Screenshot evidence should drive UI changes; do not polish blindly.
- Screenshot QA is required before feature implementation in this pass.
- Browser-local state means in-memory state for the first pass; persistent browser storage requires an explicit privacy/clear-state design later.
- MD-only applies only to the existing AAMC-band reranking selector. Dossiers and hide/restore controls should cover the full active school universe.

## Required MVP

The first implementation pass should complete these before expanding scope:

1. Capture required screenshots and record findings.
2. Fix high-impact visual/clarity issues identified by screenshots.
3. Add reversible hide/restore controls and hidden-school review.
4. Add minimal dossier index/detail for all active schools.
5. Add CSV exports for visibility state and dossier edits.

Follow-up work:

- richer research queue;
- deeper dossier editing;
- persistent local storage;
- import/writeback of exported edits;
- advanced shortlist/application workflow.

## Headless Slice Plan

Run this work as separate commits:

1. [Slice A: Screenshot QA and Triage](site/ux_review/HEADLESS_SLICE_A_SCREENSHOT_QA.md)
2. [Slice B: School Visibility Controls](site/ux_review/HEADLESS_SLICE_B_VISIBILITY_CONTROLS.md)
3. [Slice C: Minimal School Dossiers](site/ux_review/HEADLESS_SLICE_C_MINIMAL_DOSSIERS.md)
4. [Slice D: Dossier Local Edits and Export](site/ux_review/HEADLESS_SLICE_D_DOSSIER_EDITS_EXPORT.md)
5. [Slice E: Research Queue](site/ux_review/HEADLESS_SLICE_E_RESEARCH_QUEUE.md)

Do not combine slices unless the user explicitly asks. Slice A is the immediate next execution target.

## Phase Sequence

### Phase 1: Headless Visual QA

- Serve the generated site locally.
- Capture desktop and mobile screenshots for key routes/states.
- Record layout issues, confusing labels, broken controls, oversized tables, text overflow, and missing states.
- Apply small UI fixes that improve clarity without changing scoring behavior.
- Rebuild and retake screenshots.

### Phase 2: School Visibility Controls

- Add controls to hide a school from the current working view.
- Add restore controls and a hidden-school review drawer/table.
- Add visibility filters:
  - all schools;
  - visible only;
  - hidden only;
  - hard-no;
  - shortlist/research candidates if available.
- Store changes in in-memory browser state first.
- Export visibility changes as CSV.

### Phase 3: School Dossier Profiles

- Add a school profiles/dossiers route or tab listing all schools.
- Each school gets a dossier page or detail panel with precomputed fields:
  - identity and location;
  - Decision Rank and score summary;
  - admissions fit;
  - MCAT/GPA context;
  - cost/tuition context;
  - requirements and policies;
  - source confidence;
  - score contribution summary;
  - missing research prompts.
- Add structured editable local fields for applicant research:
  - interest level;
  - research status;
  - notes;
  - fit concerns;
  - outreach/interview notes;
  - final decision status.
- Export dossier edits as CSV.

### Phase 4: Research Workflow

- Add a dashboard/work queue for schools needing review.
- Let users filter by missing dossier sections, rank band, admissions tier, and visibility state.
- Show "next research action" for each school.
- Keep source links and confidence visible near every precomputed fact.

## Target Outputs

Potential generated/static outputs:

```text
outputs/site_qa/screenshots/
outputs/site_qa/ux_review_findings.csv
outputs/school_dossiers.csv
outputs/site/data/school_dossiers.json
outputs/site/data/school_visibility_defaults.json
```

Potential browser-exported files:

```text
school_visibility_export.csv
school_dossier_edits_export.csv
selected_profile_rankings_export.csv
```

Every browser-exported CSV should include:

```text
export_schema_version
exported_at
school_id
```

## Child Plans

- [Headless Site UX Review Execution Plan](HEADLESS_SITE_UX_REVIEW_EXECUTION_PLAN.md)
- [Visual QA Screenshots](site/ux_review/01_visual_qa_screenshots.md)
- [School Visibility Controls](site/ux_review/02_school_visibility_controls.md)
- [School Dossier Profiles](site/ux_review/03_school_dossier_profiles.md)
- [Research Workflow and Exports](site/ux_review/04_research_workflow_and_exports.md)
- [Slice A: Screenshot QA and Triage](site/ux_review/HEADLESS_SLICE_A_SCREENSHOT_QA.md)
- [Slice B: School Visibility Controls](site/ux_review/HEADLESS_SLICE_B_VISIBILITY_CONTROLS.md)
- [Slice C: Minimal School Dossiers](site/ux_review/HEADLESS_SLICE_C_MINIMAL_DOSSIERS.md)
- [Slice D: Dossier Local Edits and Export](site/ux_review/HEADLESS_SLICE_D_DOSSIER_EDITS_EXPORT.md)
- [Slice E: Research Queue](site/ux_review/HEADLESS_SLICE_E_RESEARCH_QUEUE.md)

## Acceptance Criteria

- Screenshots exist for the core user routes before and after changes.
- Rankings page has reversible hide/restore controls.
- Hidden schools can be reviewed and exported.
- School dossier/profile route lists every school and opens a decision-useful dossier.
- Dossier fields distinguish precomputed source-backed facts from user-entered research.
- Browser-local edits can be exported.
- Build/test/privacy checks still pass.
