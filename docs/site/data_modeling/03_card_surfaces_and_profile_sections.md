# Card Surfaces and Profile Sections

## Objective

Define the card model that will let the product site move from admin tables to decision-useful school cards and profile sections.

## Card Design Goals

Cards should be:

- dense but readable;
- source-aware;
- comparable across schools;
- usable in lists, tables, compare views, and profile pages;
- honest about missing or provisional data.

The card layer should not invent facts or hide uncertainty.

## Card Families

### School Summary Card

Use on rankings, lists, and search results.

Fields:

- school name;
- degree type;
- location;
- ownership/region when available;
- Decision Rank;
- admissions tier;
- MCAT/GPA summary;
- OOS/in-state cost summary;
- confidence/readiness chips;
- shortlist/compare/profile actions.

### Ranking Explanation Card

Use inside school profiles and ranking detail panels.

Fields:

- Decision Rank;
- rank band;
- rank confidence;
- admissions score;
- attendance score;
- top positive contributors;
- top negative contributors;
- missing/low-confidence drivers.

### Admissions Fit Card

Fields:

- applicant band context;
- school MCAT/GPA average and band;
- MCAT/GPA fit scores;
- AAMC national aggregate context;
- explicit caveat that this is not school-specific probability.

### Cost Card

Fields:

- in-state cost;
- out-of-state cost;
- COA;
- cost basis used in scoring;
- source confidence;
- missing/ambiguous flags.

### Requirements Card

Fields:

- LOR summary;
- secondary status/fee when available;
- preview policy;
- MCAT date policy;
- other policy summaries.

### Location/Lifestyle Card

Fields:

- city/state/region;
- rural/urban/suburban classification when available;
- airport/family/weather/cost-of-living fields when available;
- user-entered four-year happiness and location fit in `local_full` only.

### Source Confidence Card

Fields:

- data quality band;
- source count;
- source spread/conflict status;
- last verified date;
- source URLs;
- review queue status.

### Admin Health Card

Admin only.

Fields:

- warnings/errors;
- missing source rows;
- source review status;
- plan status;
- build metadata.

## Profile Section Model

School profiles should be assembled from sections:

```json
{
  "section_id": "cost_and_debt",
  "title": "Cost and Debt",
  "readiness": "partial",
  "cards": ["cost_card", "source_confidence_card"],
  "facts": [],
  "missing_fields": ["estimated_coa_in_state"],
  "source_refs": []
}
```

Required first-pass sections:

- overview;
- applicant fit;
- admissions stats;
- cost and debt;
- requirements and policies;
- source confidence;
- reviewer state in `local_full`;
- methodology.

Future sections:

- curriculum;
- match outcomes;
- location context;
- student life;
- hidden curriculum;
- specialty optionality.

## UI Implication

The current site can continue to render tables. The design pass should use cards as reusable components:

- same card fields in a table row;
- expanded card in a card grid;
- compare card in side-by-side review;
- profile section cards on school pages.

## Done Criteria

- Card fields are defined before visual redesign.
- Each card can render when data is partial.
- Cards can be generated for every active school.
- Admin-only card fields are excluded from `publish_safe`.
