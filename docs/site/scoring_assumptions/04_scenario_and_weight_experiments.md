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
Generated school context status
Generated school context weight
Best for
Limitations
```

Example limitations:

- `Cost-aware`: does not know actual scholarships.
- `Academic-screen focused`: still not admissions probability.
- `Florida-first`: prioritizes state context but does not guarantee in-state preference.
- `Generated school context`: experimental and can be set to weight 0.

## Custom Weights

Users should be able to adjust weights live.

Rules:

- weights can be zero;
- negative weights are not allowed;
- if all weights are zero, disable scoring and show a validation message;
- the UI should display normalized weight share if possible.

Do not silently fall back to default weights after the user sets all weights to zero.

## Generated School Context

The current live score includes a baseline attendance context component from the generated payload. The Scoring page should relabel this as:

```text
Generated school context
```

It must be visible in:

- assumptions table;
- weights and formulas table;
- selected-school breakdown;
- rank movement explanation when it is a meaningful driver.

It must also be easy to disable by setting weight to `0`.

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

All scenario comparison rows are MD-only in this slice. DO scenario scoring is a future/separate flow.

## Export

CSV export can be a later slice.

If included now, export only browser-local assumptions and visible ranking output. Do not upload or persist.

## Done Criteria

- Preset effects are visible as numbers, not just buttons.
- Custom weight changes update score tables and Build My List state.
- The UI makes it clear that different presets are value lenses, not predictions.
- Generated school context can be inspected and disabled without disappearing from the explanation.
- All-zero weights disable scoring visibly.
