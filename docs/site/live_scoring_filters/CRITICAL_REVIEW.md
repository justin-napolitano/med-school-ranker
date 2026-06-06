# Critical Review

## Finding 1: Current Inputs Overpromise Unless Labels Change

The current Build My List inputs can imply that changing MCAT/GPA/state changes the rank. Before this slice, they only affect filters and score-screen labels. The implementation must make the live rank real or label the current rank as baseline only.

Severity: high.

## Finding 2: `Your Rank` Can Be Misread As Admissions Chance

Any personalized ranking can be mistaken for admit likelihood. The UI must say that `Your Rank` is a deterministic fit ranking based on selected components, not a school-specific admissions probability.

Severity: high.

## Finding 3: Missing Data Can Distort Live Scores

If missing cost/OOS/stats fields are silently treated as zero, schools with missing data will be unfairly penalized. Missing components must be excluded from the denominator and reported as coverage warnings.

Severity: high.

## Finding 4: Too Many Weight Controls Can Make The Product Feel Like A Spreadsheet

The menu should expose a small number of meaningful components first. Detailed component tuning can come later.

Severity: medium.

## Finding 5: Excluding States/Cities Must Be Reversible

Exclusions should behave like filters, not destructive state. Schools already in Interested/Applying should remain there even if excluded from Build My List.

Severity: medium.

## Finding 6: Preset Labels Can Become Claims

Presets like `Safety` or `Likely Admit` would be misleading. Use neutral labels such as `Balanced`, `Cost-aware`, and `Florida-first`.

Severity: medium.

## Finding 7: Baseline And Live Rank Need Visual Separation

If both ranks appear with similar styling, users may not know which is generated and which is current. Cards should give `Your Rank` primary emphasis and `Baseline Rank` secondary emphasis with methodology links.

Severity: medium.

## Finding 8: Public/Private Filtering Needs Source-Backed Ownership Data

The current product payload does not expose `ownership_type`. Public/private filtering is desired, but the worker must either add source-backed ownership labels to the payload or treat ownership as Unknown. It must not infer ownership from school names or make public/private quality claims.

Severity: high.

## Finding 9: Data-Confidence Filtering Is Out Of Scope For This Slice

The user explicitly removed data-confidence filters for now. Confidence/source-quality fields can remain visible for transparency, but they must not be used to exclude schools, rank schools, or clutter the Build My List controls.

Severity: medium.

## Open Design Questions

- How many secondary live weight controls should be exposed after MCAT, GPA, state/residency, cost, and baseline attendance?
- Should ownership data be seeded in this slice or deferred with an Unknown-only filter?
- Should defaults be Florida-first, State-first, Balanced, or last-used local state?

Resolved decisions for this slice:

- City exclusion uses a dropdown.
- State exclusion is state-first.
- Public/private search/filter is desired, but only with source-backed ownership labels; otherwise keep Unknown-only/disabled.
- Texas quick exclusion should be available.
- Not Interested is a simple button plus local page.
- `Your Rank` is primary and `Baseline Rank` is secondary.
- Data-confidence/source-confidence is not a filter.
