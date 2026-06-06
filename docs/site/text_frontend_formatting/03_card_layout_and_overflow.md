# Card Layout and Overflow

## Purpose

Make school cards, score-card profiles, compare cards, and metric cards resilient to real school names and long explanation text.

## Requirements

- School names wrap inside cards.
- Fact-row labels and values wrap instead of overflowing.
- Metric values wrap inside cards.
- Badges and chips can wrap to multiple lines.
- Mobile fact rows collapse to one column.
- Desktop intake left and right panes scroll independently.

## QA Checklist

- Long school name in a guided card stays inside the card.
- Full cost labels do not push values outside the card.
- Compare cards remain readable with four selected schools.
- Score-card profile sections do not overflow on mobile.
- Intake state checkbox changes preserve the left pane scroll position.

## Guardrails

- Do not shrink text with viewport-width font scaling.
- Do not hide overflow in a way that clips important school names or explanations.
- Do not nest cards inside decorative cards.

