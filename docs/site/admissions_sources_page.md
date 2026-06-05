# Site Plan: Admissions Sources Page

## Objective

Track the research queue for finding public, source-verified GPA/MCAT pages without scraping or inferring values in the site.

## Inputs

- `admissions_source_queue.json`
- `school_master.json`
- `admissions_stats.json`
- `data_quality_report.json`
- joined per-school derived payload

## Primary Table

Columns:

- school name
- degree type
- city
- state
- candidate source URL
- source status
- extraction status
- review status
- last checked
- admissions stats present flag
- notes

## Status Values

Suggested controlled values:

- source status: blank, not_started, candidate_found, no_public_source_found, restricted_source_only, verified
- extraction status: blank, manual_review_needed, parseable, not_parseable, imported
- review status: blank, needs_review, reviewed, rejected

## Filters

- Missing source URL.
- Candidate found.
- Needs review.
- Stats present.
- Degree type.
- State.

## Interactions

- Click candidate source URL to open source in new tab.
- Click school row to open School Detail.

## Non-Goals

- No scraping in the browser.
- No direct import from this page.
- No use of third-party stats as high-confidence values.

## Definition of Done

- It is clear which schools need admissions stats source research.
- Candidate URLs are clickable.
- Schools with stats already present are distinguishable.
- The page reinforces source confidence instead of hiding it.
