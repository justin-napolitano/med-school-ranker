# Score Cards Tab Simplification

## Goal

Make `#/dossiers` feel like a school browser.

Show all schools by default. Only hard-no schools should be hidden from the primary view for now.

## Main Table Columns

- Decision Rank
- School
- Location
- Admissions Tier
- MCAT average
- GPA average
- In-state estimated cost
- Out-of-state estimated cost
- Status
- Actions

## Controls

Keep only high-value filters:

- status;
- admissions tier;
- state;
- degree;
- data quality.

## Actions

- `Open`
- `Compare`
- status switch: `None / Interested / Applying`

## Move Out Of The Main View

- missing sections;
- research status;
- export buttons;
- source confidence;
- raw local dossier language.

## Missing MCAT/GPA Labels

Do not leave blank values unexplained. Use compact labels:

- `Approved value missing` when the canonical normalized file lacks the value;
- `Candidate value available` when source evidence exists but was not approved for scoring;
- `No candidate value found` when the source layer has no value.
