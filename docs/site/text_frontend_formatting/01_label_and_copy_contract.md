# Label and Copy Contract

## Purpose

Make labels readable to an applicant or partner reviewer who does not know the data model.

## Rules

- Use full labels on applicant-facing surfaces.
- Keep acronyms only when they are standard applicant vocabulary, such as MCAT, GPA, AAMC, MD, and DO.
- Avoid short internal abbreviations such as `OOS`, `COA`, and raw snake-case labels.
- Prefer one canonical label per concept.

## Canonical Labels

| Concept | Applicant-facing label |
| --- | --- |
| `estimated_coa_in_state` | In-state estimated cost |
| `estimated_coa_out_state` | Out-of-state estimated cost |
| `cost_basis` | Cost used for selected score |
| `published_mcat_average` | MCAT average |
| `published_gpa_average` | GPA average |
| `admissions_oos_friendliness_score` | Out-of-state fit |
| `dossier` user surface | Score Card |

## Implementation Notes

- Add or extend frontend display-label helpers before sprinkling literal labels across unrelated render functions.
- Keep internal keys intact until import/persistence migration is planned.
- When a table has limited width, prefer clearer labels and horizontal table scroll over cryptic abbreviations.

