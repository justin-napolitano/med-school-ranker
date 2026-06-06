# Intake And Rankings Polish

## Objective

Polish the existing intake and rankings experience so it feels like one guided product path.

The behavior already exists. This slice improves hierarchy, clarity, and presentation.

## In Scope

- Make intake sections easier to scan.
- Make the selected profile/ranking lens summary obvious.
- Improve ranking result layout without removing advanced table access.
- Make `Interested`, `Applying`, and `None` status visually clear.
- Collapse hidden/lower-priority content by default where appropriate.
- Keep methodology links close to score/rank explanations.

## Default Presentation

Rankings should feel like a review queue:

- high-signal school identity;
- decision rank/status;
- academic fit context;
- score-based admissions-fit signal;
- cost/location context;
- concise reason/risk chips;
- obvious status actions;
- compact `Why this rank?` disclosure;
- advanced table available but not dominant.

## Copy Rules

- Do not say a school is a guaranteed fit.
- Do not imply school-specific acceptance probability.
- Prefer `Review group`, `Fit signal`, `Source confidence`, and `Next action`.
- Use full labels for user-facing stats and cost fields.

## Score-Based Fit Labels

Add score-fit labels based on MCAT/GPA fit scores only:

- `Highly likely score fit`
- `Likely score fit`
- `Possible score fit`
- `Reach on scores`
- `Unlikely score fit`

These labels must not be called admittance likelihood or acceptance probability. The UI should explain that they are score-screen fit signals and do not include mission fit, activities, essays, timing, residency policy, interview performance, or committee behavior.

## Done Criteria

- Intake and Rankings feel connected.
- Default Rankings view is understandable without reading docs.
- Score-fit labels are visible and caveated.
- Advanced table remains accessible.
- Status actions do not cause layout jump or text overflow.
