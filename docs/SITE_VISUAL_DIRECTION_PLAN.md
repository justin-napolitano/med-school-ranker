# Site Visual Direction Plan

## Objective

Define the visual language for the applicant-facing medical school ranking site before the full design implementation begins.

This plan is intentionally downstream of [Site Profile Node UI Adoption Executive Plan](SITE_PROFILE_NODE_UI_ADOPTION_EXEC_PLAN.md). The design should style stable school cards, profile sections, ranking cards, and methodology surfaces after the site proves it can render from generated nodes.

The target feel:

```text
Serious, modern, source-literate, and digitally native.
Not institutional. Not gimmicky. Not a brochure.
```

## Audience

The primary audience is current and near-future medical school applicants, especially Gen Z and early Gen Alpha users who expect:

- fast mobile-first scanning;
- transparent evidence and source links;
- compact personalization controls;
- credible data without corporate/institutional stiffness;
- high-trust design that does not feel like a hospital intranet or an admissions-office PDF.

The site can still support parents, advisors, and collaborators, but it should not visually center their expectations.

## Product Personality

The site should feel like an applicant intelligence dashboard:

- analytical;
- honest;
- direct;
- fast;
- transparent;
- personalizable;
- credible enough to make real application-list decisions.

It should not feel:

- corporate;
- academic-administrative;
- marketing-heavy;
- playful for its own sake;
- trend-chasing;
- overexplained.

## Design Principles

### Serious Without Feeling Old

Use dense, modern card surfaces, strong type hierarchy, clear chips, and crisp interaction states. Avoid the navy-gray institutional dashboard pattern as the dominant visual language.

### Transparency As Interface

Source confidence, missing data, caveats, methodology, and "why this rank" explanations should be visible design elements, not footnotes.

### Mobile-First Density

The product should scan well on a phone without becoming a watered-down version of the desktop site. Cards should collapse intelligently, preserve the rank/fit/cost/source story, and keep actions reachable.

### Personalized But Not Gimmicky

Profile selectors, MCAT/GPA band controls, location preferences, shortlist state, compare state, and hide/restore controls should feel native to the product. Do not use forced youth language or novelty interactions.

### Missing Data Is A State

Unknown, partial, provisional, and low-confidence data need clear visual treatments. Missing values should never look like a design bug or become silent zeros.

## Visual Language

### Layout

- Use rankings and school cards as the primary applicant surface.
- Keep admin/source/build-health pages visually separate from applicant-facing routes.
- Prefer compact metric groups, sticky filters, comparison panels, and profile sections.
- Avoid oversized marketing heroes, decorative cards inside cards, and generic landing-page composition.

### Typography

- Use a modern sans-serif with strong readability at small sizes.
- Use tight but not cramped hierarchy.
- Reserve large type for page-level context only.
- Keep card text compact and scannable.
- Do not use decorative typefaces or artificially youthful display fonts.

### Color

Use a restrained neutral base with semantic accents:

- green: strong fit, low concern, complete/source-backed;
- amber: caution, partial confidence, review needed;
- red: hard concern, critical missing field, hard no;
- blue: source-backed information, methodology, neutral reference;
- gray: unknown, not reviewed, unavailable;
- one restrained accent for selected/shortlisted schools.

Avoid:

- all-navy institutional dashboards;
- single-hue purple/blue gradients;
- neon "youth" palettes;
- beige academic report styling;
- color meanings that compete with data confidence meanings.

### Cards

School cards should communicate the decision story quickly:

1. school name and location;
2. Decision Rank and bucket;
3. MCAT/GPA fit summary;
4. cost/debt summary;
5. top positive and negative drivers;
6. confidence and missing-data chips;
7. actions: profile, compare, shortlist, hide.

Cards should be data-dense, not decorative. They should look trustworthy enough for serious application planning while still feeling current.

### Motion And Interaction

Use subtle motion only where it helps:

- expanding card details;
- filter changes;
- shortlist/compare state changes;
- section reveal/collapse;
- hover/focus feedback.

Do not add animation as decoration. Keep interaction states fast and obvious.

## Anti-Patterns

Avoid:

- generic Bootstrap admin tables as the only serious surface;
- hospital intranet styling;
- admissions-office brochure tone;
- corporate stock-photo or fake campus imagery;
- forced slang or "fellow kids" copy;
- giant gradients and decorative blobs;
- burying methodology or source caveats;
- making missing data look polished but complete;
- hiding key controls behind unclear icons;
- broad visual redesign before node-backed cards are working.

## Research Notes

This direction is based on two relevant audience observations:

- McKinsey describes Gen Z as digitally native, pragmatic, and comfortable cross-referencing many information sources while seeking authenticity and truth.
- Raptive's 2025 Gen Z trust research reports that Gen Z users increasingly value credible, expert-driven open-web content, independent validation, and transparent practices.

Sources:

- McKinsey, "True Gen: Generation Z and its implications for companies": `https://mckinsey.com/~/media/McKinsey/Industries/Consumer%20Packaged%20Goods/Our%20Insights/True%20Gen%20Generation%20Z%20and%20its%20implications%20for%20companies/Generation-Z-and-its-implication-for-companies.pdf`
- Raptive / PRNewswire, "New Gen Z Research Reveals a Shift Toward Credible, Expert-Driven Open Web Content": `https://www.prnewswire.com/news-releases/new-gen-z-research-reveals-a-shift-toward-credible-expert-driven-open-web-content-302350718.html`

## Implementation Timing

### Now

- Keep this design direction documented.
- Use it to evaluate whether node-backed card/profile work is creating the right surfaces.
- Avoid implementing a full style system until card/profile nodes are consumed by the UI.

### After Profile Node UI Adoption

- Create the first visual system slice:
  - tokens;
  - semantic colors;
  - card components;
  - profile section layout;
  - mobile card behavior;
  - screenshot QA.

### After Visual System Slice

- Apply the style to rankings, profiles, compare, curated lists, and public methodology routes.
- Keep admin pages useful but visually distinct from applicant-facing pages.

## Acceptance Criteria

- The product reads as serious and high-trust without feeling institutionally dated.
- Applicant-facing pages prioritize cards, source confidence, and personal decision controls.
- The design supports mobile-first review without sacrificing density.
- The design makes rank, fit, cost, source confidence, and missing data immediately legible.
- The design avoids fake youth branding and broad visual polish before data contracts are stable.

## Child Plans

- [Audience and Voice](site/design_direction/01_audience_and_voice.md)
- [Visual System Foundations](site/design_direction/02_visual_system_foundations.md)
- [Cards and Mobile Patterns](site/design_direction/03_cards_and_mobile_patterns.md)
- [Transparency and Trust Patterns](site/design_direction/04_transparency_and_trust_patterns.md)
- [Design QA](site/design_direction/05_design_qa.md)
- [Critical Review](site/design_direction/CRITICAL_REVIEW.md)

