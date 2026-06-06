# Critical Review

## Finding 1: The Current Score Is Deterministic But Not Human-Legible

`Your Rank` updates, but the user cannot easily inspect the exact denominator, component weights, missing components, and weighted contribution.

Resolution:

- add an assumptions table;
- add a selected-school score breakdown table;
- show present-components-only denominator;
- show missing components as rows, not hidden warnings.

## Finding 2: A More Detailed Score Can Look More Authoritative Than It Is

Tables can make the model feel precise even when the underlying data is partial.

Resolution:

- keep the caveat visible;
- show coverage near every score;
- label missing values clearly;
- keep `Baseline Rank` separate;
- do not use admissions probability language.

## Finding 3: User Inputs Are Private-Derived Even If The Site Is Public

The public site can safely let a user enter MCAT/GPA locally, but committed defaults must not expose a real private profile.

Resolution:

- no committed private defaults;
- browser-local state only;
- no server writeback;
- no public payload mutation from user inputs.

## Finding 4: Too Many Controls Could Make This Worse

If every possible future factor becomes a slider now, the page will feel like a spreadsheet again.

Resolution:

- only expose current live components in the first pass;
- list future components as out of scope;
- keep subjective categories for later after their data contracts exist.

## Finding 5: Present-Components-Only Denominator Is Easy To Misread

A high score with low coverage can look better than it should.

Resolution:

- display coverage next to every score;
- include missing rows in breakdown;
- add plain text: missing values are excluded, not scored as zero;
- keep rank confidence/coverage warnings visible.

## Finding 6: Build My List And Scoring Page Could Drift

If the Scoring page has separate controls or formulas, users will not know which result to trust.

Resolution:

- share the existing local state hook;
- reuse `live-scoring.ts`;
- do not duplicate scoring formulas in React components;
- add smoke coverage for both pages.

## Finding 7: Mixing MD And DO Scoring Would Break Context

The first scoring workspace is based on current live-scoring assumptions and MD-heavy MCAT/GPA context. Mixing DO schools into the same rank table could make the assumptions feel more precise than they are.

Resolution:

- make `/scoring/` MD-only in the first implementation;
- exclude DO schools from dropdowns and rank movement tables;
- explain that DO scoring needs a separate future flow;
- do not make quality claims about MD vs DO.

## Finding 8: Baseline Attendance Context Could Remain A Black Box

The existing baseline attendance context component is useful to inspect, but its label is too opaque.

Resolution:

- relabel it as `Generated school context`;
- show it in assumptions, formulas, and score breakdown;
- make it easy to set its weight to zero;
- show `Not included: weight is 0` distinctly from missing data.

## Open Decisions

These can be changed before implementation, but the default plan resolves them:

- route label: default `Scoring`;
- default selected school: current top `Your Rank`;
- private profile defaults: none committed;
- scenario compare table: optional if time allows;
- export: optional later slice.
