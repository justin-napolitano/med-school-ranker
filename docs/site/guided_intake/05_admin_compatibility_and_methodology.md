# Admin Compatibility and Methodology

## Purpose

Keep guided intake honest and compatible with the existing admin/review surfaces.

The intake should simplify first use without hiding the rules from a serious reviewer.

## Admin Compatibility

Do not remove:

- rankings table;
- source status;
- data quality report;
- plans page;
- dossier/research workflows;
- application-list workflow;
- compare workflow;
- profile routes;
- publish-safe mode.

The intake may become the default or a prominent first route later, but admin/source workflows should remain reachable.

## Methodology Requirements

The site should explain:

- intake answers are a lens over deterministic scoring;
- core scores are not recomputed by a predictive model;
- strategy changes grouping and emphasis first;
- dealbreakers are reversible local decisions;
- some answers are awareness-only because source coverage is incomplete;
- missing data can affect confidence and research priority.

## Public Copy Guardrails

The applicant-facing UI should avoid:

- `algorithm`;
- `model`;
- `recommended admit`;
- `safe school`;
- `chance`;
- `probability`;
- implementation terms such as `node`, `payload`, or `raw join`.

Use:

- `review group`;
- `fit signal`;
- `research priority`;
- `active rules`;
- `missing data`;
- `source confidence`.

## Advanced Controls

Advanced controls should remain available for:

- MCAT/GPA/state selectors;
- filters;
- visibility review;
- raw ranking table;
- source and data-quality review.

Do not expose advanced controls in a way that overwhelms the intake flow.

## Acceptance Criteria

- Guided intake improves first-use clarity by making active rules visible.
- A reviewer can inspect active rules.
- Admin/source/build-health routes remain available.
- The site does not imply a black-box recommender.
