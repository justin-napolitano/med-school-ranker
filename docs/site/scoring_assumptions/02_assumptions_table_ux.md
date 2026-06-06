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
Notes
```

## Required Rows

Initial rows:

- Applicant MCAT;
- Applicant GPA;
- Home state;
- Degree filter;
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
- Baseline attendance context weight.

## Controls

Editable rows should use the same controls and state handlers as Build My List:

- MCAT input;
- GPA input;
- home state dropdown;
- degree dropdown;
- excluded state dropdown;
- excluded city dropdown;
- ownership dropdown when source-backed labels exist;
- weight sliders;
- preset buttons;
- reset weights button.

Do not create a second state model.

## Empty Values

If a user has not entered a value, display:

```text
Not entered
```

The notes column should explain the effect:

```text
This component is excluded from Your Score until entered.
```

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
