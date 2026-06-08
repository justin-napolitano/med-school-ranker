# 02 Official Source Acceptance Rules

## Goal

Prevent the pipeline from promoting convenient but weak sources into official stats.

## Acceptable Official Sources

A candidate can be accepted for official extraction when:

- The host matches the school website host in `data/school_master.csv`.
- The host is a parent university or medical center domain strongly associated with the school.
- The URL is on a `.edu` domain and page text/title clearly identifies the same medical school.
- The PDF or page is an official annual report, fact book, class profile, student profile, or admissions page for that school.

## Rejected Sources

Reject as official evidence:

- Google AI Overview, Bing Copilot output, Perplexity answers, ChatGPT output, or any AI-generated summary.
- Search result pages or snippets.
- Consultant/advising sites, ranking sites, forums, Reddit, SDN, blogs, and general aggregators.
- Generic university-wide pages that do not identify the medical school.
- Admissions requirement pages that only list minimum GPA/MCAT or MCAT date policies.
- Pages that discuss applicants generally but not admitted/matriculated/enrolled class statistics.

## Official Domain Labels

Use these labels:

- `official_school_domain`
- `official_parent_university_domain`
- `official_health_system_domain`
- `official_pdf_or_report_host`
- `ambiguous_official_domain`
- `third_party`
- `search_or_ai_summary`
- `unknown`

Only these can auto-proceed to extraction:

- `official_school_domain`
- `official_parent_university_domain`
- `official_health_system_domain`
- `official_pdf_or_report_host`

`ambiguous_official_domain` must enter review unless the page title and body contain a strong school-name match.

## Scoring Heuristic

Compute `official_domain_score` from 0 to 1:

- `1.00`: exact school host match.
- `0.95`: same registrable domain as school host and school name appears in page title/body.
- `0.90`: known parent university or medical center domain plus strong school-name match.
- `0.75`: `.edu` host plus school-name match but no known host relation.
- `0.50`: official-looking host but weak school identity.
- `0.00`: rejected third-party/search/AI host.

Auto-accept threshold:

- `official_domain_score >= 0.90`
- source type hint is not `unknown`
- candidate is not a rejected source class
