# Visual QA Screenshots

## Objective

Use screenshots to review the current site before and after UX changes.

The goal is to make the site clearer and more usable, not to redesign blindly.

## Required Screenshots

Capture desktop and mobile screenshots for:

- default route / rankings page;
- rankings page with MD selector visible;
- rankings page after selector values are changed;
- rankings page with "Why This Rank?" open;
- methodology section/page;
- school dossier/profile index;
- one school dossier/profile page;
- hidden-school review state after at least one school is hidden;
- CSV export controls visible;
- mobile rankings view;
- mobile dossier view.

Suggested viewport sizes:

- desktop: `1440x1000`;
- tablet: `1024x768`;
- mobile: `390x844`.

## Output Location

```text
outputs/site_qa/screenshots/
```

Use stable names such as:

```text
rankings_desktop_before.png
rankings_desktop_after.png
rankings_mobile_after.png
school_dossier_desktop_after.png
hidden_schools_desktop_after.png
```

## Findings File

Create:

```text
outputs/site_qa/ux_review_findings.csv
```

Suggested columns:

```text
finding_id,route,viewport,severity,status,summary,evidence_path,fix_summary,notes
```

## Review Criteria

Look for:

- unreadable or overflowing table text;
- controls that look like static text;
- unclear MD-only selector caveat;
- hidden/private/local labels missing;
- excessive visual density without grouping;
- detail panels that are too hard to scan;
- missing empty states;
- export buttons that do not explain what is exported;
- mobile text overlap or unusable controls.

## Done Criteria

- Screenshots exist for required views.
- Findings are recorded.
- High-severity layout issues are fixed or explicitly deferred with reason.
- Updated screenshots confirm the fixes.
