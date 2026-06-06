# Guided Intake Results

## Objective

Make intake answers lead to a clear card-based review workflow.

The intake should not simply update a table. It should produce understandable school groups and next actions.

## Required Groups

Show these groups when applicable:

- `Start Here`
- `Florida Options`
- `Strong Academic Fit`
- `Reach Schools To Research`
- `Compare Next`
- `Need More Data`
- `Lower Priority Or Hidden`

Group labels are review priorities, not acceptance probability claims.

## Behavior

- High-priority groups are expanded by default.
- `Need More Data` and `Lower Priority Or Hidden` are collapsed by default.
- Each group has one sentence explaining why schools are there.
- Each card includes reason chips derived from intake context and ranking/profile nodes.
- The intake summary explains active answers and what they changed.
- The advanced rankings table remains one click away.

## Determinism

The same answers and same generated data must produce the same groups.

Do not use AI inference, random ordering, or hidden scoring.

## Done Criteria

- `#/intake` can move from questions to grouped card results.
- User can see why groups changed.
- Result card actions update local status without route jumps.
- Methodology explains that groups are deterministic review queues.

