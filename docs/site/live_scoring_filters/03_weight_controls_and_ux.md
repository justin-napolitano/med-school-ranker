# Weight Controls And UX

## Objective

Let users adjust what matters without making the UI feel like a spreadsheet.

## Control Shape

Use compact sliders or steppers for weights:

- MCAT fit;
- GPA fit;
- state/OOS fit;
- cost fit;
- baseline attendance context.

Each control should show:

```text
Component name
Current weight
One-sentence meaning
```

## Default Mode

Default controls can be collapsed under:

```text
Scoring weights
```

The user should not need to understand weights to use Build My List. The first visible result should still work with default weights.

The default workflow should be state-first:

- home state appears near the top of the menu;
- Florida remains the expected common case for the current reviewer;
- state exclusions are immediately visible;
- Texas can be excluded quickly.
- data-confidence/source-confidence does not appear as a filter.

## Presets

Only use neutral preset names:

- Balanced
- Cost-aware
- Academic-screen focused
- Florida-first
- State-first

Avoid:

- Safety
- Likely Admit
- Best Schools
- Prestige Winner

## Reset

Provide:

- reset weights;
- clear excluded states;
- clear excluded cities;
- clear ownership filter;
- clear all filters.

## Ownership Filter UX

Institution ownership is a filter, not a live score component for this slice.

Use dropdown labels:

```text
All ownership types
Public
Private
Unknown
```

If ownership data is not populated, the UI should either:

- show only `Unknown`; or
- disable the ownership dropdown with text saying ownership labels are not populated yet.

Do not label schools as public/private without a source-backed field.

If ownership labels are missing, keep the filter disabled or Unknown-only. Do not replace that gap with confidence filtering.

## Not Interested UX

Not Interested is a direct card button.

Behavior:

- click once to move the school to the Not Interested page;
- remove it from Build My List immediately;
- remove it from Interested/Applying/Compare if present;
- allow restoring it from the Not Interested page by clicking the selected Not Interested button.

## Persistence

Store in local storage only. Do not write personal scoring preferences to repo files.

## Done Criteria

- Users can change rank order without editing data files.
- Controls remain compact and understandable.
- No claimy preset labels exist.
- No data-confidence filter control appears.
