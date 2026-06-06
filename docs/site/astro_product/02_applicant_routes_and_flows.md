# Applicant Routes And Flows

## Route Inventory

```text
/                  Build My List
/interested        Browser-local shortlist, max 50
/applying          Browser-local final application list, max 25
/not-interested    Browser-local removal list
/schools/[slug]    School profile
/compare           Side-by-side comparison for selected schools
/methodology       Plain-language scoring and caveats
/admin             Admin/Data status, separate from applicant product
```

## First Screen

`/` is Build My List. It should feel like guided onboarding and list-building, not a dashboard. It collects profile/preferences such as MCAT, GPA, home state, degree type, region, cost sensitivity, and reversible exclusions.

The initial feed should show deterministic recommendation cards immediately, even before inputs are complete, with missing-input caveats.

## Build My List Behavior

Build My List sorts by generated `decision_rank`, then `overall_rank`, then name until live scoring is implemented. Controls may filter by degree, state, score-screen fit, cost availability, and reversible exclusions without changing the source payload. Data-confidence/source-confidence is transparency-only for now, not a filter. Schools marked Not Interested are removed from this feed until they are removed from the Not Interested tab.

## Local Lists

Interested and Applying are independent browser-local lists:

- Interested cap: 50 schools.
- Applying cap: 25 schools.
- Not Interested has no cap and removes schools from Build My List.
- Marking a school Not Interested removes it from Interested and Applying.
- Adding to Applying may also leave the school in Interested, but the UI should make the final-list state clear.
- Export is local JSON or CSV and must not write private state to repo files.

## Compare

Compare uses selected schools from local state or URL query/hash state. Side-by-side cards should favor school name, location, score-screen fit, MCAT/GPA, estimated cost, rank context, and source/missing-data notes.
