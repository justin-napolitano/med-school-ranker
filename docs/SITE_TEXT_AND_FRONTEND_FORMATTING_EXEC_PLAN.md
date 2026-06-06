# Site Text and Frontend Formatting Executive Plan

## Objective

Make the review site readable without spreadsheet literacy.

The site should keep deterministic data and stable internal contracts, but applicant-facing surfaces should use full labels, formatted numbers, clear score-card language, and card layouts that tolerate long school names, long labels, and missing-data explanations.

## Current Trigger

Guided result cards and school profile cards exposed several spreadsheet-shaped details:

- abbreviated labels such as `OOS` and `COA`;
- raw cost numbers such as `121282`;
- mixed `Dossier` and `Score Card` language;
- long labels and school names that could overflow card containers;
- intake checkbox updates that could move the left pane unexpectedly.

## Scope

This plan governs applicant-facing text and frontend formatting across:

- guided intake cards;
- rankings actions;
- score-card index and profile routes;
- compare cards;
- application-list and research-queue workflow copy;
- node-backed profile fact rows and metric cards;
- screenshot and interaction QA for card overflow and scroll stability.

## Non-Goals

- Do not rename stable internal CSVs, schema versions, route IDs, local-storage keys, or export filenames just to change displayed text.
- Do not redesign the full visual system in this pass.
- Do not change scoring formulas, rank logic, or source normalization.
- Do not solve missing MCAT/GPA coverage here; track that separately as a data coverage plan.

## Decisions

- Use `Score Card` as the applicant-facing term for per-school review pages and editable local school notes.
- Keep internal `dossier` data names stable until a deliberate persistence/import migration exists.
- Use full labels for cost fields:
  - `In-state estimated cost`
  - `Out-of-state estimated cost`
  - `Cost used for selected score`
- Format cost-like values as whole-dollar currency.
- Preserve same-route scroll position for intake interactions, but open new routes at the top of the page.
- Prefer display-label mappings over ad hoc label strings scattered through the site.

## Work Slices

1. Label and copy contract
   - Define approved applicant-facing labels.
   - Replace abbreviations where they reduce clarity.
   - Keep internal names stable unless a migration plan exists.

2. Numeric and currency formatting
   - Format all cost-like values as currency.
   - Add separate in-state and out-of-state cost rows where review cards discuss cost.
   - Keep missing values explicit as `Missing`.

3. Card and text overflow hardening
   - Ensure card, metric, fact-row, badge, and compare text wraps inside containers.
   - Add mobile single-column fallbacks for label/value rows.
   - Preserve stable card dimensions where possible.

4. Score-card language migration
   - Change visible `Dossier` copy to `Score Card`.
   - Keep export schemas and filenames backward compatible.
   - Verify navigation, rankings actions, profile tools, research queue, and application list copy.

5. Interaction QA
   - Verify profile links open at the top.
   - Verify intake left/right panes scroll independently on desktop.
   - Verify intake checkbox changes preserve current pane scroll.
   - Capture screenshot QA for desktop and mobile card surfaces before larger design work.

## Acceptance Criteria

- No applicant-facing label uses `OOS`, `COA`, or `Dossier`.
- School cards show both in-state and out-of-state estimated costs when available.
- Cost values render like `$121,282`, not `121282`.
- Long school names, labels, notes, and missing-data chips stay inside cards on desktop and mobile.
- Intake state changes do not jump the left pane.
- Navigation to a school score card opens at the top of that route.
- Existing tests, site build, validation, and screenshot QA pass.

## Subplans

- [Label and Copy Contract](site/text_frontend_formatting/01_label_and_copy_contract.md)
- [Numeric and Currency Formatting](site/text_frontend_formatting/02_numeric_and_currency_formatting.md)
- [Card Layout and Overflow](site/text_frontend_formatting/03_card_layout_and_overflow.md)
- [Score-Card Language Migration](site/text_frontend_formatting/04_score_card_language_migration.md)
- [QA and Accessibility](site/text_frontend_formatting/05_qa_and_accessibility.md)
- [Critical Review](site/text_frontend_formatting/CRITICAL_REVIEW.md)

