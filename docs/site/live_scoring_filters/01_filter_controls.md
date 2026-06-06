# Filter Controls

## Objective

Replace weak one-off filters with explicit exclusion controls that fit real application-list workflow.

## Controls

Build My List sidebar should include:

- search by school/city/state;
- degree type;
- home state;
- excluded states multi-select;
- excluded cities dropdown built from known city/state pairs;
- institution ownership dropdown:
  - All;
  - Public;
  - Private;
  - Unknown;
- cost availability;
- score-screen fit;
- Not Interested state handled as a separate local list.

Data-confidence/source-confidence is not a filter for now. It may appear as read-only transparency in methodology, school cards, or profile details, but it must not hide schools from Build My List.

## State Exclusions

State exclusions should:

- use USPS state abbreviations and full labels;
- support multiple states;
- show selected states as removable chips;
- remove matching schools from Build My List;
- not delete schools from local lists or payload;
- persist in local storage with other preferences.

## City Exclusions

City exclusions should:

- use city/state labels to avoid ambiguous cities;
- support multiple cities from a dropdown list generated from the payload;
- show selected cities as removable chips;
- remove matching schools from Build My List;
- persist locally.

## Ownership Filter

The user wants to search/filter public and private schools.

Current data gap:

- `data/school_master.csv` does not currently include `ownership_type`;
- the product payload does not currently expose public/private ownership labels;
- older static-site scaffolding mentions ownership lists, but those are provisional until `ownership_type` is populated.

Implementation rule:

- if source-backed `ownership_type` exists, expose Public/Private/Unknown filtering;
- if it does not exist, expose the control as Unknown-only or hide it behind a disabled note;
- do not infer ownership from school name;
- do not make public/private quality claims.

## Texas Quick Exclusion

The Build My List menu should support excluding Texas quickly because the user explicitly asked for it.

Implementation options:

- include Texas in the state exclusion dropdown like every other state;
- add a quick chip/button: `Exclude TX`;
- once selected, show `TX` as a removable exclusion chip.

## Counts

The feed should show:

```text
50 shown / 142 eligible / 233 total
```

Definitions:

- total: all payload schools;
- eligible: after filters, state/city/ownership exclusions, and Not Interested;
- shown: currently rendered after pagination/load-more.

## Edge Cases

- If every school is filtered out, show an empty state with controls to clear exclusions.
- If a school is already Interested/Applying and its state is excluded, keep it in those local lists but remove it from Build My List.
- Exclusion controls must be reversible.
- Data-confidence/source-confidence must not appear as a filter option.

## Done Criteria

- State and city exclusions work without page reload.
- Counts are transparent.
- Empty states explain which controls can restore schools.
- No data-confidence filter exists in the Build My List menu.
