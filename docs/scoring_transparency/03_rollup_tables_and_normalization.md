# Rollup Tables and Normalization

## Objective

Move toward normalized source-of-truth tables with a single generated review rollup, without breaking the current workbook/site.

## Principle

Normalized tables are source of truth. Wide tables are generated review surfaces.

## Proposed Generated Rollup

Add this after contribution outputs are stable:

```text
outputs/school_decision_rollup.csv
```

Purpose:

- one wide row per applicant profile and school;
- includes school identity, selected normalized facts, manual fit inputs, scores, ranks, warnings, and explanation fields;
- feeds workbook/site review surfaces;
- is regenerated, not hand-edited.

## Existing Table Policy

`data/school_master.csv` can remain during transition as a compatibility input and school identity surface.

Do not keep expanding it indefinitely with:

- imported GPA/MCAT values;
- tuition and COA facts;
- match outcomes;
- hidden curriculum fields;
- city research;
- partner-specific personal-fit values;
- score contributions.

## Future Normalized Domains

Candidate tables:

```text
data/normalized/school_identity.csv
data/normalized/admissions_stats.csv
data/normalized/admissions_policies.csv
data/normalized/cost_and_debt.csv
data/normalized/letter_requirements.csv
data/normalized/curriculum.csv
data/normalized/match_outcomes.csv
data/normalized/city_context.csv
data/normalized/hidden_curriculum.csv
data/manual/partner_inputs.csv
data/manual/research_notes.csv
```

## Migration Order

Recommended order:

1. Add generated rollup while leaving current inputs alone.
2. Move low-risk manual/judgment domains first.
3. Move city/curriculum/hidden-curriculum facts next.
4. Leave admissions stats and cost layers on their current normalized files because they already exist.
5. Split school identity only after workbook/site consumers no longer depend directly on `school_master.csv`.

## Guardrails

- Every normalized row needs `school_id`.
- Source-backed normalized rows need provenance fields.
- Manual rows need reviewer/date/confidence fields.
- Rollup generation must be reproducible.
- Generated rollups should never become hand-edited inputs.

## Tests

Add tests for:

- rollup row count equals expected profile-school combinations;
- rollup does not introduce private profile rows in public builds;
- rollup preserves core school identity columns;
- generated rankings and site payload can be built from rollup when that migration is activated;
- no normalized table is missing required provenance fields.

## Done Criteria

- The master surface stops growing as the place where all facts are added.
- Workbook/site consumers can use a generated rollup.
- Normalized tables remain domain-specific and source-traceable.
