# Admin Compatibility and Publish-Safe Guardrails

## Objective

Keep the current review/admin site useful while introducing node-backed profile/card rendering.

## Local-Full Mode

Local-full mode may include:

- admin status nodes;
- source/data-quality review views;
- browser-local reviewer state;
- dossier edits;
- visibility state;
- application-list state;
- plan/status pages.

## Publish-Safe Mode

Publish-safe mode must exclude:

- admin status nodes;
- private applicant data;
- private-derived outputs;
- local reviewer-state node fields;
- private source paths;
- raw private/manual files.

## Compatibility Requirements

- `site_payload.json` remains backward compatible.
- Existing routes do not break while only profile/cards migrate to nodes.
- Admin pages may continue reading existing payload shapes until a later admin cleanup slice.
- Upload bundle must remain free of private paths.

## Done Criteria

- Local-full still supports review/admin workflows.
- Publish-safe output can render node-backed profile pages without admin-only payloads.
- Tests or checks verify admin-node exclusion and upload-bundle privacy.

