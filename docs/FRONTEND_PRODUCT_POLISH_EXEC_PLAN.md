# Frontend Product Polish Executive Plan

## Objective

Polish the existing public site into a serious, applicant-facing product.

This is not a workflow rebuild. The workflow is already good enough:

```text
Intake -> Rankings -> Interested/Applying -> Applications -> School Score Card -> Methodology/source transparency
```

The next work should make that existing path feel clear, beautiful, modern, and less admin-heavy.

## What Is Already Built

Do not spend this phase rebuilding these:

- guided intake;
- profile-aware rankings;
- intake menu on rankings;
- Interested/Applying/None status controls;
- Considering/Application-style list flows;
- 50 Interested and 25 Applying list limits;
- school score-card/profile routes;
- methodology/source transparency;
- local browser state and exports;
- admin/local versus publish-safe separation;
- GitHub Pages publish-safe deployment.

## Problem To Solve

The site works, but too much of it still feels like generated data:

- rankings still default toward table/admin thinking;
- cards need clearer hierarchy and better spacing;
- score cards should feel like polished school reports;
- status actions should be visually obvious and consistent;
- methodology needs to feel trustworthy without reading like a backend report;
- admin/data-quality/source views should be visually secondary;
- mobile needs polish around scrolling, card density, and action placement.

## Current Product Decisions

These are locked unless the user reverses them:

- Product cards should not expose a manual `Hide` button. Hidden-school state can still exist for filters, state/dealbreaker rules, and restore/review workflows, but routine card actions should be `Interested`, `Applying`, `None`, `Compare`, and `Open Score Card`.
- Add a score-based admissions-fit signal, but do not present it as true acceptance probability.
- Use labels like `Highly likely score fit`, `Likely score fit`, `Possible score fit`, `Reach on scores`, and `Unlikely score fit`.
- Every score-fit label must carry the caveat that it is based on MCAT/GPA fit signals only and is not an admit chance.

## Product Direction

The public product should feel:

- serious, credible, and current;
- built for Gen Z and early Gen Alpha applicants;
- direct, not gimmicky;
- visually polished without hiding uncertainty;
- card/report-first, with tables available as advanced views;
- transparent about missing or low-confidence data.

Avoid:

- admissions-office stiffness;
- decorative gradients, blobs, or one-hue palettes;
- unsupported recommendation language;
- burying caveats;
- adding more workflow states.

## Branch Strategy

Every slice starts from latest `main`, runs on its own implementation branch, and is merged before the next slice starts.

| Slice | Branch | Intent |
| --- | --- | --- |
| 0 | `impl-product-polish-foundation` | Visual tokens, typography, spacing, product/admin visual separation. |
| 1 | `impl-product-polish-intake-rankings` | Intake and Rankings product polish using the existing workflow. |
| 2 | `impl-product-polish-score-cards` | School cards and score-card profile report polish. |
| 3 | `impl-product-polish-applications-actions` | Interested/Applying/Application actions, limits, and empty states. |
| 4 | `impl-product-polish-mobile` | Mobile layout, side-menu scrolling, overflow, touch targets, responsive cards. |
| 5 | `impl-product-polish-qa` | Screenshot QA, copy pass, accessibility, publish-safe smoke review. |

## Execution Order

### Slice 0: Visual Foundation

Establish reusable visual tokens and public/admin distinction without changing scoring or workflow.

Use:

- [Visual System And Product Shell](site/product_polish/01_visual_system_and_product_shell.md)
- [QA And Publish-Safe Review](site/product_polish/06_qa_and_publish_safe_review.md)

### Slice 1: Intake And Rankings Polish

Make the current intake/rankings path feel like a guided product path, not a settings panel plus table.

Use:

- [Intake And Rankings Polish](site/product_polish/02_intake_and_rankings_polish.md)

### Slice 2: School Cards And Score Cards

Make school review feel like cards and reports instead of dossier/admin pages.

Use:

- [School Cards And Score Cards](site/product_polish/03_school_cards_and_score_cards.md)

### Slice 3: Applications And Actions

Make Interested/Applying actions and application-list limits obvious and pleasant.

Use:

- [Applications And Actions Polish](site/product_polish/04_applications_and_actions_polish.md)

### Slice 4: Mobile And Responsive Polish

Fix mobile/desktop layout friction after the primary surfaces have product polish.

Use:

- [Mobile And Responsive Polish](site/product_polish/05_mobile_and_responsive_polish.md)

### Slice 5: QA, Copy, And Publish-Safe Review

Run visual QA, copy consistency, accessibility checks, and publish-safe verification.

Use:

- [QA And Publish-Safe Review](site/product_polish/06_qa_and_publish_safe_review.md)
- [Critical Review](site/product_polish/CRITICAL_REVIEW.md)

## Guardrails

- Do not change scoring formulas.
- Do not add new source data or scraping.
- Do not implement predictive admissions probability.
- Do not add a backend, auth, database, React, Next, or Vercel migration.
- Do not commit private applicant answers.
- Do not invent new workflow states beyond None, Interested, and Applying.
- Do not reintroduce product-card Hide buttons.
- Do not remove advanced/admin views; make them secondary.
- Do not hide missing data, low confidence, or assumed-match labels.
- Do not label score fit as school-specific acceptance probability.
- Keep `publish_safe` deploy working after every slice.

## Done Criteria

The polish phase is done when:

- the existing workflow feels intentional from intake through application list;
- rankings and intake are understandable without reading documentation;
- school score cards look like credible applicant reports;
- status actions are obvious and consistent;
- admin/source/data-quality screens are accessible but not visually primary;
- mobile and desktop views have no incoherent overflow or scroll traps;
- methodology is clear, compact, and transparent;
- publish-safe GitHub Pages build/deploy remains green.
