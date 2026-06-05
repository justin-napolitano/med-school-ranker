# Hidden Curriculum Plan

## Objective

Track day-to-day educational structure and student experience variables that often matter more than headline rankings.

## Scope

This plan covers true pass/fail, internal ranking, AOA, mandatory attendance, recorded lectures, weekly required hours, wellness reputation, and related curriculum burden.

## Inputs

- School curriculum pages.
- Student handbooks where public and allowed.
- Official admissions/curriculum FAQs.
- Current student reports, used cautiously and labeled as anecdotal.
- Manual research notes.

## Outputs

- `hidden_curriculum_score`
- Component hidden curriculum fields.
- Curriculum source links.
- Warnings for schools with high burden or unclear policy.

## Schema

Recommended fields:

- `true_pf_preclinical`
- `internal_ranking`
- `aoa_present`
- `mandatory_attendance`
- `recorded_lectures`
- `avg_weekly_required_hours`
- `wellness_reputation_score`
- `hidden_curriculum_score`
- `curriculum_source_url`
- `hidden_curriculum_notes`
- source metadata fields

## Source Policy

- Official school sources are preferred.
- Student reports can inform notes but should be labeled anecdotal.
- Do not infer true P/F from marketing language without policy evidence.
- Ambiguous policies should remain blank with notes.

## Implementation Steps

1. Add normalized hidden curriculum schema.
2. Add manual research template.
3. Define allowed values for categorical fields.
4. Add scoring rubric for hidden curriculum score.
5. Surface high-concern policies in workbook without making them heavy default ranking drivers.

## Validation Rules

- Categorical fields use controlled values such as yes, no, unclear, mixed, unknown.
- Wellness score must be blank or between 1 and 10.
- High hidden curriculum score requires enough component coverage.

## Open Questions

- How should AOA presence be scored if internal ranking is hidden?
- Should mandatory labs/small groups count differently from lectures?
- Should clinical-year grading be tracked separately?

## Current Defaults

- Hidden curriculum is important to know, but low weight in the default ranking algorithm.
- Mandatory attendance, graded/ranked preclinical, no recorded lectures, and AOA should appear as awareness flags.
- These factors can be promoted to stronger filters later if the partner cares more after review.

## Definition of Done

- Hidden curriculum is separate from general culture.
- Policy uncertainty is visible.
- Researched schools have source links and notes.
- Hidden curriculum score can be explained from components.
