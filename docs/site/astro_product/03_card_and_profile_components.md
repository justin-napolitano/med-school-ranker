# Card And Profile Components

## School Card Requirements

Each applicant card must lead with:

- school name;
- city/state and degree type;
- score-screen fit label derived from MCAT/GPA context only;
- visible caveat that score-screen fit is not acceptance probability;
- deterministic "why it ranks here" bullets from generated data;
- MCAT/GPA context;
- estimated in-state and out-of-state cost when available;
- Interested and Applying actions.

Routine visible Hide controls are out of scope for applicant cards.

## Score-Screen Fit

Labels may be:

```text
Score-screen fit: below published range
Score-screen fit: near published range
Score-screen fit: within published range
Score-screen fit: above published range
Score-screen fit: needs MCAT/GPA inputs
```

These labels use only applicant MCAT/GPA compared with generated school MCAT/GPA bands or averages. They are not acceptance probability, admit chance, safety, or school quality.

## Why Bullets

Use available generated fields in this order:

1. `rank_summary`
2. `top_positive_drivers`
3. `top_negative_drivers`
4. cost availability or missing cost data
5. admissions stats quality band
6. missing/low-confidence driver summary

Do not invent facts when generated fields are blank.

## Profile Requirements

School profiles should include:

- overview and source confidence;
- score-screen context;
- ranking context;
- MCAT/GPA context;
- cost context;
- admissions policy and letter-requirement counts when available;
- missing-data caveats;
- links back to recommendations and compare.

Profiles remain product-facing, not admin tables.
