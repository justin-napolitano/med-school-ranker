# Frontend Refresh QA And Branching

## Objective

Keep each frontend slice reviewable, public-safe, and visually checked.

## Branch Rules

- Start every implementation branch from latest `main`.
- Do not stack new frontend branches unless the user explicitly asks.
- Keep each PR focused on one slice.
- Preserve unrelated untracked screenshot files unless the slice intentionally replaces them.
- Commit generated site outputs only when the slice changes site output.

## Required Local Checks

Run:

```bash
uv run med-school-build-site --site-mode publish_safe
uv run med-school-validate
uv run pytest
git diff --check
```

Run `uv run med-school-build-all` when workbook, upload bundle, CSVs, or data/project plan surfaces need regeneration.

## Public-Safe Check

Confirm:

- `site_mode` is `publish_safe`;
- `routes.admin` is empty;
- no private path appears in committed output;
- no real applicant answers are committed.

## Screenshot QA

Capture desktop and mobile for:

- intake;
- rankings;
- schools;
- school score card;
- applications;
- methodology;
- admin fallback/local-only route if changed.

If screenshot tooling is unavailable, document the skip reason and run static build/tests.

## Visual Checks

Review:

- no overlapping text;
- no button label overflow;
- cards keep stable dimensions;
- side menus scroll independently where expected;
- clicking a school opens at the top;
- hidden/lower-priority groups stay collapsed until clicked;
- colors are not a one-hue theme;
- copy remains serious and direct.

## Done Criteria

- Build/test/validation pass.
- Public-safe payload passes smoke check.
- Screenshots or documented visual review cover changed routes.
- Handoff names residual risks and next branch.

