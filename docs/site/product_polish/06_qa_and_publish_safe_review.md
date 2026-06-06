# QA And Publish-Safe Review

## Objective

Verify the polished frontend remains deterministic, public-safe, accessible, and deployable.

## Required Checks

Run:

```bash
uv run med-school-build-site --site-mode publish_safe
uv run med-school-validate
uv run pytest
git diff --check
```

Run `uv run med-school-build-all` when generated workbook, upload bundle, CSVs, or plan-index outputs are intentionally changed.

## Publish-Safe Checks

Confirm:

- site mode is `publish_safe`;
- admin routes are omitted;
- private paths are not present;
- real applicant answers are not committed;
- methodology and source confidence remain visible.

## Screenshot QA

Capture or manually inspect:

- intake;
- rankings;
- applications;
- school score card;
- methodology;
- admin/local fallback if touched.

Desktop and mobile are required for any slice that changes visible layout.

## Accessibility And Copy

Check:

- focus states;
- contrast;
- labels;
- button text fit;
- non-color status meaning;
- no unsupported recommendation claims.

## Done Criteria

- Build/test/validation pass.
- Public-safe smoke check passes.
- Visual QA covers changed routes.
- Handoff names residual risks and next slice.

