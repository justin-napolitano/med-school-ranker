# School Dossier Profiles

## Objective

Create a structured dossier for every school so applicants can review precomputed facts and fill research fields in one place.

This should reduce duplicated research work and prevent applicants from compiling school notes from scratch across scattered documents.

## Dossier Index

Add a school profiles/dossiers tab or route.

The index should show all schools with:

- school name;
- degree type;
- city/state;
- Decision Rank;
- admissions tier;
- rank confidence;
- visibility state;
- research status;
- missing dossier sections;
- open dossier action.

## Dossier Sections

Each dossier should include:

### Summary

- school name;
- degree type;
- city/state;
- application unit type;
- source URL;
- Decision Rank;
- rank band;
- rank confidence;
- application bucket.

### Applicant Fit

- admissions score;
- attendance score;
- MCAT/GPA fit;
- OOS/residency fit;
- cost fit;
- top positive and negative contributors;
- Why This Rank audit.

### Admissions Facts

- published MCAT/GPA average and bands;
- stats data quality;
- admissions policy summary;
- letter requirements;
- source links and confidence.

### Cost

- applicant-relevant cost basis where available;
- tuition/COA fields;
- debt burden score;
- cost source/confidence.

### School Research

Precomputed where available, locally editable where missing:

- curriculum notes;
- pass/fail or ranking notes;
- mandatory attendance notes;
- recorded lecture notes;
- clinical rotation notes;
- match/outcomes notes;
- city/lifestyle notes;
- pros;
- cons;
- open questions.

### User Decision Fields

Browser-local editable fields:

- interest level;
- research status;
- four-year happiness;
- location fit;
- culture fit;
- regret index;
- hard-no flag;
- hard-no reason;
- application decision status;
- notes.

## Research Status Values

Suggested controlled values:

- `not_started`
- `skimmed`
- `needs_deep_research`
- `researched`
- `ready_to_decide`
- `excluded`
- `applied`

## Missing Research Prompts

Generate prompts when fields are missing:

- "Find curriculum structure."
- "Check attendance/recorded lecture policy."
- "Review match list or residency outcomes."
- "Confirm OOS friendliness."
- "Estimate true cost."
- "Discuss city fit."

## Export

Export file:

```text
school_dossier_edits_export.csv
```

Export local user-entered fields and visibility state. Do not export private source files.

## Done Criteria

- Every active school can be opened as a dossier.
- Dossier distinguishes source-backed facts from user-entered notes.
- Missing information becomes a research prompt.
- User-entered dossier fields can be exported.
