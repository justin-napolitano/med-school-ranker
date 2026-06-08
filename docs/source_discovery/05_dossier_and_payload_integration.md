# 05 Dossier And Payload Integration

## Goal

Make the school profile useful for research, not just ranking.

Each school profile should link to:

- the school website from `data/school_master.csv` `website`,
- the selected official class-profile/admissions-stat source when available,
- the selected provisional source only when no official source exists.

## Payload Contract

Extend generated product payload schools with:

```text
websiteUrl
statsSourceUrl
statsSourceTitle
statsSourceType
statsSourceConfidence
statsCohortYear
statsPopulation
statsMetricType
statsLastChecked
statsEvidenceSummary
officialStatsAvailable
```

Allowed `statsSourceType` values:

- `official`
- `provisional_third_party`
- `crowdsourced_context`
- `missing`

## UI Copy Rules

Use clear labels:

- `School website`
- `Official stats source`
- `Provisional stats source`
- `Crowdsourced context`
- `Official source not found yet`

Do not show:

- `Verified` unless the source has been accepted by rule or review.
- `Acceptance probability` unless a future predictive model exists.
- `AI found this` as source language.

## Profile Placement

Add source links in the score/profile area where MCAT/GPA are shown, not hidden in methodology.

Minimum profile display:

- MCAT value and definition.
- GPA value and definition.
- Cohort year or `Year not stated`.
- Source-quality chip.
- `School website` link.
- `Official stats source` or fallback source link.
