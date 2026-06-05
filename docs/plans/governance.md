# Governance Plan

## Objective

Define how updates, manual judgments, source reviews, and changes are handled so the project remains trustworthy over time.

## Scope

This plan covers update cadence, source review, manual-entry rules, changelog practices, commit discipline, and reviewer workflow.

## Inputs

- Source pages and reports.
- Manual research updates.
- Generated outputs.
- Reviewer feedback.
- Project docs and plans.

## Outputs

- Change log.
- Source review checklist.
- Manual-entry conventions.
- Review workflow for accepting new data into the model.

## Operating Rules

- Update plans before major implementation changes.
- Keep source-derived facts separate from manual judgments.
- Do not overwrite manual scores without review.
- Preserve source dates and last checked dates.
- Regenerate workbook after data or scoring changes.

## Source Policy

- Prefer official or primary sources.
- Use restricted sources only through user-provided exports or manual entries.
- Third-party data requires low confidence unless independently verified.
- Anecdotal student information should be labeled as anecdotal.

## Implementation Steps

1. Add `docs/CHANGELOG.md`.
2. Add source review checklist.
3. Add manual entry conventions to README or docs.
4. Add optional reviewer column fields for manual files.
5. Add build metadata to workbook.

## Validation Rules

- Manual override rows require notes.
- Source updates require source last checked date.
- High-confidence data requires primary or official source.
- Generated outputs should be rebuilt after source changes.

## Open Questions

- Who is the named owner for manual scores?
- How often should sources be refreshed during an application cycle?
- Should we tag releases before sharing workbook versions?

## Definition of Done

- Update workflow is documented.
- Manual changes are distinguishable from source-derived data.
- Reviewers can see what changed and why.
- Shared workbook versions can be traced back to repo commits.
