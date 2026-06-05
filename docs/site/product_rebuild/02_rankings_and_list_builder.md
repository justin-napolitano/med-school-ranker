# Rankings and List Builder

## Objective

Make rankings the primary product surface: a fast, beautiful, useful table for narrowing the school universe into an application list.

## User Jobs

- Find realistic schools for an applicant profile.
- Compare MD and DO schools without losing context.
- Filter by location, degree, ownership, cost, MCAT/GPA band, AAMC national rate band, and source confidence.
- Apply curated scoring lenses.
- Build and revise an application shortlist.
- Understand why each school appears where it does.

## Core Components

### Ranking Header

- Active profile selector when profiles are available.
- Scoring lens selector.
- Visible result count.
- Quick actions: reset filters, export visible rows, compare selected, add top N to shortlist.

### Filter Bar

Required filters:

- search;
- degree type;
- state;
- region;
- ownership type;
- dynamic tier;
- funnel bucket;
- MCAT band;
- GPA band;
- AAMC national rate band;
- data quality band;
- tuition/COA range;
- LOR burden;
- hard-no status;
- partner input status.

### Ranking Table

Columns should prioritize applicant decisions:

- rank;
- school;
- location;
- degree;
- tier/bucket;
- overall fit/value;
- admissions fit;
- MCAT/GPA averages;
- AAMC national context band;
- cost/COA;
- source confidence;
- reason chips;
- shortlist action.

### Reason Chips

Examples:

- `MCAT fit`
- `GPA fit`
- `High source confidence`
- `Low cost`
- `Public in-state`
- `Expensive OOS`
- `LOR burden`
- `Missing stats`
- `Source conflict`
- `Partner concern`

Reason chips should come from structured data and scoring outputs, not ad hoc prose.

### List Builder

The first implementation can store local UI state only:

- interested;
- apply;
- reach;
- target;
- likely;
- cut;
- compare selected.

Future implementation can export local selections to CSV or update workbook inputs.

## Scoring Lens Behavior

A lens can be used three ways:

- filter only: restrict visible schools to list eligibility;
- scoring boost: keep all eligible schools but re-rank with lens weights;
- replace scoring: rank purely by the list's scoring profile.

The UI should name the active lens clearly and explain how it changes ranking.

## Implementation Steps

1. Add ranking payload fields for route slugs, source confidence, reason chips, and lens-ready scores.
2. Replace the current rankings table with a dedicated rankings route.
3. Add filter components with stable state.
4. Add scoring lens selector.
5. Add shortlist controls stored in local browser state.
6. Add compare-selected entry point.
7. Add tests for filters, list lens payload, and publish-safe behavior.

## Done Criteria

- The rankings route is useful without visiting admin.
- Curated scoring lenses can be applied to the rankings table.
- A user can shortlist, cut, and compare schools locally.
- Missing data is labeled as missing, never converted to zero.
- School names link to profile routes.
