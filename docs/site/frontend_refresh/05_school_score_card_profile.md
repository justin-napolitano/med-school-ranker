# School Score Card Profile

## Objective

Make each school page feel like a focused score card, not a generated dossier or data dump.

## First Viewport

The first viewport should show:

- school name;
- degree;
- city/state;
- decision rank or rank status;
- academic fit summary;
- cost summary;
- current local status;
- primary actions: Interested, Applying, None, Compare;
- clear source-confidence or missing-data badges.

## Sections

Recommended section order:

1. `At A Glance`
2. `Why It Ranks Here`
3. `Academic Fit`
4. `Cost And Location`
5. `Application Notes`
6. `Data Quality`
7. `Source Details`

`Source Details` and raw node/payload details should be collapsed by default.

## Copy Rules

- Use `Score Card`, not `Dossier`, in visible applicant-facing UI.
- Use full labels for costs and stats.
- Explain missing MCAT/GPA directly:
  - no current source value;
  - assumed match;
  - low-confidence source;
  - conflicting source cluster.
- Avoid unsupported value judgments.

## Done Criteria

- Opening a school from rankings or cards lands at the top of the score card.
- The score card is understandable before expanding details.
- Raw/source details remain available but not visually dominant.
- Mobile layout does not overflow.

