# Residency and Match Plan

## Objective

Track match strength, national mobility, specialty optionality, and residency goal alignment without reducing them to prestige alone.

## Scope

This plan covers specialty opportunities, home residency programs, national match mobility, competitive specialty support, academic medicine pathways, and match list quality.

## Inputs

- School match lists.
- Home residency program lists.
- Department and faculty strength signals.
- Research infrastructure.
- Manual specialty goal preferences.

## Outputs

- `residency_goal_alignment_score`
- `specialty_optionality_score`
- `national_mobility_score`
- Specialty-specific strength scores.
- Source links for match and residency program evidence.

## Schema

Recommended fields:

- `home_residency_programs_notes`
- `match_list_source_url`
- `national_mobility_score`
- `residency_goal_alignment_score`
- `specialty_optionality_score`
- `ortho_strength_score`
- `derm_strength_score`
- `ent_strength_score`
- `plastics_strength_score`
- `neurosurgery_strength_score`
- `ophtho_strength_score`
- `academic_im_strength_score`
- `academic_surgery_strength_score`
- source metadata fields

## Source Policy

- Match lists should be linked and dated.
- Specialty strength scores are judgment unless backed by a defined formula.
- National mobility should not be inferred from prestige alone.
- Schools without home programs should not automatically score poorly if other evidence supports opportunity.

## Implementation Steps

1. Add normalized residency and match schema.
2. Add manual research template for specialty strengths.
3. Add fields for home residency programs and match list source URL.
4. Define specialty optionality scoring rubric.
5. Add emergency medicine interest fields without making specialty fit a high default weight.
6. Add scenario weighting for specialty optionality.

## Validation Rules

- Specialty scores must be blank or between 1 and 10.
- Match evidence requires a source URL or a manual note.
- Competitive specialty scores require confidence notes when high.

## Open Questions

- Which specialties matter most for this applicant right now?
- Should optionality be weighted more than current specialty interest?
- Should national mobility be categorical or 1-10?

## Current Defaults

- Emergency medicine is the current specialty interest.
- Specialty fit is low weight by default.
- Specialty data is mostly for awareness and later review, not early narrowing.
- MCAT/GPA fit matters more than specialty alignment during the first pass.

## Definition of Done

- Match and specialty data are separate from prestige.
- Specialty optionality scenario is explainable.
- Source links exist for researched schools.
- Weak evidence is flagged rather than hidden.
