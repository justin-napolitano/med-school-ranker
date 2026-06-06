# Score-Card Language Migration

## Purpose

Use `Score Card` as the visible product language for per-school review while keeping current internal data names stable.

## Migration Boundary

Change visible copy in:

- navigation;
- route tools;
- rankings actions;
- guided card actions;
- score-card index heading and caveat;
- profile local edit panel;
- research queue copy;
- application-list caveats and export buttons.

Keep stable:

- `#/dossiers` route;
- `school_dossiers.csv`;
- `school_dossier_edits_v1`;
- `school_dossier_edits_export.csv`;
- browser-local dossier state keys;
- existing import/export code paths.

## Future Migration

A full internal rename may happen later only with:

- import/export backward compatibility;
- local-storage migration;
- tests for old and new schema names;
- explicit release notes.

