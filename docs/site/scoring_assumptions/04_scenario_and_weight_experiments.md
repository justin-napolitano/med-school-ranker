# Scenario And Weight Experiments

## Objective

Let users quickly see how rankings move under different weight assumptions without making the UI feel like a data-science tool.

## Current Presets

The existing live scoring presets are:

- Balanced;
- Cost-aware;
- Academic-screen focused;
- Florida-first;
- State-first.

These can remain, but the new Scoring page should explain what each preset changes.

## Required Preset Table

Add a compact table:

```text
Preset
MCAT
GPA
State/residency
Cost
Baseline attendance
Best for
Limitations
```

Example limitations:

- `Cost-aware`: does not know actual scholarships.
- `Academic-screen focused`: still not admissions probability.
- `Florida-first`: prioritizes state context but does not guarantee in-state preference.

## Custom Weights

Users should be able to adjust weights live.

Rules:

- weights can be zero;
- negative weights are not allowed;
- if all weights are zero, show a validation message and fall back to default or disable scoring;
- the UI should display normalized weight share if possible.

## Scenario Compare

Optional in first pass, but useful if time allows:

```text
School
Balanced rank
Cost-aware rank
Academic-screen rank
Florida-first rank
State-first rank
Largest movement
```

Do not block the first implementation on this. The critical path is the current-assumptions table and selected-school breakdown.

## Export

CSV export can be a later slice.

If included now, export only browser-local assumptions and visible ranking output. Do not upload or persist.

## Done Criteria

- Preset effects are visible as numbers, not just buttons.
- Custom weight changes update score tables and Build My List state.
- The UI makes it clear that different presets are value lenses, not predictions.
