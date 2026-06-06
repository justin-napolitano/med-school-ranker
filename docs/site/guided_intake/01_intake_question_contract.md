# Intake Question Contract

## Purpose

Define the first stable question set for guided applicant intake.

The questions should feel like an application-list setup flow, not a scoring spreadsheet.

Every required question must have a current product effect. Optional questions can be retained only when they are clearly labeled as awareness-only or research prompts.

## Question Groups

### Academic Profile

Required for the proof of concept:

- `degree_goal`: controlled option, default `md_only`.
- `applicant_state`: controlled state option, default empty or Florida when a saved profile already exists.
- `mcat_band`: controlled AAMC-compatible band option.
- `gpa_band`: controlled AAMC-compatible band option.

Do not add exact MCAT or exact GPA entry to the first applicant-facing intake slice. The first slice should use existing deterministic band logic rather than adding a new probability model.

## Minimum First-Slice Schema

| Question ID | Required | Type | Allowed Values | Product Effect |
| --- | --- | --- | --- | --- |
| `degree_goal` | yes | select | `md_only` | Filters first-pass guided results to MD schools. |
| `applicant_state` | yes | select | US state code | Sets in-state context. Florida is the first proof-of-concept priority. |
| `mcat_band` | yes | select | existing AAMC-compatible MCAT bands | Sets existing selector context. |
| `gpa_band` | yes | select | existing AAMC-compatible GPA bands | Sets existing selector context. |
| `application_strategy` | yes | select | `safer_list`, `balanced_list`, `reach_heavy_list` | Changes group emphasis and target mix, not core scores. |
| `target_application_count` | yes | number/select | `15`, `20`, `25`, `30`, `35` | Sets list-size goal and progress copy. |
| `include_reach_schools` | no | boolean/select | `yes`, `no` | Changes whether reach schools stay in prominent review groups. |
| `urbanicity_preference` | yes | select | `urban_preferred`, `suburban_ok`, `rural_ok`, `no_preference` | Adds geography chips; hard filters only if paired with a dealbreaker. |
| `cost_sensitivity` | yes | select | `low`, `medium`, `high`, `debt_averse` | Adds cost warnings/grouping emphasis. |
| `states_to_avoid` | no | multi-select | US state codes | Creates reversible local hide/flag rules for specific states. Broad regions are out of first-slice scope. |
| `career_optionality` | no | select | `undecided`, `em_leaning`, `competitive_optionality`, `academic_research` | Awareness/research prompts only in first slice unless data support exists. |
| `school_environment_preferences` | no | multi-select | `true_pass_fail`, `low_mandatory_attendance`, `recorded_lectures`, `research_heavy`, `clinical_focus`, `large_academic_center`, `community_focus` | Awareness/research prompts only in first slice unless data support exists. |
| `dealbreakers` | no | multi-select | `hide_rural`, `hide_high_cost`, `hide_low_confidence`, `hide_state`, `hide_already_ruled_out` | Reversible hide/flag rules. |

### Application Strategy

Use controlled values:

- `safer_list`;
- `balanced_list`;
- `reach_heavy_list`.

Also ask:

- `target_application_count`: default `25`;
- `include_reach_schools`: yes/no.

### Geography

Use controlled values:

- home-state priority;
- Florida priority;
- national openness;
- specific states to avoid;
- urban/suburban/rural preference.

Urban should be a supported preference value, not a hard-coded assumption.

`states_to_avoid` should be visible in the first slice as an optional control. It must only create reversible local hide/flag behavior.

### Lifestyle

Ask as low-friction preference sliders or choices:

- weather importance;
- airport access;
- family access;
- cost of living;
- social life / city energy;
- political/cultural comfort.

These initially affect explanation chips and awareness warnings, unless an existing deterministic field supports a documented rule.

### Cost Sensitivity

Use controlled values:

- low;
- medium;
- high;
- debt-averse.

This can change result grouping and warnings before changing core score formulas.

### Career Optionality

Use controlled values:

- undecided;
- emergency medicine leaning;
- competitive specialty optionality;
- academic/research optionality.

Keep this awareness-only in the first implementation unless existing deterministic fields support a documented rule.

### School Environment

Track:

- pass/fail importance;
- mandatory attendance tolerance;
- research-heavy vs clinically focused preference;
- large academic center vs community-focused preference.

If source coverage is incomplete, show the answer as a research prompt rather than as a score driver.

### Dealbreakers

Ask for:

- specific states to hide;
- rural schools to hide;
- high-cost schools to flag or hide;
- low-confidence schools to flag or hide;
- schools already ruled out.

Every dealbreaker action must be reversible.

## Copy Rules

- Use direct applicant language.
- Avoid "weights," "payload," "nodes," "algorithm," and "model" in the intake UI.
- Do not use slang.
- Do not imply admission probability.
- Explain uncertainty near the relevant question.
- Do not call a school "safe" or "likely" unless the label comes from an existing deterministic fit field and is explained as non-predictive.

## Schema Requirements

Each question should have:

- stable `question_id`;
- display label;
- short helper text;
- input type;
- allowed values;
- default;
- whether it affects filtering, grouping, scoring context, or awareness only.

## Acceptance Criteria

- Questions can be rendered from a single schema.
- All ranking-affecting answers use controlled values.
- Free-text notes do not affect rank or grouping.
- Missing answers have safe defaults.
- The question set does not ask for data that the current site cannot use or explain.
