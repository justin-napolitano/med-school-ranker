# Methodology And Claim Safety

## Objective

Make the Scoring page transparent without overstating what the app knows.

## Methodology Updates

Update `/methodology/` to include:

- link to `/scoring/`;
- current live components;
- formula labels;
- present-components-only denominator;
- weight preset definitions;
- missing-data policy;
- distinction between `Your Rank` and `Baseline Rank`;
- local-state privacy statement.

## Required Caveat

Use this caveat near personalized scoring:

```text
MCAT/GPA score-screen fit only; not acceptance probability or a school-specific admit chance.
```

## Unsupported Claims

The page must not say:

- guaranteed admission;
- likely admitted;
- safe school;
- sure thing;
- best school;
- acceptance probability, unless explicitly negated/caveated;
- admit chance, unless explicitly negated/caveated.

## Source Confidence

Data confidence and source quality can appear as transparency fields.

They should not become filters or score components in this slice.

## Privacy Copy

Add plain copy:

```text
Your inputs are stored in this browser only. They are not sent to a server by this static site.
```

Do not overclaim absolute privacy beyond the static-site behavior.

## Done Criteria

- Methodology and Scoring page agree on formulas and labels.
- No unsupported claims appear in generated HTML.
- Smoke tests enforce the main caveats.
