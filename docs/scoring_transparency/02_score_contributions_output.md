# Score Contributions Output

## Objective

Generate a long-form audit table that decomposes every score into components.

This is the highest-value first implementation slice because it makes current scoring transparent without requiring a broad data-model migration.

## Output Files

Public/template build:

```text
outputs/score_contributions.csv
```

Private local build:

```text
outputs/private/score_contributions.private.csv
```

Optional future output:

```text
outputs/score_explanations.csv
```

## Grain

One row per:

```text
applicant_profile_id
school_id
score_model
score_group
component_column
```

Examples:

- Balanced model, Admissions Score, MCAT fit.
- Overall School Value, Attendance Score, cost.
- Admissions Realist scenario, admissions score.

## Required Columns

```text
applicant_profile_id
profile_name
profile_source
school_id
school_name
score_model
score_group
component_column
component_label
raw_applicant_value
raw_school_value
applicant_value_band
school_value_band
delta_value
delta_band
raw_context
normalized_score
component_weight
weight_basis
weighted_contribution
component_coverage_status
source_type
source_name
source_url
data_confidence
formula_note
missing_reason
warning
```

## Contribution Math

For a score group:

```text
weighted_contribution = normalized_score * component_weight / sum(weights_for_present_components)
```

Because missing data is excluded from weighted averages today, the contribution table must disclose the denominator actually used.

Required fields:

```text
weight_basis = "present_components_only" or "all_configured_components"
component_coverage_status = present | missing | excluded | warning
```

If future behavior changes to penalize missing data directly, the contribution output must make that explicit.

## Display and Privacy Policy

Use exact raw values only where they are public school facts or local private outputs.

Public-safe contribution displays should prefer:

- MCAT band instead of exact private MCAT.
- GPA band instead of exact private GPA.
- MCAT delta band instead of exact applicant-school delta when the applicant value is private.
- GPA delta band instead of exact applicant-school delta when the applicant value is private.
- Relationship labels such as `same_state`, `oos_policy_accepts`, `oos_policy_unknown`.
- Cost percentile band instead of unnecessary exact personal debt assumptions.

Even if applicant values are banded, a ranking generated from a real applicant profile is still private-derived. Keep real-profile ranking and contribution outputs under ignored private paths unless a separate publish-safe anonymization process is explicitly designed.

## Source Type Values

Suggested controlled values:

- `source_backed`
- `manual_partner_input`
- `applicant_profile`
- `derived_formula`
- `fallback`
- `missing`
- `excluded`

## Private Data Rules

- Public contribution output must use only committed public/template profiles.
- Private contribution output must live only under `outputs/private/`.
- Private contribution output must not enter site payloads, workbooks, or upload bundles unless a separate local-private build mode is explicitly implemented.

## Tests

Add tests for:

- contribution rows exist for scored components;
- weighted contributions sum to the displayed score within rounding tolerance;
- missing components are marked missing rather than scored as zero;
- hard-no rows are visible but excluded;
- private contribution output is ignored by upload bundle behavior;
- public output does not contain private profile IDs.
- public output does not expose exact private applicant values.

## Done Criteria

- A ranked school can be audited component by component.
- Contribution math matches ranking output.
- Private and public outputs stay separated.
