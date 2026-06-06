# Profile And Compare Integration

## Objective

Make school-specific overrides visible wherever a user would expect to evaluate a school.

## School Profile

Update profile route behavior:

- show `Global Score`;
- show `Adjusted Score` when override exists;
- show `Override applied` chip when override exists;
- add `Edit scoring override` action;
- add `Reset to global` action when override exists;
- include concise component-level explanation for the adjusted score.

Do not remove existing baseline rank/source/data-status sections.

## Compare

Compare should surface override state without becoming a full scoring workspace.

For each compared school:

- show global score/rank;
- show adjusted score/rank when override exists;
- show override chip;
- offer profile link for detailed override editing.

Do not put full override editors inside every compare card in the first slice. That would make compare too noisy.

## Interested And Applying Lists

Interested and Applying cards should show:

- override chip;
- adjusted score if present;
- profile link or edit link.

First slice can route editing through the profile or school browser.

## Build My List

Build My List should remain the primary ranking/list-building surface.

First slice options:

- show override chip and adjusted score if an override exists;
- leave default ranking based on global score unless an explicit adjusted-rank toggle is added.

Do not surprise the user by silently reordering Build My List based on hidden per-school overrides.

## Acceptance Criteria

- Override applied on `/schools/` is visible on `/schools/:slug/`.
- Profile reset removes the chip and adjusted score on browser/profile/list pages.
- Compare shows adjusted context without full editor clutter.
- No page claims adjusted score is an admissions probability.

