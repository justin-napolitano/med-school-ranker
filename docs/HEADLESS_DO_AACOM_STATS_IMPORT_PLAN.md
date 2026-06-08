# Headless DO AACOM Stats Import Plan

## Worker Objective

Implement the DO-only AACOM stats importer described in `docs/DO_AACOM_STATS_IMPORT_EXEC_PLAN.md`.

## Scope Rules

- Process only `degree_type=DO` schools.
- Use only AACOM-hosted College of Osteopathic Medicine profile pages.
- Label extracted values as `aacom_com_submitted_profile`.
- Preserve existing third-party/provisional rows.
- Do not modify MD official-source discovery in this run.

## Required Implementation

1. Add AACOM discovery, extraction, and apply modules.
2. Add CLI scripts:
   - `med-school-discover-aacom-do-profiles`
   - `med-school-extract-aacom-do-stats`
   - `med-school-apply-aacom-do-stats`
3. Create source tables and outputs named in the DO exec plan.
4. Add validation for DO-only AACOM URLs and accepted MCAT/GPA ranges.
5. Add tests using local HTML fixtures that include AACOM `MCAT/GPA Information`.
6. Update site/profile source labels for AACOM rows.

## Verification

Run:

```bash
uv run med-school-discover-aacom-do-profiles
uv run med-school-extract-aacom-do-stats
uv run med-school-apply-aacom-do-stats
uv run med-school-validate
uv run pytest
cd frontend && npm run build
cd frontend && npm run smoke
git diff --check
```

## Stop Conditions

Stop and report if:

- AACOM pages require JavaScript-only search to discover all profile URLs.
- Matching would merge multiple campuses without state/campus evidence.
- Extraction cannot isolate `MCAT/GPA Information`.
- The implementation starts changing MD rows.
