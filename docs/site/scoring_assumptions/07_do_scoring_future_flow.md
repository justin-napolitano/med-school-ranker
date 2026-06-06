# DO Scoring Future Flow

## Objective

Keep DO school scoring out of the first `/scoring/` implementation while preserving a clear path to support it later.

## Why Separate

DO schools should not be mixed into the first MD scoring assumptions workspace because:

- the current AAMC band context is primarily MD-focused;
- DO source coverage and cost coverage differ from MD source coverage;
- applicant strategy may differ for DO applications;
- mixing both contexts could make rank movement and score-screen fit harder to trust.

## Current Product Behavior

Build My List may continue showing MD and DO schools.

The first `/scoring/` page must:

- score MD schools only;
- exclude DO schools from selected-school dropdowns;
- exclude DO schools from rank movement tables;
- explain that DO scoring needs a separate flow.

## Future DO Flow

A later DO scoring flow should define:

- DO-specific school universe;
- DO-specific source coverage and confidence labels;
- DO-specific MCAT/GPA interpretation;
- cost and geography handling;
- whether COMLEX or osteopathic mission fit should be visible;
- whether DO and MD should ever be compared in one mixed rank.

Potential future route:

```text
/scoring/do/
```

Do not implement this future route in the current slice.

## Done Criteria For Current Slice

- DO schools are not silently mixed into MD scoring.
- The UI explains the omission without making quality claims.
- The headless worker does not implement a DO scoring route.
