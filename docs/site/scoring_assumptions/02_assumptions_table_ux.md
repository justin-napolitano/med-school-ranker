# Assumptions Table UX

## Objective

Give users one readable table that answers: "What assumptions are currently active?"

This table should be easier to understand than sliders buried in the side menu.

## Page Placement

Add a new route:

```text
/scoring/
```

Nav label:

```text
Scoring
```

The page should sit near Build My List and Methodology in the product nav.

## Required Section

Section title:

```text
Assumptions in use
```

Required columns:

```text
Assumption
Current value
Used by
Can change?
Source
Notes
```

## Required Rows

Initial rows:

- Applicant MCAT;
- Applicant GPA;
- Home state;
- Scoring universe;
- Cost basis;
- Excluded states;
- Excluded cities;
- Institution ownership filter status;
- Not Interested behavior;
- Active scoring preset;
- MCAT fit weight;
- GPA fit weight;
- State/residency fit weight;
- Cost fit weight;
- Generated school context weight.

`Scoring universe` must display:

```text
MD schools only
```

Notes should explain:

```text
DO schools use a different source context and are planned for a separate scoring flow.
```

Do not include a DO scoring toggle in this slice.

## Controls

Editable rows should use the same controls and state handlers as Build My List:

- MCAT input;
- GPA input;
- home state dropdown;
- excluded state dropdown;
- excluded city dropdown;
- ownership dropdown when source-backed labels exist;
- weight sliders;
- preset buttons;
- reset weights button.

Do not create a second state model.

The Scoring page can show the existing Build My List degree filter as context if needed, but scoring calculations and score breakdown tables must remain MD-only in this slice.

## Empty Values

If a user has not entered a value, display:

```text
Not entered
```

The notes column should explain the effect:

```text
This component is excluded from Your Score until entered.
```

If a component has weight `0`, display:

```text
Not included because weight is 0.
```

This must be visually distinct from missing data.

## Ownership Filter

If source-backed ownership labels are not populated:

- show `Unknown / disabled`;
- explain that the app is not inferring public or private status from names;
- do not allow public/private filtering.

## Visual Requirements

- The table must work on mobile without horizontal overflow that hides key values.
- Long excluded city/state lists should wrap as chips.
- The current value column should be scannable.
- Avoid a spreadsheet-admin feel by grouping assumptions into compact table sections:
  - Applicant;
  - Geography and filters;
  - Weights.

## Done Criteria

- User can tell what assumptions are active without opening methodology.
- User can change the assumptions that already exist in Build My List.
- Values persist through the existing local browser state.
- The page does not expose unsupported claims.
- The page states that the scoring workspace is MD-only for now.
- The page distinguishes missing assumptions from zero-weight assumptions.
