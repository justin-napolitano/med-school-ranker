# School Cards And Score Cards

## Objective

Make school review feel like polished cards and reports instead of generated dossiers.

## School Card Polish

Cards should show:

- school name;
- degree and location;
- decision rank/status;
- academic fit summary;
- score-based admissions-fit signal with caveat;
- cost/location summary;
- reasons, risks, and missing data;
- local status;
- actions: Interested, Applying, None, Compare, Open Score Card.

Cards should not show raw source dumps unless expanded.

Cards should not show a manual `Hide` action. Hidden schools may show `Restore` in hidden review contexts, but visible cards should not invite routine hiding.

## Score Card Polish

The school page should read like a report:

1. `At A Glance`
2. `Why It Ranks Here`
3. `Academic Fit`
4. `Cost And Location`
5. `Application Notes`
6. `Data Quality`
7. `Source Details`

`Data Quality` and `Source Details` should be available but visually secondary.

## Copy Rules

- Use `Score Card`, not `Dossier`.
- Use `Out-of-state cost`, `In-state cost`, and `Total cost of attendance`.
- Explain missing MCAT/GPA as missing, assumed-match, low-confidence, or conflicting evidence.
- Explain score-fit labels as MCAT/GPA-based only, not as admit probability.
- Avoid raw field names in visible labels.

## Done Criteria

- Opening a school feels like a polished school report.
- Score-card first viewport has useful summary and actions.
- Product cards do not show a manual Hide button.
- Raw details are collapsed or secondary.
- Mobile cards do not overflow.
