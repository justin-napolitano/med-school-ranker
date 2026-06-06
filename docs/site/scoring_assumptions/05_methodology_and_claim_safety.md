# Methodology And Claim Safety

## Objective

Make the Scoring page transparent without overstating what the app knows.

## Methodology Updates

Update `/methodology/` to include:

- link to `/scoring/`;
- current live components;
- MD-only scoring scope for the first Scoring workspace;
- DO scoring as a future/separate flow;
- formula labels;
- present-components-only denominator;
- weight preset definitions;
- missing-data policy;
- zero-weight component policy;
- distinction between `Your Rank` and `Baseline Rank`;
- deterministic `Why did this move?` explanation;
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

## DO Scope Copy

Add plain copy:

```text
This Scoring page covers MD schools only. DO schools need a separate scoring flow because the source context and applicant-pool assumptions differ.
```

Do not frame DO schools as lower quality or less desirable.

## Movement Explanation Copy

Use:

```text
Why did this move?
```

The explanation must come from deterministic contribution data, not generated prose.

## Privacy Copy

Add plain copy:

```text
Your inputs are stored in this browser only. They are not sent to a server by this static site.
```

Do not overclaim absolute privacy beyond the static-site behavior.

## Done Criteria

- Methodology and Scoring page agree on formulas and labels.
- No unsupported claims appear in generated HTML.
- MD-only scope and DO future-flow copy are visible.
- `Why did this move?` appears near rank movement.
- Smoke tests enforce the main caveats.
