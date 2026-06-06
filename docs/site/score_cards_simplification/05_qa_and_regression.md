# QA And Regression

## Required Checks

- `uv run pytest tests/test_phase1.py`
- `uv run med-school-validate`
- `uv run med-school-build-site`

## Manual Or Browser Checks

- Score Cards tab opens and reads as a school browser.
- Status switch works from Score Cards.
- School profile opens at the top.
- Status switch works from profile.
- Missing MCAT/GPA labels distinguish approved value, candidate-only evidence, and no candidate value found.
- Export still downloads local score-card edits.
- Data Details is collapsed by default and can be opened.
