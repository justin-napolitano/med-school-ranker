# Admin and Public Payload Separation

## Objective

Make it impossible to confuse "hidden in the UI" with "not present in the payload."

The static site embeds JSON. Therefore publish safety must be enforced at payload generation time, not by hiding routes or CSS.

## Existing Modes

The repo already supports:

- `local_full`: local review/admin mode;
- `publish_safe`: public-safe payload mode.

This plan extends that boundary to node families.

## Product/Public Nodes

Allowed in `publish_safe` if they contain only public-safe data:

- school nodes;
- school card nodes;
- school profile nodes;
- ranking card nodes generated from public/template profile only;
- compare card nodes without reviewer state;
- list nodes;
- methodology nodes;
- public source summary nodes.

## Admin/Local Nodes

Allowed only in `local_full`:

- admin status nodes;
- source review queue nodes;
- data quality detail nodes if they expose local paths or admin-only review details;
- reviewer-state nodes;
- school visibility nodes;
- school dossier edit nodes;
- partner input nodes;
- private applicant profile nodes;
- private-derived ranking/card nodes.

## Private-Derived Rule

A ranking generated from a real private applicant profile is private-derived even if exact GPA/MCAT values are not displayed. The order itself can reveal fit.

Private-derived outputs must stay under ignored paths unless the user explicitly requests an uncommitted local-only artifact.

## Node-Level Metadata

Every node file should expose metadata:

```json
{
  "node_schema_version": "site_nodes_v1",
  "site_mode": "publish_safe",
  "publish_safe": true,
  "contains_admin_data": false,
  "contains_reviewer_state": false,
  "contains_private_derived_data": false
}
```

For array-only files, use a wrapper object or adjacent manifest if needed. The first implementation can choose the least disruptive shape, but tests must verify the boundary.

## Test Requirements

Publish-safe tests must assert:

- admin node files are not written;
- reviewer-state node files are not written;
- private fields are absent from embedded HTML;
- private/admin strings are absent from `site_payload.json`;
- upload bundle contains no private ignored paths;
- `routes.admin` is empty;
- product routes still render.

## Done Criteria

- Payload safety is enforced by generation, not navigation.
- Node families are classified as product-public, product-local, or admin-local.
- Tests fail if admin/private nodes enter `publish_safe`.
