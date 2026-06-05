# Canonical Domain Tables

## Objective

Keep the source of truth narrow, auditable, and migration-ready. The site can become card-based, but canonical data should stay domain-specific instead of becoming one giant JSON blob.

## Current Canonical Sources

Current repo inputs already imply these domains:

- school identity and universe;
- applicant profiles;
- admissions stats;
- cost and debt;
- admissions policies;
- letter requirements;
- source review;
- source match overrides;
- partner/reviewer inputs;
- rankings and score methodology;
- score contributions;
- project governance/status.

## Target Canonical Tables

The long-term canonical model should resolve into these domain families:

```text
school_identity
school_campuses
school_urls
admissions_stats
cost_and_debt
admissions_policies
letter_requirements
curriculum
match_outcomes
city_context
hidden_curriculum
source_records
source_review_queue
source_match_overrides
applicant_profiles
preference_weights
partner_inputs
school_visibility
school_dossiers
calculated_rankings
score_contributions
scoring_methodology
project_subplans
```

CSV files can continue to hold these domains now. Future Postgres tables should map closely to these same domains.

## Rules

- A canonical table should not contain display-only card copy.
- A canonical table may contain source metadata, confidence labels, and last-verified dates.
- A canonical table should have stable IDs wherever rows are joined.
- Imported source rows should remain traceable to source table/file/URL.
- Manual reviewer state should remain separate from source-backed facts.
- Private applicant data must remain under ignored private paths.

## Generated Outputs Are Not Canonical

These are generated read/review surfaces:

```text
outputs/calculated_rankings.csv
outputs/school_decision_rollup.csv
outputs/site/data/site_payload.json
outputs/site/data/nodes/*.json
outputs/med_school_ranker.xlsx
```

They may be regenerated, diffed, and published if safe, but they should not become hand-edited source files.

## Postgres Implication

When Postgres is introduced:

- canonical CSVs become relational tables first;
- generated node JSON can be produced from SQL views or a build job;
- JSONB can cache card/profile nodes if useful, but should not replace normalized source tables for auditable facts.

## First Implementation Slice

Do not migrate canonical tables yet. Use current CSVs and current joined site payload to generate stable read-model nodes.

## Done Criteria

- Every node field can be traced back to a canonical source, a generated score, or a documented manual/reviewer input.
- No card field requires editing generated JSON by hand.
- Future Postgres mapping is obvious from the table family names.
