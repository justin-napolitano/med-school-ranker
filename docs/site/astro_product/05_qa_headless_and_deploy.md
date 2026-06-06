# QA Headless And Deploy

## Frontend Verification

From repo root:

```bash
cd frontend
npm install
npm run build
npm run smoke
```

The smoke script must inspect static output in `frontend/dist` and fail nonzero if required route files, caveats, or claim-safety checks fail.

## Repo Verification

From repo root:

```bash
uv run med-school-validate
uv run pytest
git diff --check
```

## Static Deploy Notes

The first pass does not replace the existing GitHub Pages workflow. Future deployment can either:

- continue publishing `outputs/site` for the admin/static review surface; or
- publish `frontend/dist` once the product frontend is selected as the public surface.

No server runtime is needed for either path.

## Headless Worker Checklist

- Do not touch untracked screenshots under `outputs/site_qa/screenshots`.
- Regenerate or copy only publish-safe JSON.
- Keep route names stable.
- Verify product output lacks unsupported claims.
- Verify admin route exists but is not the first route.
- Commit package lockfile when npm install creates it.
