from __future__ import annotations

import csv
import html
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from med_school_ranker.paths import (
    AAMC_MCAT_GPA_GRID_CSV,
    ADMISSIONS_POLICIES_CSV,
    ADMISSIONS_SOURCE_QUEUE_CSV,
    ADMISSIONS_STATS_CANDIDATES_CSV,
    ADMISSIONS_STATS_CONFLICTS_CSV,
    ADMISSIONS_STATS_CSV,
    APPLICANT_PROFILES_CSV,
    COST_AND_DEBT_CANDIDATES_CSV,
    COST_AND_DEBT_CSV,
    COST_AND_DEBT_REVIEW_CSV,
    DATA_QUALITY_REPORT_CSV,
    LETTER_REQUIREMENTS_CSV,
    MASTER_CSV,
    OUT,
    PARTNER_INPUTS_CSV,
    RANKINGS_CSV,
    ROOT,
    SITE_DIR,
    SITE_INDEX_HTML,
    SOURCE_INTEGRATION_REPORT_CSV,
    SOURCE_MATCH_OVERRIDES_CSV,
    SOURCE_MATCH_REVIEW_CSV,
    SOURCE_REVIEW_QUEUE_CSV,
)


JSON_OUTPUTS = {
    "school_master": MASTER_CSV,
    "calculated_rankings": RANKINGS_CSV,
    "applicant_profiles": APPLICANT_PROFILES_CSV,
    "aamc_mcat_gpa_grid": AAMC_MCAT_GPA_GRID_CSV,
    "admissions_stats": ADMISSIONS_STATS_CSV,
    "cost_and_debt": COST_AND_DEBT_CSV,
    "admissions_policies": ADMISSIONS_POLICIES_CSV,
    "letter_requirements": LETTER_REQUIREMENTS_CSV,
    "partner_inputs": PARTNER_INPUTS_CSV,
    "source_match_overrides": SOURCE_MATCH_OVERRIDES_CSV,
    "source_review_queue": SOURCE_REVIEW_QUEUE_CSV,
    "admissions_source_queue": ADMISSIONS_SOURCE_QUEUE_CSV,
    "data_quality_report": DATA_QUALITY_REPORT_CSV,
    "source_integration_report": SOURCE_INTEGRATION_REPORT_CSV,
    "source_match_review": SOURCE_MATCH_REVIEW_CSV,
    "admissions_stats_candidates": ADMISSIONS_STATS_CANDIDATES_CSV,
    "admissions_stats_conflicts": ADMISSIONS_STATS_CONFLICTS_CSV,
    "cost_and_debt_candidates": COST_AND_DEBT_CANDIDATES_CSV,
    "cost_and_debt_review": COST_AND_DEBT_REVIEW_CSV,
    "project_subplans": ROOT / "data/project_subplans.csv",
}

SOURCE_TABLE_DIR = ROOT / "data/source_tables"
SOURCE_DIFFS_DIR = OUT / "source_diffs"
RAW_AAMC_MSAR_DIR = ROOT / "data/raw/aamc/msar_reports"

MCAT_GPA_FIELDS = {
    "mcat_median_accepted",
    "mcat_median_matriculated",
    "mcat_mean_enrolled",
    "mcat_10th_percentile",
    "mcat_25th_percentile",
    "mcat_75th_percentile",
    "mcat_90th_percentile",
    "overall_gpa_median_accepted",
    "overall_gpa_median_matriculated",
    "overall_gpa_mean_enrolled",
    "science_gpa_mean_enrolled",
}

TRUTHY = {"1", "true", "t", "yes", "y"}
US_STATE_ABBREVS = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUTHY


def parse_number(value: str | None) -> float | None:
    text = str(value or "").strip().replace("$", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def has_partner_input(row: dict[str, str]) -> bool:
    fields = [
        "could_live_here_4_years_score",
        "location_fit_score",
        "culture_fit_score",
        "regret_index_score",
        "hard_no_flag",
        "hard_no_reason",
        "partner_notes",
    ]
    return any(row.get(field, "").strip() for field in fields)


def has_admissions_stats(row: dict[str, str]) -> bool:
    return any(row.get(field, "").strip() for field in MCAT_GPA_FIELDS)


def first_by_school(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_school: dict[str, dict[str, str]] = {}
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id and school_id not in by_school:
            by_school[school_id] = row
    return by_school


def group_by_school(rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id:
            grouped[school_id].append(row)
    return grouped


def count_populated(rows: Iterable[dict[str, str]], field: str) -> int:
    return sum(1 for row in rows if row.get(field, "").strip())


def csv_row_count(path: Path) -> int:
    return len(read_csv(path))


def csv_file_count(path: Path) -> int:
    return len(list(path.glob("*.csv"))) if path.exists() else 0


def source_table_counts() -> dict[str, int]:
    if not SOURCE_TABLE_DIR.exists():
        return {}
    return {
        path.name: csv_row_count(path)
        for path in sorted(SOURCE_TABLE_DIR.glob("*.csv"))
    }


def count_raw_aamc_files() -> dict[str, int]:
    if not RAW_AAMC_MSAR_DIR.exists():
        return {"all": 0, "pdf": 0, "html": 0}
    files = [path for path in RAW_AAMC_MSAR_DIR.iterdir() if path.is_file()]
    return {
        "all": len(files),
        "pdf": sum(1 for path in files if path.suffix.lower() == ".pdf"),
        "html": sum(1 for path in files if path.suffix.lower() == ".html"),
    }


def tuition_status(school_master: list[dict[str, str]]) -> dict[str, object]:
    patch_rows = read_csv(SOURCE_TABLE_DIR / "aamc_msar_tuition_school_master_patch_candidates.csv")
    join_rows = read_csv(SOURCE_TABLE_DIR / "aamc_msar_tuition_school_master_join_candidates.csv")
    join_by_row = {row.get("aamc_source_row_number", ""): row for row in join_rows}
    safe_rows = []
    ambiguous_rows = []
    review_rows = []
    for row in patch_rows:
        join_row = join_by_row.get(row.get("aamc_source_row_number", ""), {})
        match_label = row.get("match_label", "")
        match_score = parse_number(join_row.get("match_score") or row.get("match_score")) or 0
        second_score = parse_number(join_row.get("second_match_score"))
        second_gap = match_score - second_score if second_score is not None else 999
        has_cost = any(
            (parse_number(row.get(field)) or 0) > 0
            for field in [
                "in_state_tuition_fees_insurance",
                "out_state_tuition_fees_insurance",
                "estimated_coa_in_state",
                "estimated_coa_out_state",
            ]
        )
        is_safe = has_cost and (match_label == "exact" or (match_label == "high_confidence" and second_gap >= 0.03))
        if is_safe:
            safe_rows.append(row)
        elif match_label == "high_confidence":
            ambiguous_rows.append(row)
        else:
            review_rows.append(row)

    md_rows = [row for row in school_master if row.get("degree_type") == "MD"]
    do_rows = [row for row in school_master if row.get("degree_type") == "DO"]
    safe_school_ids = {row.get("school_id") for row in safe_rows}
    return {
        "parsed_rows": csv_row_count(SOURCE_TABLE_DIR / "aamc_msar_tuition_fees_insurance.csv"),
        "patch_candidates": len(patch_rows),
        "safe_rows_after_gap_review": len(safe_rows),
        "ambiguous_high_confidence_rows": len(ambiguous_rows),
        "join_review_or_no_match_rows": sum(1 for row in join_rows if row.get("match_label") in {"review", "no_match"}),
        "md_rows_not_safe_yet": sum(1 for row in md_rows if row.get("school_id") not in safe_school_ids),
        "do_rows_missing_tuition": len(do_rows),
    }


def mcat_gpa_status() -> dict[str, object]:
    comparable_rows = read_csv(SOURCE_TABLE_DIR / "all_comparable_mcat_gpa_sources.csv")
    comparison_rows = read_csv(SOURCE_DIFFS_DIR / "mcat_gpa_source_comparison.csv")
    conflict_rows = read_csv(SOURCE_DIFFS_DIR / "mcat_gpa_conflicts.csv")
    admissions_stats = read_csv(ADMISSIONS_STATS_CSV)
    source_counts = Counter(row.get("source_key", "") or "unknown" for row in comparable_rows)
    agreement_counts = Counter(row.get("agreement_label", "") or "unknown" for row in comparison_rows)
    quality_counts = Counter(row.get("data_quality_band", "") or "unknown" for row in admissions_stats)
    return {
        "comparable_rows": len(comparable_rows),
        "rows_with_gpa": count_populated(comparable_rows, "gpa"),
        "rows_with_mcat": count_populated(comparable_rows, "mcat"),
        "source_counts": dict(sorted(source_counts.items())),
        "comparison_clusters": len(comparison_rows),
        "conflict_rows": len(conflict_rows),
        "agreement_counts": dict(sorted(agreement_counts.items())),
        "quality_counts": dict(sorted(quality_counts.items())),
    }


def source_status(
    school_master: list[dict[str, str]],
    admissions_stats: list[dict[str, str]],
    cost_and_debt: list[dict[str, str]],
    admissions_policies: list[dict[str, str]],
    letter_requirements: list[dict[str, str]],
    source_review_queue: list[dict[str, str]],
    project_subplans: list[dict[str, str]],
    source_match_overrides: list[dict[str, str]],
) -> dict[str, object]:
    source_plans = [
        row
        for row in project_subplans
        if row.get("plan_id") in {"source_data_integration_exec", "headless_source_phase_2a", "admissions_stats", "cost_and_debt"}
    ]
    canonical_counts = {
        "school_master_rows": len(school_master),
        "admissions_stats_rows": len(admissions_stats),
        "cost_and_debt_rows": len(cost_and_debt),
        "admissions_policy_rows": len(admissions_policies),
        "letter_requirement_rows": len(letter_requirements),
        "source_review_queue_rows": len(source_review_queue),
        "open_source_review_rows": sum(1 for row in source_review_queue if row.get("review_status", "").strip().lower() in {"", "open"}),
        "school_master_median_mcat_populated": count_populated(school_master, "median_mcat"),
        "school_master_median_gpa_populated": count_populated(school_master, "median_gpa"),
        "school_master_in_state_tuition_populated": count_populated(school_master, "in_state_tuition_fees_insurance"),
        "school_master_out_state_tuition_populated": count_populated(school_master, "out_state_tuition_fees_insurance"),
        "school_master_estimated_coa_in_state_populated": count_populated(school_master, "estimated_coa_in_state"),
        "school_master_estimated_coa_out_state_populated": count_populated(school_master, "estimated_coa_out_state"),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_table_count": csv_file_count(SOURCE_TABLE_DIR),
        "source_diff_file_count": len(list(SOURCE_DIFFS_DIR.glob("*"))) if SOURCE_DIFFS_DIR.exists() else 0,
        "raw_aamc_files": count_raw_aamc_files(),
        "source_tables": source_table_counts(),
        "canonical_counts": canonical_counts,
        "manual_override_count": len(source_match_overrides),
        "tuition": tuition_status(school_master),
        "mcat_gpa": mcat_gpa_status(),
        "source_plans": source_plans,
    }


def suggested_next_action(
    partner_row: dict[str, str],
    source_row: dict[str, str],
    warning_count: int,
    error_count: int,
) -> str:
    if not has_partner_input(partner_row):
        return "review partner input"
    if not source_row.get("candidate_source_url", "").strip():
        return "find admissions source"
    if warning_count or error_count:
        return "review data quality"
    return "review ranking"


def build_site_payload() -> dict[str, object]:
    school_master = read_csv(MASTER_CSV)
    rankings = read_csv(RANKINGS_CSV)
    applicant_profiles = read_csv(APPLICANT_PROFILES_CSV)
    admissions_stats = read_csv(ADMISSIONS_STATS_CSV)
    aamc_mcat_gpa_grid = read_csv(AAMC_MCAT_GPA_GRID_CSV)
    cost_and_debt = read_csv(COST_AND_DEBT_CSV)
    admissions_policies = read_csv(ADMISSIONS_POLICIES_CSV)
    letter_requirements = read_csv(LETTER_REQUIREMENTS_CSV)
    partner_inputs = read_csv(PARTNER_INPUTS_CSV)
    source_match_overrides = read_csv(SOURCE_MATCH_OVERRIDES_CSV)
    source_review_queue = read_csv(SOURCE_REVIEW_QUEUE_CSV)
    source_queue = read_csv(ADMISSIONS_SOURCE_QUEUE_CSV)
    data_quality = read_csv(DATA_QUALITY_REPORT_CSV)
    project_subplans = read_csv(ROOT / "data/project_subplans.csv")

    rankings_by_school = first_by_school(rankings)
    partner_by_school = first_by_school(partner_inputs)
    source_by_school = first_by_school(source_queue)
    stats_by_school = first_by_school(admissions_stats)
    cost_by_school = first_by_school(cost_and_debt)
    policies_by_school = group_by_school(admissions_policies)
    letters_by_school = group_by_school(letter_requirements)
    source_reviews_by_school = group_by_school(source_review_queue)

    warning_counts: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()
    issues_by_school: dict[str, list[dict[str, str]]] = defaultdict(list)
    for issue in data_quality:
        school_id = issue.get("row_id", "").strip()
        severity = issue.get("severity", "").strip().lower()
        if not school_id:
            continue
        if severity == "warning":
            warning_counts[school_id] += 1
        elif severity == "error":
            error_counts[school_id] += 1
        issues_by_school[school_id].append(issue)

    schools = []
    for school in school_master:
        school_id = school.get("school_id", "")
        partner_row = partner_by_school.get(school_id, {})
        source_row = source_by_school.get(school_id, {})
        stats_row = stats_by_school.get(school_id, {})
        cost_row = cost_by_school.get(school_id, {})
        policy_rows = policies_by_school.get(school_id, [])
        letter_rows = letters_by_school.get(school_id, [])
        review_rows = source_reviews_by_school.get(school_id, [])
        warning_count = warning_counts[school_id]
        error_count = error_counts[school_id]
        schools.append(
            {
                "school": school,
                "ranking": rankings_by_school.get(school_id, {}),
                "partner_input": partner_row,
                "admissions_source": source_row,
                "admissions_stats": stats_row,
                "cost_and_debt": cost_row,
                "admissions_policies": policy_rows,
                "letter_requirements": letter_rows,
                "source_review_queue": review_rows,
                "data_quality": issues_by_school.get(school_id, []),
                "derived": {
                    "warning_count": warning_count,
                    "error_count": error_count,
                    "partner_input_status": "present" if has_partner_input(partner_row) else "missing",
                    "partner_notes_indicator": "yes" if partner_row.get("partner_notes", "").strip() else "no",
                    "hard_no_flag": is_truthy(partner_row.get("hard_no_flag")),
                    "admissions_stats_present": "yes" if has_admissions_stats(stats_row) else "no",
                    "admissions_data_quality_band": stats_row.get("data_quality_band", "").strip() or "missing",
                    "published_mcat_band": stats_row.get("published_mcat_band", "").strip() or "missing",
                    "published_gpa_band": stats_row.get("published_gpa_band", "").strip() or "missing",
                    "aamc_acceptance_rate_band": stats_row.get("aamc_acceptance_rate_band", "").strip() or "missing",
                    "cost_data_present": "yes" if cost_row else "no",
                    "admissions_policy_count": len(policy_rows),
                    "letter_requirement_count": len(letter_rows),
                    "source_review_count": len(review_rows),
                    "source_queue_status": source_row.get("source_status", "").strip() or "not_started",
                    "suggested_next_action": suggested_next_action(
                        partner_row,
                        source_row,
                        warning_count,
                        error_count,
                    ),
                },
            }
        )

    degree_counts = Counter(row.get("degree_type", "Unknown") or "Unknown" for row in school_master)
    status = source_status(
        school_master,
        admissions_stats,
        cost_and_debt,
        admissions_policies,
        letter_requirements,
        source_review_queue,
        project_subplans,
        source_match_overrides,
    )
    return {
        "meta": {
            "site_privacy_mode": "local_full",
            "active_school_count": len(school_master),
            "degree_counts": dict(sorted(degree_counts.items())),
            "generated_at": status["generated_at"],
        },
        "source_status": status,
        "schools": schools,
        "school_master": school_master,
        "calculated_rankings": rankings,
        "applicant_profiles": applicant_profiles,
        "aamc_mcat_gpa_grid": aamc_mcat_gpa_grid,
        "admissions_stats": admissions_stats,
        "cost_and_debt": cost_and_debt,
        "admissions_policies": admissions_policies,
        "letter_requirements": letter_requirements,
        "partner_inputs": partner_inputs,
        "source_match_overrides": source_match_overrides,
        "source_review_queue": source_review_queue,
        "admissions_source_queue": source_queue,
        "data_quality_report": data_quality,
        "project_subplans": project_subplans,
    }


def write_site_json(payload: dict[str, object]) -> None:
    data_dir = SITE_DIR / "data"
    for key, source in JSON_OUTPUTS.items():
        write_json(data_dir / f"{key}.json", read_csv(source))
    write_json(data_dir / "source_status.json", payload["source_status"])
    write_json(data_dir / "site_payload.json", payload)


def render_site_html(payload: dict[str, object]) -> str:
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    escaped_payload = html.escape(payload_json, quote=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Medical School Ranker</title>
  <style>{CSS}</style>
</head>
<body>
  <header class="app-header">
    <div>
      <h1>Medical School Ranker</h1>
      <p id="summaryText">Static local review dashboard</p>
    </div>
    <label class="search-label">Search
      <input id="globalSearch" type="search" placeholder="School, city, state">
    </label>
  </header>
  <nav class="tabs" aria-label="Primary views">
    <button data-view="dashboard" class="active">Dashboard</button>
    <button data-view="status">Status</button>
    <button data-view="rankings">Rankings</button>
    <button data-view="detail">School Detail</button>
    <button data-view="partner">Partner Review</button>
    <button data-view="sources">Admissions Sources</button>
    <button data-view="quality">Data Quality</button>
    <button data-view="plans">Plans</button>
  </nav>
  <main>
    <section id="dashboard" class="view active"></section>
    <section id="status" class="view"></section>
    <section id="rankings" class="view"></section>
    <section id="detail" class="view"></section>
    <section id="partner" class="view"></section>
    <section id="sources" class="view"></section>
    <section id="quality" class="view"></section>
    <section id="plans" class="view"></section>
  </main>
  <script type="application/json" id="site-data">{escaped_payload}</script>
  <script>{JS}</script>
</body>
</html>
"""


CSS = r"""
:root {
  color-scheme: light;
  --border: #d7dee8;
  --header: #13324f;
  --muted: #627386;
  --bg: #f5f7fa;
  --panel: #ffffff;
  --accent: #146c94;
  --warn: #8a5a00;
  --error: #a12d2d;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: #172331;
}
.app-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
  padding: 18px 22px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}
h1 { margin: 0; font-size: 22px; color: var(--header); }
h2 { margin: 0 0 12px; font-size: 18px; color: var(--header); }
h3 { margin: 0 0 8px; font-size: 15px; color: var(--header); }
p { margin: 4px 0 0; color: var(--muted); }
.search-label { display: grid; gap: 4px; color: var(--muted); font-size: 12px; min-width: 280px; }
input, select {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  font: inherit;
  background: #fff;
}
.tabs {
  display: flex;
  gap: 6px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: #eaf0f6;
  overflow-x: auto;
}
button {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  background: #fff;
  color: #203347;
  cursor: pointer;
  white-space: nowrap;
}
button.active { background: var(--accent); border-color: var(--accent); color: #fff; }
main { padding: 18px; }
.view { display: none; }
.view.active { display: block; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 18px; }
.metric, .panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
}
.metric strong { display: block; font-size: 24px; color: var(--header); }
.filters { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 12px; align-items: end; }
.table-wrap { overflow: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); }
table { width: 100%; border-collapse: collapse; min-width: 900px; }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; font-size: 13px; }
th { position: sticky; top: 0; background: #eef4f8; color: var(--header); cursor: pointer; z-index: 1; }
tr:hover td { background: #f8fbfd; }
.badge { display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; border: 1px solid var(--border); background: #f7fafc; }
.badge.warn { color: var(--warn); border-color: #e6c773; background: #fff8df; }
.badge.error { color: var(--error); border-color: #e7aaaa; background: #fff0f0; }
.badge.good { color: #17623a; border-color: #a9d6bb; background: #eefaf2; }
.muted { color: var(--muted); }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
a { color: var(--accent); }
@media (max-width: 760px) {
  .app-header { display: grid; align-items: stretch; }
  .search-label { min-width: 0; }
  main { padding: 12px; }
}
"""


JS = r"""
const payload = JSON.parse(document.getElementById('site-data').textContent);
let currentView = 'dashboard';
let selectedSchoolId = payload.schools[0]?.school?.school_id || '';
let sortState = {};
let filters = {
  rankings: {degree: '', state: '', tier: '', bucket: '', hardNo: '', warnings: '', partner: '', quality: '', mcatBand: '', gpaBand: '', aamcRateBand: ''},
  sources: {sourceMissing: ''},
};

const $ = (id) => document.getElementById(id);
const missing = (value) => value === undefined || value === null || value === '' ? 'Missing' : value;
const truthy = (value) => ['1','true','t','yes','y'].includes(String(value || '').toLowerCase());
const schoolText = (item) => [
  item.school.school_name,
  item.school.city,
  item.school.state,
  item.school.degree_type,
].join(' ').toLowerCase();

function filteredSchools() {
  const query = $('globalSearch').value.trim().toLowerCase();
  return payload.schools.filter(item => !query || schoolText(item).includes(query));
}

function setView(view) {
  currentView = view;
  document.querySelectorAll('.tabs button').forEach(btn => btn.classList.toggle('active', btn.dataset.view === view));
  document.querySelectorAll('.view').forEach(section => section.classList.toggle('active', section.id === view));
  render();
}

function openDetail(schoolId) {
  selectedSchoolId = schoolId;
  setView('detail');
}

function metric(label, value) {
  return `<div class="metric"><span class="muted">${label}</span><strong>${value}</strong></div>`;
}

function badge(text, type='') {
  return `<span class="badge ${type}">${text}</span>`;
}

function table(headers, rows, key) {
  const head = headers.map(h => `<th data-key="${h.key}" data-table="${key}">${h.label}</th>`).join('');
  const body = rows.map(row => `<tr>${headers.map(h => `<td>${h.render(row)}</td>`).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${headers.length}">No rows</td></tr>`}</tbody></table></div>`;
}

function optionTags(values, selected) {
  return values.map(value => `<option value="${value}" ${value === selected ? 'selected' : ''}>${value}</option>`).join('');
}

function sortRows(rows, tableKey, defaultKey, defaultDir='asc') {
  const state = sortState[tableKey] || {key: defaultKey, dir: defaultDir};
  return [...rows].sort((a, b) => {
    const av = String(state.get ? state.get(a) : state.key.split('.').reduce((o,k)=>o?.[k], a) || '').toLowerCase();
    const bv = String(state.get ? state.get(b) : state.key.split('.').reduce((o,k)=>o?.[k], b) || '').toLowerCase();
    const an = Number(av), bn = Number(bv);
    const result = !Number.isNaN(an) && !Number.isNaN(bn) ? an - bn : av.localeCompare(bv);
    return state.dir === 'desc' ? -result : result;
  });
}

function warningCount() { return payload.data_quality_report.filter(i => i.severity === 'warning').length; }
function errorCount() { return payload.data_quality_report.filter(i => i.severity === 'error').length; }
function sourceStatus() { return payload.source_status || {}; }
function sourceMetric(path, fallback='0') {
  const value = path.split('.').reduce((obj, key) => obj?.[key], sourceStatus());
  return value === undefined || value === null || value === '' ? fallback : value;
}

function renderStatusSummary() {
  return `<div class="panel">
    <h2>Current Source Status</h2>
    <div class="grid">
      ${metric('Source tables', sourceMetric('source_table_count'))}
      ${metric('Raw AAMC files', sourceMetric('raw_aamc_files.all'))}
      ${metric('GPA/MCAT clusters', sourceMetric('mcat_gpa.comparison_clusters'))}
      ${metric('GPA/MCAT conflicts', sourceMetric('mcat_gpa.conflict_rows'))}
      ${metric('Tuition patch candidates', sourceMetric('tuition.patch_candidates'))}
      ${metric('Safe tuition rows', sourceMetric('tuition.safe_rows_after_gap_review'))}
      ${metric('Ambiguous tuition rows', sourceMetric('tuition.ambiguous_high_confidence_rows'))}
      ${metric('Manual overrides', sourceMetric('manual_override_count'))}
      ${metric('Canonical admissions stats', sourceMetric('canonical_counts.admissions_stats_rows'))}
      ${metric('Canonical cost rows', sourceMetric('canonical_counts.cost_and_debt_rows'))}
      ${metric('Open source reviews', sourceMetric('canonical_counts.open_source_review_rows'))}
    </div>
    <p>Generated ${missing(payload.meta.generated_at)}. Canonical rows are promoted only when source match and confidence rules pass; unresolved rows remain visible in review outputs.</p>
  </div>`;
}

function renderDashboard() {
  const schools = filteredSchools();
  const md = payload.schools.filter(s => s.school.degree_type === 'MD').length;
  const degreeDo = payload.schools.filter(s => s.school.degree_type === 'DO').length;
  const partnerPresent = payload.schools.filter(s => s.derived.partner_input_status === 'present').length;
  const hardNo = payload.schools.filter(s => s.derived.hard_no_flag).length;
  const sourceFound = payload.schools.filter(s => s.admissions_source.candidate_source_url).length;
  const priority = schools
    .filter(s => s.derived.suggested_next_action !== 'review ranking')
    .slice(0, 20);
  $('dashboard').innerHTML = `
    <div class="grid">
      ${metric('Active schools', payload.meta.active_school_count)}
      ${metric('MD', md)}
      ${metric('DO', degreeDo)}
      ${metric('Partner inputs', partnerPresent)}
      ${metric('Hard no', hardNo)}
      ${metric('Errors', errorCount())}
      ${metric('Warnings', warningCount())}
      ${metric('Admissions sources found', sourceFound)}
    </div>
    ${renderStatusSummary()}
    <div class="panel">
      <h2>Top Research Priorities</h2>
      ${table([
        {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
        {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
        {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
        {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
        {key:'derived.partner_input_status', label:'Partner', render:s=>s.derived.partner_input_status},
        {key:'derived.suggested_next_action', label:'Next Action', render:s=>s.derived.suggested_next_action},
      ], priority, 'dashboard')}
    </div>`;
}

function linkSchool(item) {
  return `<a href="#" data-school="${item.school.school_id}">${item.school.school_name}</a>`;
}

function rankingFilters() {
  const degrees = [...new Set(payload.schools.map(s => s.school.degree_type).filter(Boolean))].sort();
  const states = [...new Set(payload.schools.map(s => s.school.state).filter(Boolean))].sort();
  const tiers = [...new Set(payload.schools.map(s => s.ranking.dynamic_tier).filter(Boolean))].sort();
  const buckets = [...new Set(payload.schools.map(s => s.ranking.suggested_funnel_bucket).filter(Boolean))].sort();
  const qualities = [...new Set(payload.schools.map(s => s.derived.admissions_data_quality_band).filter(Boolean))].sort();
  const mcatBands = [...new Set(payload.schools.map(s => s.derived.published_mcat_band).filter(Boolean))].sort();
  const gpaBands = [...new Set(payload.schools.map(s => s.derived.published_gpa_band).filter(Boolean))].sort();
  const aamcRateBands = [...new Set(payload.schools.map(s => s.derived.aamc_acceptance_rate_band).filter(Boolean))].sort();
  const f = filters.rankings;
  return `
    <div class="filters">
      <label>Degree <select id="rankDegree"><option value="" ${f.degree === '' ? 'selected' : ''}>All</option>${optionTags(degrees, f.degree)}</select></label>
      <label>State <select id="rankState"><option value="" ${f.state === '' ? 'selected' : ''}>All</option>${optionTags(states, f.state)}</select></label>
      <label>Tier <select id="rankTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
      <label>Bucket <select id="rankBucket"><option value="" ${f.bucket === '' ? 'selected' : ''}>All</option>${optionTags(buckets, f.bucket)}</select></label>
      <label>Hard No <select id="rankHardNo"><option value="" ${f.hardNo === '' ? 'selected' : ''}>All</option><option value="yes" ${f.hardNo === 'yes' ? 'selected' : ''}>Yes</option><option value="no" ${f.hardNo === 'no' ? 'selected' : ''}>No</option></select></label>
      <label>Warnings <select id="rankWarnings"><option value="" ${f.warnings === '' ? 'selected' : ''}>All</option><option value="yes" ${f.warnings === 'yes' ? 'selected' : ''}>Has warnings</option><option value="no" ${f.warnings === 'no' ? 'selected' : ''}>No warnings</option></select></label>
      <label>Partner <select id="rankPartner"><option value="" ${f.partner === '' ? 'selected' : ''}>All</option><option value="present" ${f.partner === 'present' ? 'selected' : ''}>Present</option><option value="missing" ${f.partner === 'missing' ? 'selected' : ''}>Missing</option></select></label>
      <label>Stats Quality <select id="rankQuality"><option value="" ${f.quality === '' ? 'selected' : ''}>All</option>${optionTags(qualities, f.quality)}</select></label>
      <label>MCAT Band <select id="rankMcatBand"><option value="" ${f.mcatBand === '' ? 'selected' : ''}>All</option>${optionTags(mcatBands, f.mcatBand)}</select></label>
      <label>GPA Band <select id="rankGpaBand"><option value="" ${f.gpaBand === '' ? 'selected' : ''}>All</option>${optionTags(gpaBands, f.gpaBand)}</select></label>
      <label>AAMC Rate Band <select id="rankAamcRateBand"><option value="" ${f.aamcRateBand === '' ? 'selected' : ''}>All</option>${optionTags(aamcRateBands, f.aamcRateBand)}</select></label>
    </div>`;
}

function rankingsRows() {
  const {degree, state, tier, bucket, hardNo, warnings, partner, quality, mcatBand, gpaBand, aamcRateBand} = filters.rankings;
  return filteredSchools().filter(s => {
    if (degree && s.school.degree_type !== degree) return false;
    if (state && s.school.state !== state) return false;
    if (tier && s.ranking.dynamic_tier !== tier) return false;
    if (bucket && s.ranking.suggested_funnel_bucket !== bucket) return false;
    if (hardNo === 'yes' && !s.derived.hard_no_flag) return false;
    if (hardNo === 'no' && s.derived.hard_no_flag) return false;
    if (warnings === 'yes' && s.derived.warning_count < 1) return false;
    if (warnings === 'no' && s.derived.warning_count > 0) return false;
    if (partner && s.derived.partner_input_status !== partner) return false;
    if (quality && s.derived.admissions_data_quality_band !== quality) return false;
    if (mcatBand && s.derived.published_mcat_band !== mcatBand) return false;
    if (gpaBand && s.derived.published_gpa_band !== gpaBand) return false;
    if (aamcRateBand && s.derived.aamc_acceptance_rate_band !== aamcRateBand) return false;
    return true;
  });
}

function renderRankings() {
  $('rankings').innerHTML = `<h2>Rankings</h2>${rankingFilters()}<div id="rankTable"></div>`;
  const bindings = {
    rankDegree: 'degree',
    rankState: 'state',
    rankTier: 'tier',
    rankBucket: 'bucket',
    rankHardNo: 'hardNo',
    rankWarnings: 'warnings',
    rankPartner: 'partner',
    rankQuality: 'quality',
    rankMcatBand: 'mcatBand',
    rankGpaBand: 'gpaBand',
    rankAamcRateBand: 'aamcRateBand',
  };
  Object.entries(bindings).forEach(([id, key]) => $(id).addEventListener('change', event => {
    filters.rankings[key] = event.target.value;
    renderRankingTable();
  }));
  renderRankingTable();
}

function renderRankingTable() {
  const rows = sortRows(rankingsRows(), 'rankings', 'ranking.overall_rank');
  $('rankTable').innerHTML = `<p>${rows.length} visible schools</p>` + table([
    {key:'ranking.overall_rank', label:'Rank', render:s=>missing(s.ranking.overall_rank)},
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'ranking.dynamic_tier', label:'Tier', render:s=>missing(s.ranking.dynamic_tier)},
    {key:'ranking.suggested_funnel_bucket', label:'Bucket', render:s=>missing(s.ranking.suggested_funnel_bucket)},
    {key:'ranking.overall_school_value', label:'Overall', render:s=>missing(s.ranking.overall_school_value)},
    {key:'ranking.admissions_score', label:'Admissions', render:s=>missing(s.ranking.admissions_score)},
    {key:'ranking.attendance_score', label:'Attendance', render:s=>missing(s.ranking.attendance_score)},
    {key:'ranking.data_completeness_score', label:'Data', render:s=>missing(s.ranking.data_completeness_score)},
    {key:'derived.admissions_data_quality_band', label:'Stats Quality', render:s=>badge(s.derived.admissions_data_quality_band)},
    {key:'admissions_stats.published_mcat_average', label:'MCAT Avg', render:s=>missing(s.admissions_stats.published_mcat_average)},
    {key:'admissions_stats.published_gpa_average', label:'GPA Avg', render:s=>missing(s.admissions_stats.published_gpa_average)},
    {key:'derived.published_mcat_band', label:'MCAT Band', render:s=>missing(s.derived.published_mcat_band)},
    {key:'derived.published_gpa_band', label:'GPA Band', render:s=>missing(s.derived.published_gpa_band)},
    {key:'admissions_stats.aamc_acceptance_rate', label:'AAMC Rate', render:s=>missing(s.admissions_stats.aamc_acceptance_rate)},
    {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
    {key:'derived.hard_no_flag', label:'Hard No', render:s=>s.derived.hard_no_flag ? badge('Hard No', 'error') : ''},
    {key:'derived.partner_input_status', label:'Partner', render:s=>s.derived.partner_input_status},
  ], rows, 'rankings');
}

function renderDetail() {
  const item = payload.schools.find(s => s.school.school_id === selectedSchoolId) || payload.schools[0];
  if (!item) { $('detail').innerHTML = '<p>No school selected.</p>'; return; }
  selectedSchoolId = item.school.school_id;
  const sourceUrl = item.school.source_url ? `<a href="${item.school.source_url}" target="_blank">Source</a>` : 'Missing';
  $('detail').innerHTML = `
    <h2>${item.school.school_name}</h2>
    <p>${item.school.degree_type} · ${missing(item.school.city)}, ${missing(item.school.state)} · ${sourceUrl}</p>
    <div class="detail-grid">
      ${detailPanel('Identity', [
        ['School ID', item.school.school_id],
        ['Parent', item.school.parent_school_name],
        ['Campus', item.school.campus_name],
        ['Accreditation', item.school.accreditation_status],
      ])}
      ${detailPanel('Ranking', [
        ['Overall rank', item.ranking.overall_rank],
        ['Tier', item.ranking.dynamic_tier],
        ['Bucket', item.ranking.suggested_funnel_bucket],
        ['Admissions', item.ranking.admissions_score],
        ['Attendance', item.ranking.attendance_score],
        ['Data completeness', item.ranking.data_completeness_score],
      ])}
      ${detailPanel('Partner Review', [
        ['Could live here', item.partner_input.could_live_here_4_years_score],
        ['Location fit', item.partner_input.location_fit_score],
        ['Culture fit', item.partner_input.culture_fit_score],
        ['Regret index', item.partner_input.regret_index_score],
        ['Hard no', item.derived.hard_no_flag ? 'Yes' : 'No'],
        ['Reason', item.partner_input.hard_no_reason],
        ['Notes', item.partner_input.partner_notes],
      ])}
      ${detailPanel('Admissions Research', [
        ['Source status', item.derived.source_queue_status],
        ['Candidate URL', item.admissions_source.candidate_source_url],
        ['Stats present', item.derived.admissions_stats_present],
        ['Published source count', item.admissions_stats.published_source_count],
        ['Published MCAT average', item.admissions_stats.published_mcat_average],
        ['Published GPA average', item.admissions_stats.published_gpa_average],
        ['MCAT spread', item.admissions_stats.published_mcat_spread],
        ['GPA spread', item.admissions_stats.published_gpa_spread],
        ['Data quality', item.admissions_stats.data_quality_band],
        ['MCAT band', item.admissions_stats.published_mcat_band],
        ['GPA band', item.admissions_stats.published_gpa_band],
        ['AAMC grid rate', item.admissions_stats.aamc_acceptance_rate],
        ['AAMC rate band', item.admissions_stats.aamc_acceptance_rate_band],
        ['Confidence', item.admissions_stats.data_confidence],
      ])}
      ${detailPanel('Cost and Debt', [
        ['Cost data present', item.derived.cost_data_present],
        ['In-state tuition+fees+insurance', item.cost_and_debt.in_state_tuition_fees_insurance],
        ['Out-state tuition+fees+insurance', item.cost_and_debt.out_state_tuition_fees_insurance],
        ['Estimated COA in-state', item.cost_and_debt.estimated_coa_in_state],
        ['Estimated COA out-state', item.cost_and_debt.estimated_coa_out_state],
        ['Confidence', item.cost_and_debt.data_confidence],
      ])}
      ${detailPanel('Source Coverage', [
        ['Admissions policy rows', item.derived.admissions_policy_count],
        ['Letter requirement rows', item.derived.letter_requirement_count],
        ['Source review rows', item.derived.source_review_count],
      ])}
      ${detailPanel('Data Quality', [
        ['Warnings', item.derived.warning_count],
        ['Errors', item.derived.error_count],
        ['Next action', item.derived.suggested_next_action],
      ])}
    </div>
    <div class="panel" style="margin-top:12px">
      <h3>Issues</h3>
      ${table([
        {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
        {key:'file', label:'File', render:i=>i.file},
        {key:'field', label:'Field', render:i=>i.field},
        {key:'message', label:'Message', render:i=>i.message},
        {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
      ], item.data_quality, 'detailIssues')}
    </div>`;
}

function detailPanel(title, rows) {
  return `<div class="panel"><h3>${title}</h3>${rows.map(([k,v])=>`<p><strong>${k}:</strong> ${missing(v)}</p>`).join('')}</div>`;
}

function renderPartner() {
  const rows = filteredSchools();
  $('partner').innerHTML = `<h2>Partner Review</h2>` + table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'partner_input.could_live_here_4_years_score', label:'4 Years', render:s=>missing(s.partner_input.could_live_here_4_years_score)},
    {key:'partner_input.location_fit_score', label:'Location', render:s=>missing(s.partner_input.location_fit_score)},
    {key:'partner_input.culture_fit_score', label:'Culture', render:s=>missing(s.partner_input.culture_fit_score)},
    {key:'partner_input.regret_index_score', label:'Regret', render:s=>missing(s.partner_input.regret_index_score)},
    {key:'derived.hard_no_flag', label:'Hard No', render:s=>s.derived.hard_no_flag ? badge('Hard No', 'error') : ''},
    {key:'partner_input.partner_notes', label:'Notes', render:s=>missing(s.partner_input.partner_notes)},
  ], rows, 'partner');
}

function renderSources() {
  const current = filters.sources.sourceMissing;
  $('sources').innerHTML = `<h2>Admissions Sources</h2>
    <div class="filters"><label>Source URL <select id="sourceMissing"><option value="">All</option><option value="missing">Missing</option><option value="present">Present</option></select></label></div>
    <div id="sourceTable"></div>`;
  $('sourceMissing').value = current;
  $('sourceMissing').addEventListener('change', event => {
    filters.sources.sourceMissing = event.target.value;
    renderSourceTable();
  });
  renderSourceTable();
}

function renderSourceTable() {
  const rows = filteredSchools().filter(s => {
    const filter = filters.sources.sourceMissing;
    return !filter || (filter === 'missing' ? !s.admissions_source.candidate_source_url : !!s.admissions_source.candidate_source_url);
  });
  $('sourceTable').innerHTML = table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'admissions_source.candidate_source_url', label:'Candidate URL', render:s=>s.admissions_source.candidate_source_url ? `<a href="${s.admissions_source.candidate_source_url}" target="_blank">Open</a>` : 'Missing'},
    {key:'derived.source_queue_status', label:'Source Status', render:s=>s.derived.source_queue_status},
    {key:'derived.admissions_stats_present', label:'Stats', render:s=>s.derived.admissions_stats_present},
    {key:'admissions_source.notes', label:'Notes', render:s=>missing(s.admissions_source.notes)},
  ], rows, 'sources');
}

function renderQuality() {
  const severity = $('qualitySeverity')?.value || '';
  const rows = payload.data_quality_report.filter(i => !severity || i.severity === severity);
  $('quality').innerHTML = `<h2>Data Quality</h2>
    <div class="grid">${metric('Errors', errorCount())}${metric('Warnings', warningCount())}</div>
    <div class="filters"><label>Severity <select id="qualitySeverity"><option value="">All</option><option value="error">Error</option><option value="warning">Warning</option><option value="info">Info</option></select></label></div>
    <div id="qualityTable"></div>`;
  $('qualitySeverity').value = severity;
  $('qualitySeverity').addEventListener('change', renderQuality);
  $('qualityTable').innerHTML = table([
    {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
    {key:'file', label:'File', render:i=>i.file},
    {key:'row_id', label:'Row', render:i=>i.row_id},
    {key:'field', label:'Field', render:i=>i.field},
    {key:'message', label:'Message', render:i=>i.message},
    {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
  ], rows, 'quality');
}

function renderPlans() {
  $('plans').innerHTML = `<h2>Plans</h2>` + table([
    {key:'plan_name', label:'Plan', render:p=>p.plan_name},
    {key:'status', label:'Status', render:p=>badge(p.status)},
    {key:'priority', label:'Priority', render:p=>p.priority},
    {key:'phase', label:'Phase', render:p=>p.phase},
    {key:'current_decision_summary', label:'Decision', render:p=>p.current_decision_summary},
    {key:'next_action', label:'Next Action', render:p=>p.next_action},
    {key:'doc_path', label:'Doc', render:p=>p.doc_path},
  ], payload.project_subplans, 'plans');
}

function objectRows(obj) {
  return Object.entries(obj || {}).map(([key, value]) => ({key, value}));
}

function renderStatus() {
  const status = sourceStatus();
  const canonical = status.canonical_counts || {};
  const tuition = status.tuition || {};
  const mcat = status.mcat_gpa || {};
  const raw = status.raw_aamc_files || {};
  $('status').innerHTML = `<h2>Current Status</h2>
    ${renderStatusSummary()}
    <div class="detail-grid">
      ${detailPanel('Canonical Model Coverage', [
        ['School master rows', canonical.school_master_rows],
        ['Admissions stats rows', canonical.admissions_stats_rows],
        ['Cost and debt rows', canonical.cost_and_debt_rows],
        ['Admissions policy rows', canonical.admissions_policy_rows],
        ['Letter requirement rows', canonical.letter_requirement_rows],
        ['Source review rows', canonical.source_review_queue_rows],
        ['Open source reviews', canonical.open_source_review_rows],
        ['Median MCAT populated', canonical.school_master_median_mcat_populated],
        ['Median GPA populated', canonical.school_master_median_gpa_populated],
        ['In-state tuition populated', canonical.school_master_in_state_tuition_populated],
        ['Out-state tuition populated', canonical.school_master_out_state_tuition_populated],
        ['COA in-state populated', canonical.school_master_estimated_coa_in_state_populated],
        ['COA out-state populated', canonical.school_master_estimated_coa_out_state_populated],
      ])}
      ${detailPanel('AAMC Tuition Source', [
        ['Parsed rows', tuition.parsed_rows],
        ['Patch candidates', tuition.patch_candidates],
        ['Safe after gap review', tuition.safe_rows_after_gap_review],
        ['Ambiguous high-confidence', tuition.ambiguous_high_confidence_rows],
        ['Join review/no-match', tuition.join_review_or_no_match_rows],
        ['MD not safe yet', tuition.md_rows_not_safe_yet],
        ['DO missing tuition', tuition.do_rows_missing_tuition],
      ])}
      ${detailPanel('Raw and Parsed Sources', [
        ['Source table CSVs', status.source_table_count],
        ['Source diff files', status.source_diff_file_count],
        ['Raw AAMC files', raw.all],
        ['Raw AAMC PDFs', raw.pdf],
        ['Raw AAMC HTML', raw.html],
        ['Manual match overrides', status.manual_override_count],
      ])}
      ${detailPanel('GPA/MCAT Source Data', [
        ['Comparable rows', mcat.comparable_rows],
        ['Rows with GPA', mcat.rows_with_gpa],
        ['Rows with MCAT', mcat.rows_with_mcat],
        ['Comparison clusters', mcat.comparison_clusters],
        ['Conflict rows', mcat.conflict_rows],
      ])}
    </div>
    <div class="detail-grid" style="margin-top:12px">
      <div class="panel">
        <h3>GPA/MCAT Agreement</h3>
        ${table([
          {key:'key', label:'Label', render:r=>r.key},
          {key:'value', label:'Count', render:r=>r.value},
        ], objectRows(mcat.agreement_counts), 'statusAgreement')}
      </div>
      <div class="panel">
        <h3>GPA/MCAT Data Quality</h3>
        ${table([
          {key:'key', label:'Band', render:r=>r.key},
          {key:'value', label:'Rows', render:r=>r.value},
        ], objectRows(mcat.quality_counts), 'statusQuality')}
      </div>
      <div class="panel">
        <h3>GPA/MCAT Sources</h3>
        ${table([
          {key:'key', label:'Source', render:r=>r.key},
          {key:'value', label:'Rows', render:r=>r.value},
        ], objectRows(mcat.source_counts), 'statusSources')}
      </div>
    </div>
    <div class="panel" style="margin-top:12px">
      <h3>Phase 2A Plan Status</h3>
      ${table([
        {key:'plan_id', label:'Plan', render:p=>p.plan_name},
        {key:'status', label:'Status', render:p=>badge(p.status)},
        {key:'priority', label:'Priority', render:p=>p.priority},
        {key:'current_decision_summary', label:'Current Decision', render:p=>p.current_decision_summary},
        {key:'next_action', label:'Next Action', render:p=>p.next_action},
        {key:'doc_path', label:'Doc', render:p=>p.doc_path},
      ], status.source_plans || [], 'statusPlans')}
    </div>`;
}

function render() {
  $('summaryText').textContent = `${payload.meta.active_school_count} active schools · ${warningCount()} warnings · ${errorCount()} errors`;
  if (currentView === 'dashboard') renderDashboard();
  if (currentView === 'status') renderStatus();
  if (currentView === 'rankings') renderRankings();
  if (currentView === 'detail') renderDetail();
  if (currentView === 'partner') renderPartner();
  if (currentView === 'sources') renderSources();
  if (currentView === 'quality') renderQuality();
  if (currentView === 'plans') renderPlans();
  document.querySelectorAll('[data-school]').forEach(el => el.addEventListener('click', event => {
    event.preventDefault();
    openDetail(el.dataset.school);
  }));
}

document.querySelectorAll('.tabs button').forEach(btn => btn.addEventListener('click', () => setView(btn.dataset.view)));
$('globalSearch').addEventListener('input', render);
document.addEventListener('click', event => {
  const th = event.target.closest('th[data-key]');
  if (!th) return;
  const tableKey = th.dataset.table;
  const key = th.dataset.key;
  const prior = sortState[tableKey] || {};
  sortState[tableKey] = {key, dir: prior.key === key && prior.dir === 'asc' ? 'desc' : 'asc'};
  render();
});
render();
"""


def build_site() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_site_payload()
    write_site_json(payload)
    SITE_INDEX_HTML.write_text(render_site_html(payload), encoding="utf-8")
    return SITE_INDEX_HTML


def main() -> None:
    output = build_site()
    print(f"Wrote {output.relative_to(ROOT)}")
