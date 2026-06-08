# Critical Review: Official MCAT/GPA Source Discovery

## High-Risk Assumptions

1. **Assumption: Most schools publish clean MCAT/GPA class profiles.**
   Risk: Many do not, and some publish only broad ranges, requirements, or marketing facts.
   Mitigation: Treat missing official source as a normal coverage state, not a failure.

2. **Assumption: Search will reliably find the right page.**
   Risk: Search snippets often surface consultant pages or stale PDFs before official sources.
   Mitigation: Search results are candidate URLs only; official-source rules and fetched evidence decide.

3. **Assumption: Official pages use consistent language.**
   Risk: Schools use `entering`, `accepted`, `matriculated`, `enrolled`, `average`, `median`, and `profile` inconsistently.
   Mitigation: Store population and metric type explicitly and route ambiguity to review.

4. **Assumption: PDF parsing will be robust.**
   Risk: Annual reports can be scanned, image-based, or layout-heavy.
   Mitigation: Build HTML first; queue PDFs when parser support is missing or extraction confidence is low.

5. **Assumption: Current `website` values are enough to establish official domains.**
   Risk: Some schools use parent university, admissions subdomains, or health-system hosts.
   Mitigation: Allow parent-domain scoring but require school-name evidence before auto-accepting.

6. **Assumption: Higher official quality always means better scoring.**
   Risk: Official values can be older or refer to a different population than third-party values.
   Mitigation: Do not collapse rows; selection policy must explain population/year/metric priority.

## Implementation Drift To Avoid

- Do not turn this into a generic web scraper with no school-specific identity checks.
- Do not add a dependency-heavy crawler before proving the narrow class-profile use case.
- Do not mutate `school_master.csv` directly during discovery; normalized stats and source tables should drive updates.
- Do not bury source links in admin-only views.
- Do not label provisional third-party values as official because they agree with each other.
- Do not use Google AI Overview, search snippets, or an LLM answer as evidence.

## Concrete Guardrails

- Every accepted official stat must have a fetched URL and evidence text.
- Every score-driving stat must have `data_confidence`.
- Every ambiguous source must produce a review row.
- Every generated table must have deterministic ordering.
- Manual review queue notes must survive reruns.
- Site copy must distinguish source quality in user-facing language.
