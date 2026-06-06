# Critical Review

## Finding 1: Display copy can drift from data contracts

Risk: Renaming visible `Dossier` language to `Score Card` could accidentally rename CSVs, route IDs, local-storage keys, or export schemas.

Resolution: Keep internal names stable in this pass. Rename only visible text unless a separate migration plan exists.

## Finding 2: Formatting can hide missing or low-confidence data

Risk: Pretty cards could make incomplete source coverage look more complete than it is.

Resolution: Preserve `Missing` labels, data quality bands, and source confidence. Formatting should clarify values, not suppress gaps.

## Finding 3: Full labels increase layout pressure

Risk: Replacing abbreviations with full labels can make cards overflow, especially on mobile.

Resolution: Treat label changes and card overflow as one implementation slice. Require wrapping, responsive fact rows, and screenshot QA.

## Finding 4: Cost fields can be ambiguous

Risk: In-state cost, out-of-state cost, tuition-only rows, and scoring cost basis are related but not identical.

Resolution: Display separate rows with explicit names. Do not collapse them into one generic `Cost` row.

## Finding 5: Same-route rerenders can feel like broken scrolling

Risk: Updating intake checkboxes re-renders the form and can move the user's scroll position.

Resolution: Preserve scroll for same-route intake updates. Continue resetting scroll for actual route changes.

## Finding 6: Screenshot QA alone is insufficient

Risk: Screenshots can show visual state but miss broken exports, schema regressions, or route behavior.

Resolution: Pair screenshot QA with unit tests, validation, generated-output review, and targeted browser smoke checks.

