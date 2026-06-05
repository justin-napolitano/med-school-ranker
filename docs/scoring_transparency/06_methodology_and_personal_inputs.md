# Methodology and Personal Input Controls

## Objective

Create a deterministic methodology section and controlled personal-input workflow.

The reviewer should understand how every non-personal score is computed, and the applicant/partner should change subjective preferences through explicit dropdowns or rubric scores rather than manually editing ranks.

## Methodology Outputs

Recommended generated file:

```text
outputs/scoring_methodology.csv
```

Recommended site/workbook section:

```text
Methodology
```

The methodology should cover:

- MCAT fit formula.
- GPA fit formula.
- AAMC national band context caveat.
- OOS/residency fit rules.
- Cost percentile scoring.
- Rank confidence thresholds.
- Scenario weight behavior.
- Missing data behavior.
- Subjective dropdown/rubric definitions.

## Proof-Of-Concept Scope

The first interactive selector should answer:

```text
All things being equal, how do active MD schools rank for this selected AAMC band profile and state?
```

Scope:

- active MD schools only;
- AAMC MCAT bands;
- AAMC GPA bands;
- applicant state selector;
- fixed weights;
- local browser state;
- CSV download/export;
- no server writeback;
- no tie-breaking work beyond existing shared-rank behavior;
- no DO school reranking until DO-specific context and caveats are designed.

DO schools should remain in the broader project, but they are excluded from this proof-of-concept reranking view because the AAMC grid is MD applicant context.

## Precomputed Score Bands

Where practical, precompute possible deterministic scores as reference rows.

Examples:

```text
methodology_area,input_band_or_condition,score,display_label,notes
mcat_fit,applicant 4+ points above school average,9-10,strong MCAT fit,Derived from clamp formula.
mcat_fit,applicant equal to school average,7,at school average,Derived from clamp formula.
mcat_fit,applicant 4 points below school average,5,below school average,Derived from clamp formula.
gpa_fit,applicant 0.16+ above school average,9-10,strong GPA fit,Derived from clamp formula.
oos_fit,same_state,10,in-state advantage,State relation rule.
oos_fit,oos accepted,6,OOS possible,Policy rule.
oos_fit,oos unknown,4,unknown OOS policy,Warning required.
```

These tables are public-safe because they describe possible model behavior, not a real applicant's exact profile or rank order.

## Personal Inputs

Subjective fields should be entered with controlled values.

Examples:

- `could_live_here_4_years_score`
- `location_fit_score`
- `culture_fit_score`
- `regret_index_score`
- `hard_no_flag`
- `hard_no_reason`

Preferred control:

- dropdown for hard-no values;
- 1-10 numeric dropdown for scores;
- optional notes field for the reason;
- rubric text visible beside the input.

Users should update these inputs, then regenerate ranks. They should not directly edit `overall_rank`, `decision_rank`, or generated score outputs.

## Selector Order

Implement selectors in this order:

1. Global all-else-equal selectors:
   - AAMC MCAT band.
   - AAMC GPA band.
   - Applicant state.
   - Global cost sensitivity if needed later.
2. School-specific subjective dropdowns:
   - four-year happiness;
   - location fit;
   - culture fit;
   - regret index;
   - hard-no flag/reason.
3. Weight controls only after the fixed-weight proof of concept is trusted.

The first release should not try to solve all 200 school-specific personal scores at once.

## Suggested 1-10 Rubric

Use the same general interpretation across personal-fit scores:

- `10`: exceptional fit; would be actively excited.
- `8-9`: strong fit; clear positive.
- `6-7`: acceptable or mildly positive.
- `5`: neutral or uncertain.
- `3-4`: concern.
- `1-2`: serious concern.

## Deterministic Explanation Rule

Explanations should be generated from contribution rows and fixed templates.

Example:

```text
Strong GPA fit and same-state residency help this school. MCAT fit is below the school average. Rank confidence is partial because culture and curriculum inputs are missing.
```

Rules:

- Use no more than three positive contributors.
- Use no more than three negative contributors.
- Include missing-data caveat when confidence is below `medium`.
- Label AAMC context as national aggregate MD data, not school-specific probability.
- Do not use AI-generated freeform prose for methodology or rank explanations.

## Done Criteria

- Methodology can be reviewed without reading source code.
- Possible deterministic scores can be inspected as banded reference rows.
- Personal scoring happens through controlled inputs.
- Final ranks remain generated outputs.
