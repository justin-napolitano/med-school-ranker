# Answer To Ranking Context Mapping

## Purpose

Define how intake answers become deterministic site behavior.

The mapping should be inspectable and reproducible:

```text
answers -> intake context -> filters/groups/chips/actions
```

## Mapping Rules

### Academic Profile

- `degree_goal=md_only` enables the MD-only result lens for the proof of concept.
- `applicant_state` maps to existing state context and in-state grouping. Florida is the first proof-of-concept priority.
- `mcat_band` maps to the existing MCAT band selector.
- `gpa_band` maps to the existing GPA band selector.

Do not infer school-specific admission probability.

### Strategy

- `safer_list` emphasizes schools already labeled by existing outputs as stronger admissions fits, Florida options when applicable, and high-confidence rows.
- `balanced_list` mixes stronger admissions fits, reasonable reaches, and Florida fit using existing rank band/application bucket fields.
- `reach_heavy_list` keeps more reach schools visible and labels them as schools to research, not as predicted admits.

Strategy should influence grouping and target counts first. It should not silently change scoring formulas in this slice.

If `admissions_fit_tier`, `application_bucket`, or equivalent fields are missing for a row, route the school to `Need More Data` rather than inventing a group.

### Geography

- Home-state preference groups Florida schools prominently when the applicant state is Florida and state/location fields exist.
- Urban preference adds positive explanation chips where city context is available.
- Rural avoid moves rural schools to low-fit/hidden only if the user explicitly chooses a hard avoid.
- Unknown geography fields create "needs review" chips, not false negatives.

### Lifestyle

Lifestyle answers initially produce:

- reason chips;
- warning chips;
- research prompts;
- profile-section emphasis.

They do not change rank unless an existing deterministic field supports the mapping and the methodology names the field.

### Cost

Cost sensitivity should:

- highlight estimated COA and cost-basis facts;
- flag high-cost schools;
- move high-cost/low-fit schools lower in guided review groups when cost sensitivity is high;
- explain missing cost data.

Do not invent scholarship assumptions.

### Career Optionality

Career optionality should:

- show awareness chips;
- emphasize research/match/source gaps;
- create research prompts for schools missing relevant data.

Keep the first implementation awareness-only unless existing deterministic fields support a clear rule.

### Dealbreakers

Dealbreakers can affect visibility, but every exclusion must be:

- reversible;
- visible in hidden-school review;
- exportable as a local decision;
- separate from source-derived ranking facts.

## Derived Context Shape

The derived context should include:

- selected profile band values;
- active filters;
- active review-group rules;
- target application count;
- strategy label;
- visible explanation chips;
- awareness-only preferences;
- dealbreaker rules;
- methodology lines.

## Required Output Terms

Use these labels unless deliberately changed with a methodology update:

- `Start Here`
- `Florida Options`
- `Reach Schools To Research`
- `Compare Next`
- `Need More Data`
- `Lower Priority Or Hidden`

Do not use `Safe`, `Likely Admit`, `Recommended Admit`, or similar probability-implying labels.

## Guardrails

- No hidden weights.
- No private answer values in generated public payloads.
- No school-specific probability claims.
- No score mutation without a documented scoring-plan update.
- No irreversible school removal.
- No grouping rule that cannot be explained from answer values plus existing school/ranking/card fields.

## Acceptance Criteria

- A pure function can map the same answers to the same context.
- The UI can display the active context in plain language.
- The grouped results can be reproduced from the context and existing node/ranking data.
- Unavailable mappings are labeled as awareness-only or future, not silently ignored.
