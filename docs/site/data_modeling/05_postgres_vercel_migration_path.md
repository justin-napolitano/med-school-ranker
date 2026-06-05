# Postgres and Vercel Migration Path

## Objective

Preserve today's local CSV/static workflow while designing a clean path to Postgres-backed persistence and Vercel hosting.

## Recommended Sequence

### Stage 1: Static Generated Site

Current mode:

```text
CSV/manual inputs -> Python generators -> outputs/site/index.html + JSON
```

Keep this working while node contracts are introduced.

### Stage 2: Static Site With Node JSON

Near-term mode:

```text
CSV/manual inputs -> Python generators -> outputs/site/data/nodes/*.json -> static UI
```

This is enough for GitHub Pages, Vercel static hosting, or local review.

### Stage 3: Postgres as Canonical Store

Future mode:

```text
Postgres relational tables -> node builder -> JSON nodes/API responses -> UI
```

Canonical tables should remain relational and source-traceable. JSONB can cache card/profile nodes, but should not be the only home for facts that need auditability.

### Stage 4: Vercel Hosted Product

Potential hosted options:

- fully static export with generated JSON files;
- Vercel-hosted frontend plus static JSON assets;
- Vercel frontend plus API/database reads;
- hybrid: public site static, admin/reviewer workflows local or authenticated later.

Do not choose the final hosting mode until card contracts and public/private payload boundaries are stable.

## Postgres Table Mapping

Likely tables:

```text
schools
campuses
school_urls
admissions_stats
cost_and_debt
admissions_policies
letter_requirements
source_records
source_reviews
applicant_profiles
preference_weights
rankings
score_contributions
reviewer_school_visibility
reviewer_school_dossiers
curated_lists
card_node_cache
profile_node_cache
build_runs
```

## JSONB Guidance

Use JSONB for:

- generated node cache;
- flexible source snapshots;
- card/profile render payloads;
- audit snapshots of a build.

Prefer relational columns for:

- school IDs and joins;
- scores and ranks;
- cost numeric values;
- MCAT/GPA numeric values;
- source confidence labels;
- filters/sorts used by the product UI;
- reviewer decisions that need querying.

## Vercel Guidance

Before Vercel:

- define `publish_safe` build as the default public target;
- keep admin/local routes out of public output;
- decide whether public pages are static or API-backed;
- avoid relying on browser-only private state for hosted reviewer workflows.

## Done Criteria

- Current CSV/static workflow remains viable.
- Future Postgres table names map naturally to canonical domain tables.
- Frontend card contracts do not depend on CSV paths.
- Public hosted output can be generated without admin/private payloads.
