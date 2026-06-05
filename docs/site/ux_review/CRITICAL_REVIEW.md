# Site UX Review Critical Review

## Findings

### High: The Execution Plan Was Too Broad For One Headless Pass

The first draft combined screenshot QA, visual fixes, hide/restore controls, dossiers, research queue, and multiple exports into one pass.

Risk:

- a worker could partially implement several surfaces without one coherent workflow being usable;
- screenshot QA could be skipped in favor of feature work;
- dossiers could become a large untested UI surface.

Resolution:

- Define a required MVP slice:
  1. screenshot QA;
  2. high-impact layout/clarity fixes;
  3. reversible hide/restore controls;
  4. minimal dossier index/detail shell;
  5. visibility and dossier CSV export.
- Treat research queue and deeper dossier editing as follow-up unless the MVP is complete and verified.

### High: Browser-Local State Needed A Privacy Policy

The plan said browser-local state but did not specify whether that meant memory, `sessionStorage`, or `localStorage`.

Risk:

- local edits could persist on a shared machine without clear user intent;
- private notes could remain in browser storage unexpectedly.

Resolution:

- First pass should use in-memory state.
- If storage persistence is added later, it must include a visible privacy label, clear/reset control, and export/import policy.

### High: Dossier Scope Needed A Source-Of-Truth Boundary

The dossier plan mixed precomputed facts and user-entered research fields.

Risk:

- local edits could be confused with source-backed facts;
- exported user notes could be mistaken for normalized source data.

Resolution:

- Dossier UI must visually separate generated facts from local user research fields.
- Generated dossier data should come from existing normalized/ranking outputs.
- User-entered dossier edits are browser-local and exported separately.
- Import/writeback remains future scope.

### Medium: Screenshot Tooling Needed A Concrete Stop Rule

The plan required screenshots but did not define what happens if tooling is missing beyond a general blocker.

Risk:

- a worker might claim visual QA passed without image evidence.

Resolution:

- Screenshots are required for Phase 1 completion.
- If no screenshot mechanism is available, the worker must stop before feature implementation and report the tooling gap.
- A text-only DOM/HTML review is not a substitute for screenshot QA for this pass.

### Medium: Export Schemas Needed Versioning

The plan named CSV exports but did not require schema/version fields.

Risk:

- exported files become hard to import or reconcile later.

Resolution:

- Browser exports must include `export_schema_version`, `exported_at`, and stable `school_id` fields.
- Exported edit rows should include only non-default local state.

### Medium: MD Selector Scope Could Confuse Dossier Scope

The existing selector proof of concept is MD-only, but the school dossier workflow should cover the full active school universe.

Risk:

- a worker could mistakenly omit DO schools from dossiers.

Resolution:

- MD-only applies only to the AAMC-band reranking selector.
- Visibility controls and dossier index should include every active school unless a user filter says otherwise.

## Required Plan Updates

- Add an MVP/follow-up split to the headless execution plan.
- Define browser-local state as in-memory for the first pass.
- Add export schema fields.
- Clarify screenshots are required before implementation.
- Clarify dossiers cover the full active school universe.
