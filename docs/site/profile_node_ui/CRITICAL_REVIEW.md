# Critical Review: Profile Node UI Adoption

## Finding 1: UI Could Drift Back Into Raw Payload Joins

The largest risk is implementing node-backed rendering in name only while continuing to pull facts from wide joined rows in JavaScript.

Mitigation:

- Treat `school_profile_nodes` as the primary source for profile sections.
- Add missing display fields to Python node builders when needed.
- Keep raw payload fallback narrow and visibly defensive.

## Finding 2: Visual Redesign Could Expand Scope Too Early

The project is close to a design pass, but styling before proving node consumption would lock the design to unstable payload assumptions.

Mitigation:

- Limit this slice to card helpers and profile-section rendering.
- Defer broad visual language, navigation redesign, and hosted-product polish.

## Finding 3: Publish-Safe Mode Could Regress Quietly

New node-backed routes may accidentally depend on admin-only or local reviewer data.

Mitigation:

- Test publish-safe exclusion for admin status and reviewer/local-only node fields.
- Make profile route rendering work without admin nodes.
- Keep upload-bundle privacy checks in the required verification set.

## Finding 4: Browser-Local Workflow Regressions Are Easy To Miss

Profile route changes could break shortlist, compare, visibility, and dossier edit actions even if the profile visually renders.

Mitigation:

- Keep action wiring keyed by stable `school_id`.
- Smoke-test profile actions after route changes.
- Preserve current local storage/export schemas.

## Finding 5: Node Contracts May Be Missing Fields

The first node generation slice was intentionally conservative. Some profile facts may not be present yet.

Mitigation:

- Start with a contract audit.
- Prefer explicit missing/partial rendering over ad hoc joins.
- Add only high-value missing node fields in this slice; leave deeper content for future school-profile enrichment.

## Go/No-Go Assessment

This slice is ready for headless execution if the worker starts from a clean branch, follows the profile-node adoption plan, and keeps the scope to node consumption plus minimal card helpers.

