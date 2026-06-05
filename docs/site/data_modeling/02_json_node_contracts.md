# JSON Node Contracts

## Objective

Create generated JSON read models that are stable enough for the site to render cards, profiles, lists, and admin surfaces without reimplementing joins in browser JavaScript.

## Node Contract Principles

- Nodes are generated artifacts.
- Nodes are typed by `node_type`.
- Nodes are versioned by `node_schema_version`.
- Nodes use stable IDs and slugs.
- Nodes separate data from presentation, but may be shaped for display.
- Nodes include confidence/readiness/missing-data metadata.
- Nodes are safe-by-construction for their site mode.

## Common Fields

Every node should include:

```json
{
  "node_schema_version": "site_nodes_v1",
  "node_type": "school_card",
  "id": "school_one",
  "generated_at": "2026-06-05T00:00:00Z",
  "site_mode": "local_full",
  "publish_safe": false
}
```

Where relevant, add:

```json
{
  "school_id": "school_one",
  "school_slug": "example-school-of-medicine",
  "route": "#/schools/example-school-of-medicine",
  "readiness": "partial",
  "confidence": "medium",
  "missing_fields": ["cost", "letters"],
  "source_refs": []
}
```

## Required Node Files

```text
outputs/site/data/nodes/school_nodes.json
outputs/site/data/nodes/school_card_nodes.json
outputs/site/data/nodes/school_profile_nodes.json
outputs/site/data/nodes/ranking_card_nodes.json
outputs/site/data/nodes/compare_card_nodes.json
outputs/site/data/nodes/list_nodes.json
outputs/site/data/nodes/methodology_nodes.json
outputs/site/data/nodes/admin_status_nodes.json
```

## School Node

Purpose: stable fact node for a school.

Required fields:

- `school_id`
- `school_slug`
- `display_name`
- `degree_type`
- `campus_name`
- `city`
- `state`
- `state_abbrev`
- `region`
- `ownership_type`
- `official_url`
- `profile_route`
- `active`
- `manual_exclusion_flag`
- `source_confidence`

## School Card Node

Purpose: compact school summary for card grids and table rows.

Required fields:

- identity fields;
- rank summary;
- MCAT/GPA summary;
- cost summary;
- location summary;
- readiness/confidence labels;
- warning chips;
- primary actions/routes.

Do not include admin-only source review queues.

## Ranking Card Node

Purpose: ranking-specific card or row.

Required fields:

- `decision_rank`
- `rank_band`
- `rank_confidence`
- `overall_school_value`
- `admissions_score`
- `attendance_score`
- `admissions_fit_tier`
- `application_bucket`
- `top_positive_contributors`
- `top_negative_contributors`
- `missing_or_low_confidence_drivers`
- `aamc_context_label`

## Compare Card Node

Purpose: side-by-side school comparison.

Required fields:

- identity;
- rank/fit;
- admissions facts;
- cost facts;
- requirements summary;
- reviewer-state summary in `local_full` only;
- missing-data summary.

## School Profile Node

Purpose: complete profile route model.

Required fields:

- `school_id`
- `school_slug`
- `route`
- `header`
- `snapshot_cards`
- `sections`
- `source_confidence`
- `methodology_refs`
- `admin_refs` in `local_full` only.

Sections should be arrays, not hard-coded top-level keys, so the UI can add/reorder sections without changing every node consumer.

## List Node

Purpose: curated list route and card source.

Required fields:

- `list_id`
- `slug`
- `route`
- `title`
- `description`
- `readiness_label`
- `eligibility_summary`
- `required_fields`
- `missing_or_low_confidence_fields`
- `school_ids`
- `top_card_ids`

## Methodology Node

Purpose: explain scoring and caveats.

Required fields:

- scoring group;
- formula summary;
- weight basis;
- component rows;
- AAMC caveat;
- confidence labels;
- private/public note.

## Admin Status Node

Purpose: admin panel summary.

Required fields:

- source integration status;
- validation error/warning counts;
- source-review counts;
- raw-source counts;
- plan status counts;
- build metadata.

This node is not allowed in `publish_safe`.

## Done Criteria

- Nodes are deterministic across repeated builds.
- Nodes can be consumed without joining raw CSV-shaped arrays in browser code.
- `publish_safe` node output omits admin/reviewer/private nodes.
- Every node family has tests for count and required fields.
