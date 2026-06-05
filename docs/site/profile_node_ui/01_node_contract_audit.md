# Node Contract Audit

## Objective

Confirm the generated node contracts are sufficient for the first profile UI adoption slice before changing rendering code.

## Required Inputs

- `outputs/site/data/site_payload.json`
- `outputs/site/data/nodes/school_nodes.json`
- `outputs/site/data/nodes/school_card_nodes.json`
- `outputs/site/data/nodes/school_profile_nodes.json`
- `outputs/site/data/nodes/ranking_card_nodes.json`
- `outputs/site/data/nodes/compare_card_nodes.json`
- `outputs/site/data/nodes/methodology_nodes.json`
- `docs/site/data_modeling/02_json_node_contracts.md`
- `docs/site/data_modeling/03_card_surfaces_and_profile_sections.md`

## Checks

- Active school count matches across school, card, profile, ranking, and compare node families.
- Every profile node has a stable `school_id`, `school_slug`, display name, section list, and readiness/missing-field data.
- Every section renders if facts are partial or missing.
- Profile nodes contain enough source/confidence/caveat data to avoid consulting raw joined rows for normal display.
- Publish-safe node families omit admin status and reviewer/local-only data.
- Node schema version and generated metadata are present.

## Gap Handling

If a UI field is missing:

- first decide whether the field belongs in a generated node;
- if yes, add it in the Python node builder and test it;
- if no, leave it out of the profile UI for this slice;
- do not patch the browser by rejoining raw CSV-like arrays unless no node contract can reasonably represent the field.

## Done Criteria

- Contract gaps are documented or fixed.
- No broad UI work starts before the node audit is complete.
- The implementation worker knows which node fields are authoritative for the profile route.

