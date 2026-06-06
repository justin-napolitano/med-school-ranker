# School Browser And Per-School Overrides Exec Plan

## Objective

Add a first-class school browser route where a user can scan every school as cards, click into profiles, and optionally apply transparent school-specific scoring overrides.

This is a product route, not an admin table. It should make browsing and personal adjustment feel simple without hiding how the score changed.

## Product Outcome

The user should be able to:

- open `/schools/` from the applicant app shell;
- see all schools as compact, scannable cards;
- search and filter the school universe without needing the ranking flow;
- click any school card to open the school profile at `/schools/:slug/`;
- mark schools as Interested, Applying, Compare, or Not Interested from cards;
- open an override panel for an individual school;
- adjust that school's personal scoring emphasis;
- see both the global score and adjusted score when an override exists;
- reset one school's override or all school-specific overrides;
- understand that overrides are browser-local and not admissions probabilities.

## Route Scope

Add one route:

```text
/schools/       School Browser
```

Existing route remains:

```text
/schools/:slug/ School Profile
```

`/schools/` must be a shell route. `/schools/:slug/` already renders inside the app shell and should keep working.

## Navigation

Add `Schools` to the applicant shell nav.

Suggested order:

```text
Build My List
Schools
Interested
Applying
Not Interested
Compare
Scoring
Methodology
```

Do not add Admin/Data to applicant shell nav.

Do not restore Recommendations.

## Scoring Model

Keep the existing global scoring model intact.

Add a second optional layer:

```text
Adjusted Score = Your Score using school-specific override weights when present
Adjusted Rank = rank order using Adjusted Score for the school-browser view
```

Important rule:

- `Your Score` means global assumptions only.
- `Adjusted Score` means school-specific override applied.
- Cards and profiles must show an `Override applied` chip when adjusted scoring differs from global scoring.

This avoids implying that customized weights are directly comparable to schools that use only global weights.

## Per-School Override Contract

Store overrides in browser local storage only.

Override object:

```ts
type SchoolWeightOverride = {
  schoolSlug: string;
  weights: Partial<{
    mcat: number;
    gpa: number;
    state: number;
    cost: number;
    context: number;
  }>;
  note?: string;
  updatedAt: string;
};
```

The first implementation should not add freeform notes unless the existing UI already supports notes. Keep the override focused on scoring emphasis.

Weight controls:

- default to current global weights;
- allow 0-100 numeric values;
- validate all-zero overrides and refuse to apply them;
- show component-level effects in a compact preview;
- support `Reset to global` for that school.

## User-Facing Copy

Use plain labels:

```text
Schools
Personal scoring override
Global Score
Adjusted Score
Override applied
Reset to global
```

Avoid:

```text
custom algorithm
admit odds
admissions probability
safe school
guaranteed
```

Continue showing the existing caveat:

```text
MCAT/GPA score-screen fit only; not acceptance probability or a school-specific admit chance.
```

## Data And Privacy

No backend or database is required.

Local state only:

- global applicant preferences;
- list statuses;
- compare selection;
- per-school overrides.

No private applicant profile values should be committed, built into payloads, or logged.

## Implementation Slices

1. Route and navigation contract
2. School browser card grid
3. Per-school override state and score derivation
4. Profile and compare integration
5. Local storage reset/export behavior
6. QA, claim-safety checks, and deploy verification

## Acceptance Criteria

- `/schools/` builds as a static Astro route and hydrates inside `ProductAppShell`.
- `/schools/:slug/` direct refresh still works.
- Shell navigation to and from `/schools/` does not full reload.
- The school browser shows all schools, not only the current ranked shortlist.
- Cards expose profile links and local-list actions.
- Overrides are optional and visibly labeled.
- Global score remains visible when an adjusted score exists.
- Reset removes an override and returns the school to global scoring.
- Smoke checks cover `/schools/`, school profiles, and claim-safety language.
- GitHub Pages base-path build still passes.

## Out Of Scope

- Server-side user accounts.
- Database persistence.
- Sharing a partner's override state through a backend.
- Predictive admissions probability.
- New source-data ingestion.
- DO-specific scoring model changes.

