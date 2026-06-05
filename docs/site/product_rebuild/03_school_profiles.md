# School Profiles

## Objective

Create polished, source-backed school profile pages that explain each medical school in a decision-useful way.

## Profile Route

```text
#/schools/:school_slug
```

The route should resolve by generated slug and stable `school_id`.

## Page Structure

### Profile Header

- school name;
- degree type;
- city/state;
- ownership type when available;
- primary school/source link;
- rank and active scoring lens context;
- shortlist/compare actions.

### Snapshot Cards

Cards should show:

- MCAT average/band;
- GPA average/band;
- AAMC national context rate band;
- in-state and out-of-state cost/COA;
- LOR requirement summary;
- data quality band.

### Applicant Fit

Show:

- applicant MCAT/GPA when available;
- school published averages;
- gap/delta;
- AAMC national grid context;
- fit tier;
- caveat that AAMC grid is national aggregate MD data, not a school-specific acceptance probability.

### Cost and Debt

Show:

- in-state tuition, fees, insurance;
- out-of-state tuition, fees, insurance;
- estimated COA;
- source name, URL, and confidence;
- missing DO tuition coverage where applicable.

### Requirements and Policies

Show:

- LOR requirements and links;
- secondary application status;
- MCAT dates accepted;
- PREview policy;
- transfer policy;
- DACA policy;
- community college coursework policy;
- interview/waitlist/deposit details where parsed.

### Source Confidence

Show:

- source count;
- MCAT/GPA spread;
- quality band;
- conflicts or review flags;
- last checked dates;
- links to candidate/source-review rows where available.

### Risk Flags

Examples:

- source conflict;
- missing GPA/MCAT;
- missing cost;
- expensive out-of-state;
- all-zero tuition row;
- ambiguous source match;
- policy not parsed cleanly;
- partner hard-no.

## Visual Requirements

- Professional profile layout with clear hierarchy.
- Dense but readable facts.
- No marketing hero.
- No fake imagery.
- Use badges, compact metric cards, tables, and source panels.
- Profiles should look credible enough to send to someone reviewing schools seriously.

## Implementation Steps

1. Add school slug generation.
2. Add profile payload per school.
3. Build route rendering for `#/schools/:slug`.
4. Add profile cards and section components.
5. Add profile source/confidence panels.
6. Link rankings, curated lists, compare, and source pages into profiles.
7. Add tests for direct profile route resolution and missing-data rendering.

## Done Criteria

- Every active school has a profile route.
- Profile pages do not depend on admin payloads in publish-safe mode.
- Source-backed values show confidence/caveats.
- Missing fields render as missing.
- Rankings and list pages deep-link into profiles.
