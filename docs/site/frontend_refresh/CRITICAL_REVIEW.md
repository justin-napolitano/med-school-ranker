# Frontend Refresh Critical Review

## High: Do Not Redesign Before Workflow Clarity

Risk: visual polish could make the same spreadsheet-like workflow look nicer without making it easier to use.

Resolution: execute route shell, shared cards, intake results, and list builder before broad visual polish.

## High: Keep Deterministic Methodology Visible

Risk: card-based UI could start feeling like a recommendation engine without explaining what changed and why.

Resolution: every card/group must expose reason chips, missing-data warnings, and links to methodology. Avoid labels that imply school-specific admissions probability.

## High: Protect Publish-Safe Output

Risk: frontend work touches local state and admin routes, which could accidentally leak into GitHub Pages output.

Resolution: every slice must run publish-safe build and verify that admin routes are omitted.

## Medium: Avoid Duplicating Data Joins In JavaScript

Risk: the site already has generated nodes, but quick frontend changes could rejoin raw tables in browser code and create inconsistent displays.

Resolution: use node builders and shared render helpers where possible. If a card needs a missing field, add it to generated nodes with tests.

## Medium: Do Not Overload Intake

Risk: asking too many questions recreates the spreadsheet problem in form format.

Resolution: required intake fields stay short. Optional answers affect visible chips/prompts or remain clearly awareness-only.

## Medium: List Limits Need Hard Behavior

Risk: Interested/Applying limits could become decorative counters that do not actually guide behavior.

Resolution: limits must block over-limit additions and tell the user what to remove.

## Low: Branch Drift

Risk: multiple frontend branches can diverge quickly because the site is generated from one large Python file and embedded output.

Resolution: one branch per slice, merge to `main`, then start the next branch from latest `main`.

## Ready For Execution

The plan is ready when:

- branch names are explicit;
- each slice has a bounded child plan;
- verification commands are listed;
- public-safe guardrails are explicit;
- the runbook points to this plan as the next selected frontend phase.

