# Route Views And Profile Contract

## Objective

Define the applicant route views rendered by the app shell.

## Build My List

Reuse `RecommendationFeed`.

Required behavior:

- same caveat copy;
- same local filters and scoring controls;
- same card actions;
- same limits/load-more behavior;
- same Not Interested exclusion behavior.

## Interested And Applying

Reuse `LocalListPage`.

Required behavior:

- Interested cap remains 50;
- Applying cap remains 25;
- selected-list reweighting controls remain visible;
- cards sort by live score where available;
- export still works;
- empty state links back through app-shell navigation.

## Not Interested

Reuse `LocalListPage`.

Required behavior:

- no ranking control panel unless already present by product decision;
- page shows schools removed from Build My List;
- restoring from card actions works.

## Compare

Reuse `CompareApp`.

Required behavior:

- selected compare schools persist through app navigation;
- add-school picker works;
- remove button works;
- profile links route through app shell.

## Scoring

Reuse `ScoringAssumptionsApp`.

Required behavior:

- MD-only scope remains visible;
- assumptions table remains;
- weights/formulas table remains;
- selected school dropdown works;
- rank movement table remains;
- zero-weight and missing-data policies remain visible;
- MCAT/GPA/weight changes update visible values.

## Methodology

Add a React view:

```text
frontend/src/components/AppMethodologyView.tsx
```

The view should preserve existing methodology content from `frontend/src/pages/methodology.astro`.

Required behavior:

- keep live scoring formulas;
- keep missing-data policy;
- keep zero-weight policy;
- keep DO separate-scope caveat;
- keep local-state privacy;
- render generated methodology rows from payload.

## School Profile

Add a React view:

```text
frontend/src/components/AppSchoolProfileView.tsx
```

The view should preserve existing profile content from `frontend/src/pages/schools/[slug].astro`.

Required behavior:

- use current browser-local preferences for score-screen fit, not only `defaultPreferences`;
- include Interested, Applying, Not Interested, and Compare action buttons using the same local state as school cards;
- show current selected status for those actions;
- keep profile actions scoped to browser-local state only;
- show rank label and baseline rank;
- show MCAT/GPA context;
- show cost context;
- show Why It Ranks Here;
- show data status;
- show source link as a normal external link;
- show a Not Found state for unknown slug;
- scroll to top when entering a profile route from a card.

## Page Headers

The shell owns page headers so route changes feel consistent.

Each route should have:

- eyebrow;
- H1;
- short caveated description.

Do not add marketing hero copy. This is still a working applicant tool.

## Acceptance Criteria

- All current applicant views are represented inside the shell.
- No applicant workflow feature is lost.
- Existing caveats survive the migration.
