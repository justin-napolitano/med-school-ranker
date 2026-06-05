from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
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
    PREFERENCES_CSV,
    RANKINGS_CSV,
    ROOT,
    SCENARIO_WEIGHTS_CSV,
    SCORE_CONTRIBUTIONS_CSV,
    SCORING_METHODOLOGY_CSV,
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
    "scoring_methodology": SCORING_METHODOLOGY_CSV,
    "score_contributions": SCORE_CONTRIBUTIONS_CSV,
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

SITE_MODE_LOCAL_FULL = "local_full"
SITE_MODE_PUBLISH_SAFE = "publish_safe"
SITE_MODES = {SITE_MODE_LOCAL_FULL, SITE_MODE_PUBLISH_SAFE}
DEFAULT_ROUTE = "#/rankings"

AAMC_GRID_CAVEAT = (
    "AAMC MCAT/GPA grid context is national aggregate data for U.S. MD-granting medical "
    "school applicants and acceptees; it is not a school-specific acceptance probability."
)

PUBLIC_ROUTES = [
    {"path": "#/rankings", "label": "Rankings", "route_type": "public"},
    {"path": "#/dossiers", "label": "Dossiers", "route_type": "public"},
    {"path": "#/research", "label": "Research Queue", "route_type": "public"},
    {"path": "#/lists", "label": "Curated Lists", "route_type": "public"},
    {"path": "#/compare", "label": "Compare", "route_type": "public"},
    {"path": "#/methodology", "label": "Methodology", "route_type": "public"},
    {"path": "#/sources", "label": "Sources", "route_type": "public"},
]

ADMIN_ROUTES = [
    {"path": "#/admin", "label": "Admin Overview", "route_type": "admin"},
    {"path": "#/admin/sources", "label": "Source Review", "route_type": "admin"},
    {"path": "#/admin/data-quality", "label": "Data Quality", "route_type": "admin"},
    {"path": "#/admin/build", "label": "Build Status", "route_type": "admin"},
]

PRODUCT_PUBLIC_JSON_KEYS = {
    "school_master",
    "calculated_rankings",
    "scoring_methodology",
    "score_contributions",
    "aamc_mcat_gpa_grid",
    "admissions_stats",
    "cost_and_debt",
    "admissions_policies",
    "letter_requirements",
}

PRODUCT_LOCAL_KEYS = {"applicant_profiles", "partner_inputs"}
ADMIN_LOCAL_KEYS = {
    "source_status",
    "source_match_overrides",
    "source_review_queue",
    "admissions_source_queue",
    "data_quality_report",
    "source_integration_report",
    "source_match_review",
    "admissions_stats_candidates",
    "admissions_stats_conflicts",
    "cost_and_debt_candidates",
    "cost_and_debt_review",
    "project_subplans",
}

PUBLIC_STRIPPED_FIELDS = {
    "hard_no_flag",
    "hard_no_reason",
    "source_snapshot_path",
    "source_table",
    "source_row_number",
    "source_table_row_number",
    "source_file",
    "raw_file",
    "local_file_path",
    "review_notes",
    "reviewed_by",
}

CURATED_LIST_DEFINITIONS = [
    {
        "list_id": "best_cities",
        "title": "Best Cities",
        "category": "location",
        "description": "Location-focused scaffold for schools in stronger city and setting contexts.",
        "route_enabled": "TRUE",
        "required_fields": ["city", "region", "city_fit_score"],
        "core_fields": ["region", "city_fit_score"],
        "scoring_profile_id": "city_fit",
        "default_apply_mode": "scoring_boost",
        "methodology_notes": "Requires sourced region, setting, and city-fit facts before strong claims.",
        "missing_data_behavior": "Label provisional until city and region facts are populated.",
    },
    {
        "list_id": "best_culture_fit",
        "title": "Best Culture Fit",
        "category": "culture",
        "description": "Culture-fit scaffold for future evidence-backed culture and fit scores.",
        "route_enabled": "TRUE",
        "required_fields": ["culture_fit_score", "culture_evidence_status"],
        "core_fields": ["culture_fit_score", "culture_evidence_status"],
        "scoring_profile_id": "culture_fit",
        "default_apply_mode": "scoring_boost",
        "methodology_notes": "Requires explicit culture evidence or reviewed fit scores.",
        "missing_data_behavior": "Label provisional until culture evidence exists.",
    },
    {
        "list_id": "best_public_schools",
        "title": "Best Public Schools",
        "category": "ownership",
        "description": "Public-school scaffold for future ownership-backed filtering and scoring.",
        "route_enabled": "TRUE",
        "required_fields": ["ownership_type"],
        "core_fields": ["ownership_type"],
        "scoring_profile_id": "public_value",
        "default_apply_mode": "filter_only",
        "methodology_notes": "Requires source-backed ownership type before public/private claims.",
        "missing_data_behavior": "Label provisional until ownership type is populated.",
    },
    {
        "list_id": "best_private_schools",
        "title": "Best Private Schools",
        "category": "ownership",
        "description": "Private-school scaffold for future ownership-backed filtering and scoring.",
        "route_enabled": "TRUE",
        "required_fields": ["ownership_type"],
        "core_fields": ["ownership_type"],
        "scoring_profile_id": "private_value",
        "default_apply_mode": "filter_only",
        "methodology_notes": "Requires source-backed ownership type before public/private claims.",
        "missing_data_behavior": "Label provisional until ownership type is populated.",
    },
    {
        "list_id": "best_low_cost",
        "title": "Best Low Cost",
        "category": "cost",
        "description": "Cost-focused list using available tuition and cost-of-attendance rows.",
        "route_enabled": "TRUE",
        "required_fields": [
            "in_state_tuition_fees_insurance",
            "out_state_tuition_fees_insurance",
            "estimated_coa_in_state",
            "estimated_coa_out_state",
        ],
        "core_fields": ["in_state_tuition_fees_insurance", "out_state_tuition_fees_insurance"],
        "scoring_profile_id": "low_cost",
        "default_apply_mode": "replace_scoring",
        "methodology_notes": "MD AAMC cost rows are partially available; DO tuition coverage is incomplete.",
        "missing_data_behavior": "Render with partial status and missing-cost caveats.",
    },
    {
        "list_id": "best_admissions_realism",
        "title": "Best Admissions Realism",
        "category": "admissions",
        "description": "Admissions-realism list using published MCAT/GPA stats where source-backed.",
        "route_enabled": "TRUE",
        "required_fields": [
            "published_mcat_average",
            "published_gpa_average",
            "aamc_acceptance_rate_band",
        ],
        "core_fields": ["published_mcat_average", "published_gpa_average"],
        "scoring_profile_id": "admissions_realism",
        "default_apply_mode": "scoring_boost",
        "methodology_notes": AAMC_GRID_CAVEAT,
        "missing_data_behavior": "Render with partial status and national-grid caveats.",
    },
    {
        "list_id": "best_partner_fit",
        "title": "Best Partner Fit",
        "category": "local_review",
        "description": "Local-only partner-fit scaffold for reviewed partner preferences.",
        "route_enabled": "TRUE",
        "required_fields": ["partner_fit_score", "partner_review_status"],
        "core_fields": ["partner_fit_score", "partner_review_status"],
        "scoring_profile_id": "partner_fit",
        "default_apply_mode": "scoring_boost",
        "methodology_notes": "Requires intentionally populated partner inputs before use.",
        "missing_data_behavior": "Label provisional until partner inputs are intentionally populated.",
    },
]

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


def grouped_weights(rows: list[dict[str, str]], group_field: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        group = row.get(group_field, "").strip()
        column = row.get("column_name", "").strip()
        weight = row.get("weight", "").strip()
        if group and column and weight:
            grouped[group].append({"column_name": column, "weight": weight})
    return dict(grouped)


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


def validate_site_mode(site_mode: str) -> str:
    if site_mode not in SITE_MODES:
        raise ValueError(f"Unsupported site mode '{site_mode}'. Expected one of: {', '.join(sorted(SITE_MODES))}.")
    return site_mode


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return slug or fallback


def unique_slug(base: str, used_slugs: set[str]) -> str:
    slug = base
    suffix = 2
    while slug in used_slugs:
        slug = f"{base}-{suffix}"
        suffix += 1
    used_slugs.add(slug)
    return slug


def school_slug_for(row: dict[str, str], used_slugs: set[str]) -> str:
    existing = row.get("school_slug", "").strip() or row.get("profile_slug", "").strip()
    base = slugify(existing or row.get("school_name") or row.get("school_id"), row.get("school_id", "school"))
    return unique_slug(base, used_slugs)


def list_slug_for(row: dict[str, object], used_slugs: set[str]) -> str:
    existing = str(row.get("slug", "") or "").strip()
    base = slugify(existing or str(row.get("title", "") or row.get("list_id", "")), str(row.get("list_id", "list")))
    return unique_slug(base, used_slugs)


def public_row(row: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in row.items() if key not in PUBLIC_STRIPPED_FIELDS}


def payload_groups(site_mode: str) -> dict[str, list[str]]:
    groups = {
        "product_public": [
            "meta",
            "routes",
            "copy",
            "schools",
            "school_profiles",
            "school_master",
            "calculated_rankings",
            "scoring_methodology",
            "score_contributions",
            "curated_lists",
            "aamc_mcat_gpa_grid",
            "admissions_stats",
            "cost_and_debt",
            "admissions_policies",
            "letter_requirements",
            "public_sources",
        ],
        "product_local": sorted(PRODUCT_LOCAL_KEYS),
        "admin_local": sorted(ADMIN_LOCAL_KEYS),
    }
    if site_mode == SITE_MODE_PUBLISH_SAFE:
        return {"product_public": groups["product_public"], "product_local": [], "admin_local": []}
    return groups


def field_counts_by_school(
    school_master: list[dict[str, str]],
    rankings: list[dict[str, str]],
    admissions_stats: list[dict[str, str]],
    cost_and_debt: list[dict[str, str]],
    partner_inputs: list[dict[str, str]],
) -> dict[str, int]:
    counts: dict[str, set[str]] = defaultdict(set)
    row_groups = [school_master, rankings, admissions_stats, cost_and_debt, partner_inputs]
    for rows in row_groups:
        for row in rows:
            school_id = row.get("school_id", "").strip()
            if not school_id:
                continue
            for field, value in row.items():
                if str(value or "").strip():
                    counts[field].add(school_id)
    return {field: len(school_ids) for field, school_ids in counts.items()}


def curated_list_readiness(
    definition: dict[str, object],
    field_counts: dict[str, int],
    active_school_count: int,
) -> dict[str, object]:
    required_fields = [str(field) for field in definition["required_fields"]]
    core_fields = [str(field) for field in definition.get("core_fields", required_fields)]
    available_fields = [field for field in required_fields if field_counts.get(field, 0) > 0]
    missing_fields = [field for field in required_fields if field not in available_fields]
    core_missing = [field for field in core_fields if field not in available_fields]
    coverage_by_field = {
        field: {
            "populated_school_count": field_counts.get(field, 0),
            "active_school_count": active_school_count,
        }
        for field in required_fields
    }
    coverage_ratio = (
        min((field_counts.get(field, 0) / active_school_count for field in required_fields), default=0)
        if active_school_count
        else 0
    )
    if core_missing:
        readiness_label = "provisional"
    elif missing_fields or coverage_ratio < 0.95:
        readiness_label = "partial"
    else:
        readiness_label = "ready"
    confidence_label = {
        "ready": "source-backed",
        "partial": "partial coverage",
        "provisional": "provisional",
    }[readiness_label]
    return {
        "required_fields": required_fields,
        "available_fields": available_fields,
        "missing_fields": missing_fields,
        "core_missing_fields": core_missing,
        "coverage_by_field": coverage_by_field,
        "readiness_label": readiness_label,
        "confidence_label": confidence_label,
    }


def build_curated_lists(
    school_master: list[dict[str, str]],
    rankings: list[dict[str, str]],
    admissions_stats: list[dict[str, str]],
    cost_and_debt: list[dict[str, str]],
    partner_inputs: list[dict[str, str]],
) -> list[dict[str, object]]:
    field_counts = field_counts_by_school(school_master, rankings, admissions_stats, cost_and_debt, partner_inputs)
    used_slugs: set[str] = set()
    active_school_count = len(school_master)
    curated_lists = []
    for definition in CURATED_LIST_DEFINITIONS:
        row = dict(definition)
        row["slug"] = list_slug_for(row, used_slugs)
        row["route"] = f"#/lists/{row['slug']}"
        row.update(curated_list_readiness(row, field_counts, active_school_count))
        curated_lists.append(row)
    return curated_lists


def public_source_summary(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    sources: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        name = row.get("source_name", "").strip()
        url = row.get("source_url", "").strip()
        if not name and not url:
            continue
        key = (name, url)
        sources.setdefault(
            key,
            {
                "source_name": name or "Source",
                "source_url": url,
                "row_count": "0",
            },
        )
        sources[key]["row_count"] = str(int(sources[key]["row_count"]) + 1)
    return sorted(sources.values(), key=lambda row: (row["source_name"], row["source_url"]))


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


def build_site_payload(site_mode: str = SITE_MODE_LOCAL_FULL) -> dict[str, object]:
    site_mode = validate_site_mode(site_mode)
    publish_safe = site_mode == SITE_MODE_PUBLISH_SAFE
    school_master_raw = read_csv(MASTER_CSV)
    rankings = read_csv(RANKINGS_CSV)
    scoring_methodology = read_csv(SCORING_METHODOLOGY_CSV)
    score_contributions = read_csv(SCORE_CONTRIBUTIONS_CSV)
    preference_weights = read_csv(PREFERENCES_CSV)
    scenario_weights = read_csv(SCENARIO_WEIGHTS_CSV)
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

    used_school_slugs: set[str] = set()
    school_slugs_by_id: dict[str, str] = {}
    school_master = []
    for row in school_master_raw:
        school = dict(row)
        school_id = school.get("school_id", "").strip()
        school_slug = school_slug_for(school, used_school_slugs)
        school["school_slug"] = school_slug
        school["profile_route"] = f"#/schools/{school_slug}"
        if school_id:
            school_slugs_by_id[school_id] = school_slug
        school_master.append(school)

    def with_school_route(rows: list[dict[str, str]]) -> list[dict[str, str]]:
        routed_rows = []
        for row in rows:
            routed = dict(row)
            school_id = routed.get("school_id", "").strip()
            school_slug = school_slugs_by_id.get(school_id, "")
            if school_slug:
                routed["school_slug"] = school_slug
                routed["profile_route"] = f"#/schools/{school_slug}"
            routed_rows.append(routed)
        return routed_rows

    rankings = with_school_route(rankings)
    admissions_stats = with_school_route(admissions_stats)
    cost_and_debt = with_school_route(cost_and_debt)
    admissions_policies = with_school_route(admissions_policies)
    letter_requirements = with_school_route(letter_requirements)
    partner_inputs = with_school_route(partner_inputs)
    source_match_overrides = with_school_route(source_match_overrides)
    source_review_queue = with_school_route(source_review_queue)
    source_queue = with_school_route(source_queue)
    data_quality = with_school_route(data_quality)

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
        school_slug = school.get("school_slug", "")
        ranking_row = rankings_by_school.get(school_id, {})
        derived = {
            "admissions_stats_present": "yes" if has_admissions_stats(stats_row) else "no",
            "admissions_fit_tier": ranking_row.get("admissions_fit_tier", "").strip() or ranking_row.get("dynamic_tier", "").strip() or "missing",
            "application_bucket": ranking_row.get("application_bucket", "").strip() or ranking_row.get("suggested_funnel_bucket", "").strip() or "missing",
            "admissions_data_quality_band": ranking_row.get("stats_data_quality_band", "").strip() or stats_row.get("data_quality_band", "").strip() or "missing",
            "published_mcat_band": ranking_row.get("published_mcat_band", "").strip() or stats_row.get("published_mcat_band", "").strip() or "missing",
            "published_gpa_band": ranking_row.get("published_gpa_band", "").strip() or stats_row.get("published_gpa_band", "").strip() or "missing",
            "aamc_acceptance_rate_band": stats_row.get("aamc_acceptance_rate_band", "").strip() or "missing",
            "cost_basis_present": "yes" if ranking_row.get("cost_basis", "").strip() else "no",
            "cost_data_present": "yes" if cost_row else "no",
            "missing_score_status": "missing" if ranking_row.get("missing_score_inputs", "").strip() else "complete",
            "score_warning_status": "warning" if ranking_row.get("score_warnings", "").strip() else "clear",
            "rank_confidence": ranking_row.get("rank_confidence", "").strip() or "missing",
            "rank_band": ranking_row.get("rank_band", "").strip() or "missing",
            "admissions_policy_count": len(policy_rows),
            "letter_requirement_count": len(letter_rows),
        }
        if not publish_safe:
            derived.update(
                {
                    "warning_count": warning_count,
                    "error_count": error_count,
                    "partner_input_status": "present" if has_partner_input(partner_row) else "missing",
                    "partner_notes_indicator": "yes" if partner_row.get("partner_notes", "").strip() else "no",
                    "hard_no_flag": is_truthy(partner_row.get("hard_no_flag")) or is_truthy(ranking_row.get("hard_no_flag")),
                    "excluded_from_rank": is_truthy(ranking_row.get("excluded_from_rank")),
                    "source_review_count": len(review_rows),
                    "source_queue_status": source_row.get("source_status", "").strip() or "not_started",
                    "suggested_next_action": suggested_next_action(
                        partner_row,
                        source_row,
                        warning_count,
                        error_count,
                    ),
                }
            )
        item = {
            "school_slug": school_slug,
            "profile_route": f"#/schools/{school_slug}",
            "school": public_row(school) if publish_safe else school,
            "ranking": public_row(ranking_row) if publish_safe else ranking_row,
            "admissions_stats": public_row(stats_row) if publish_safe else stats_row,
            "cost_and_debt": public_row(cost_row) if publish_safe else cost_row,
            "admissions_policies": [public_row(row) for row in policy_rows] if publish_safe else policy_rows,
            "letter_requirements": [public_row(row) for row in letter_rows] if publish_safe else letter_rows,
            "derived": derived,
        }
        if not publish_safe:
            item.update(
                {
                    "partner_input": partner_row,
                    "admissions_source": source_row,
                    "source_review_queue": review_rows,
                    "data_quality": issues_by_school.get(school_id, []),
                }
            )
        schools.append(item)

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
    curated_lists = build_curated_lists(
        school_master,
        rankings,
        admissions_stats,
        cost_and_debt,
        partner_inputs if not publish_safe else [],
    )
    school_profiles = [
        {
            "school_id": school.get("school_id", ""),
            "school_slug": school.get("school_slug", ""),
            "route": school.get("profile_route", ""),
            "school_name": school.get("school_name", ""),
            "degree_type": school.get("degree_type", ""),
            "city": school.get("city", ""),
            "state": school.get("state", ""),
        }
        for school in school_master
    ]
    public_sources = public_source_summary(
        list(school_master)
        + list(aamc_mcat_gpa_grid)
        + list(admissions_stats)
        + list(cost_and_debt)
        + list(admissions_policies)
        + list(letter_requirements)
    )
    groups = payload_groups(site_mode)
    payload: dict[str, object] = {
        "meta": {
            "site_mode": site_mode,
            "site_privacy_mode": site_mode,
            "active_school_count": len(school_master),
            "degree_counts": dict(sorted(degree_counts.items())),
            "generated_at": status["generated_at"],
            "default_route": DEFAULT_ROUTE,
            "payload_groups": groups,
        },
        "routes": {
            "default": DEFAULT_ROUTE,
            "public": PUBLIC_ROUTES,
            "admin": ADMIN_ROUTES if site_mode == SITE_MODE_LOCAL_FULL else [],
            "school_profile_pattern": "#/schools/:school_slug",
            "curated_list_pattern": "#/lists/:list_slug",
        },
        "copy": {
            "aamc_grid_caveat": AAMC_GRID_CAVEAT,
            "curated_list_readiness": {
                "ready": "Required fields are populated at high coverage and can support source-backed list claims.",
                "partial": "Some required fields are present, but coverage gaps require visible caveats.",
                "provisional": "Core fields are missing; the list is a scaffold and should not make strong claims.",
            },
        },
        "schools": schools,
        "school_profiles": school_profiles,
        "school_master": [public_row(row) for row in school_master] if publish_safe else school_master,
        "calculated_rankings": [public_row(row) for row in rankings] if publish_safe else rankings,
        "scoring_methodology": [public_row(row) for row in scoring_methodology] if publish_safe else scoring_methodology,
        "score_contributions": [public_row(row) for row in score_contributions] if publish_safe else score_contributions,
        "scoring_config": {
            "weight_basis": "present_components_only",
            "preference_weights_by_group": grouped_weights(preference_weights, "score_group"),
            "scenario_weights_by_scenario": grouped_weights(scenario_weights, "scenario"),
        },
        "curated_lists": curated_lists,
        "aamc_mcat_gpa_grid": [public_row(row) for row in aamc_mcat_gpa_grid] if publish_safe else aamc_mcat_gpa_grid,
        "admissions_stats": [public_row(row) for row in admissions_stats] if publish_safe else admissions_stats,
        "cost_and_debt": [public_row(row) for row in cost_and_debt] if publish_safe else cost_and_debt,
        "admissions_policies": [public_row(row) for row in admissions_policies] if publish_safe else admissions_policies,
        "letter_requirements": [public_row(row) for row in letter_requirements] if publish_safe else letter_requirements,
        "public_sources": public_sources,
    }
    if site_mode == SITE_MODE_LOCAL_FULL:
        payload.update(
            {
                "source_status": status,
                "applicant_profiles": applicant_profiles,
                "partner_inputs": partner_inputs,
                "source_match_overrides": source_match_overrides,
                "source_review_queue": source_review_queue,
                "admissions_source_queue": source_queue,
                "data_quality_report": data_quality,
                "project_subplans": project_subplans,
            }
        )
    return payload


def write_site_json(payload: dict[str, object], site_mode: str) -> None:
    data_dir = SITE_DIR / "data"
    json_keys = set(PRODUCT_PUBLIC_JSON_KEYS)
    if site_mode == SITE_MODE_LOCAL_FULL:
        json_keys.update(JSON_OUTPUTS)
        json_keys.add("source_status")
    for key in sorted(json_keys):
        if key in payload:
            write_json(data_dir / f"{key}.json", payload[key])
        elif key in JSON_OUTPUTS:
            write_json(data_dir / f"{key}.json", read_csv(JSON_OUTPUTS[key]))
    write_json(data_dir / "curated_lists.json", payload["curated_lists"])
    write_json(data_dir / "school_profiles.json", payload["school_profiles"])
    write_json(data_dir / "public_sources.json", payload["public_sources"])
    write_json(data_dir / "site_payload.json", payload)


def render_site_html(payload: dict[str, object]) -> str:
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    escaped_payload = html.escape(payload_json, quote=False)
    public_nav = "\n    ".join(
        f'<a data-route="{route["path"]}" href="{route["path"]}">{html.escape(route["label"])}</a>'
        for route in payload["routes"]["public"]  # type: ignore[index]
    )
    admin_nav = ""
    if payload["routes"]["admin"]:  # type: ignore[index]
        admin_nav = '\n    <a data-route="#/admin" href="#/admin" class="admin-link">Admin</a>'
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
      <p id="summaryText">Applicant-facing rankings and school profiles</p>
    </div>
    <label class="search-label">Search
      <input id="globalSearch" type="search" placeholder="School, city, state">
    </label>
  </header>
  <nav class="tabs" aria-label="Primary routes">
    {public_nav}{admin_nav}
  </nav>
  <main>
    <section id="rankings" class="view"></section>
    <section id="dossiers" class="view"></section>
    <section id="research" class="view"></section>
    <section id="lists" class="view"></section>
    <section id="listDetail" class="view"></section>
    <section id="compare" class="view"></section>
    <section id="profile" class="view"></section>
    <section id="methodology" class="view"></section>
    <section id="sources" class="view"></section>
    <section id="admin" class="view"></section>
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
input, select, textarea {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  font: inherit;
  background: #fff;
}
textarea { min-height: 120px; resize: vertical; width: 100%; }
.tabs {
  display: flex;
  gap: 6px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: #eaf0f6;
  overflow-x: auto;
}
.tabs a, button {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  background: #fff;
  color: #203347;
  cursor: pointer;
  white-space: nowrap;
  text-decoration: none;
}
.tabs a.active, button.active { background: var(--accent); border-color: var(--accent); color: #fff; }
button:disabled { color: var(--muted); background: #eef3f7; cursor: not-allowed; }
button.secondary { background: #f7fafc; }
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
.selector-panel { margin: 0 0 14px; }
.selector-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 10px; }
.field-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 10px; }
.field-grid label { display: grid; gap: 4px; color: var(--muted); font-size: 12px; }
.full-span { grid-column: 1 / -1; }
.inline-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.table-wrap { overflow: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); }
table { width: 100%; border-collapse: collapse; min-width: 1100px; }
#rankTable table { min-width: 2100px; }
#mdSelectorTable table { min-width: 1300px; }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; font-size: 13px; }
th { position: sticky; top: 0; background: #eef4f8; color: var(--header); cursor: pointer; z-index: 1; }
tr:hover td { background: #f8fbfd; }
.badge { display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; border: 1px solid var(--border); background: #f7fafc; }
.badge.warn { color: var(--warn); border-color: #e6c773; background: #fff8df; }
.badge.error { color: var(--error); border-color: #e7aaaa; background: #fff0f0; }
.badge.good { color: #17623a; border-color: #a9d6bb; background: #eefaf2; }
.badge.provisional { color: var(--warn); border-color: #e6c773; background: #fff8df; }
.badge.partial { color: #7b5a00; border-color: #d8bf72; background: #fff9e8; }
.badge.ready { color: #17623a; border-color: #a9d6bb; background: #eefaf2; }
.muted { color: var(--muted); }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr)); gap: 12px; }
.panel p { overflow-wrap: anywhere; line-height: 1.25; }
.empty-state { border: 1px dashed var(--border); border-radius: 8px; padding: 12px; color: var(--muted); background: #f8fbfd; }
.route-tools { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 12px; }
.route-tools a { color: var(--accent); }
.caveat { border-left: 4px solid #d8bf72; background: #fff9e8; padding: 10px 12px; margin: 10px 0 12px; color: #4d4125; }
a { color: var(--accent); }
@media (max-width: 760px) {
  .app-header { display: grid; align-items: stretch; }
  .search-label { min-width: 0; }
  main { padding: 12px; }
}
"""


JS = r"""
const payload = JSON.parse(document.getElementById('site-data').textContent);
const DEFAULT_ROUTE = payload.routes?.default || '#/rankings';
const ADMIN_ENABLED = (payload.routes?.admin || []).length > 0;
let currentRoute = {view: 'rankings', path: '/rankings'};
let sortState = {};
let filters = {
  rankings: {degree: '', state: '', tier: '', bucket: '', visibility: 'visible', hardNo: '', excluded: '', warnings: '', partner: '', quality: '', mcatBand: '', gpaBand: '', aamcRateBand: '', missingScore: '', scoreWarning: ''},
  dossiers: {visibility: 'visible', status: '', missing: '', tier: '', rankBand: ''},
  research: {visibility: 'visible', status: '', tier: '', rankBand: '', action: ''},
  sources: {sourceMissing: ''},
  quality: {severity: ''},
};
let selectorState = {
  mcatBand: '',
  gpaBand: '',
  applicantState: '',
};
let visibilityState = {};
let dossierState = {};

const VISIBILITY_EXPORT_HEADERS = ['export_schema_version', 'exported_at', 'school_id', 'school_name', 'visibility_state', 'visibility_reason', 'hidden_at', 'updated_at', 'source', 'notes'];
const DOSSIER_EXPORT_HEADERS = ['export_schema_version', 'exported_at', 'school_id', 'school_name', 'research_status', 'interest_level', 'four_year_happiness', 'location_fit', 'culture_fit', 'regret_index', 'hard_no_flag', 'hard_no_reason', 'application_decision_status', 'notes'];
const DOSSIER_FIELDS = DOSSIER_EXPORT_HEADERS.filter(field => !['export_schema_version', 'exported_at', 'school_id', 'school_name'].includes(field));
const RESEARCH_STATUSES = ['not_started', 'skimmed', 'needs_deep_research', 'researched', 'ready_to_decide', 'excluded', 'applied'];
const INTEREST_LEVELS = ['high', 'medium', 'low', 'none'];
const DECISION_STATUSES = ['considering', 'applying', 'applied', 'interview', 'accepted', 'waitlisted', 'rejected', 'withdrawn', 'not_applying'];

const $ = (id) => document.getElementById(id);
const rows = (key) => Array.isArray(payload[key]) ? payload[key] : [];
const missing = (value) => value === undefined || value === null || value === '' ? 'Missing' : value;
const truthy = (value) => ['1', 'true', 't', 'yes', 'y'].includes(String(value || '').trim().toLowerCase());
const parseScore = (value) => {
  const text = String(value ?? '').replace(/[$,%]/g, '').replace(/,/g, '').trim();
  if (!text) return null;
  const number = Number(text);
  return Number.isFinite(number) ? number : null;
};
const clamp = (value, lower=1, upper=10) => Math.max(lower, Math.min(upper, value));
const routeHash = (path) => path.startsWith('#') ? path : `#${path}`;
const routePath = (hash) => {
  const cleaned = String(hash || '').replace(/^#/, '') || '/rankings';
  return cleaned === '/' ? '/rankings' : cleaned;
};
const schoolText = (item) => [
  item.school.school_name,
  item.school.city,
  item.school.state,
  item.school.degree_type,
].join(' ').toLowerCase();

function filteredSchools() {
  const query = $('globalSearch').value.trim().toLowerCase();
  return rows('schools').filter(item => !query || schoolText(item).includes(query));
}

function parseRoute() {
  const path = routePath(window.location.hash);
  if (path.startsWith('/admin') && !ADMIN_ENABLED) return {view: 'rankings', path: '/rankings'};
  if (path === '/rankings') return {view: 'rankings', path};
  if (path === '/dossiers') return {view: 'dossiers', path};
  if (path === '/research') return {view: 'research', path};
  if (path === '/lists') return {view: 'lists', path};
  if (path.startsWith('/lists/')) return {view: 'listDetail', path, slug: path.split('/')[2] || ''};
  if (path === '/compare') return {view: 'compare', path};
  if (path.startsWith('/schools/')) return {view: 'profile', path, slug: path.split('/')[2] || ''};
  if (path === '/methodology') return {view: 'methodology', path};
  if (path === '/sources') return {view: 'sources', path};
  if (path.startsWith('/admin')) return {view: 'admin', path};
  return {view: 'rankings', path: '/rankings'};
}

function ensureDefaultRoute() {
  if (!window.location.hash || window.location.hash === '#' || window.location.hash === '#/') {
    window.location.replace(DEFAULT_ROUTE);
    return true;
  }
  return false;
}

function setActiveSection(view) {
  document.querySelectorAll('.view').forEach(section => section.classList.toggle('active', section.id === view));
}

function setActiveNav(path) {
  document.querySelectorAll('.tabs a').forEach(link => {
    const navPath = routePath(link.dataset.route);
    const active = navPath === path
      || (path.startsWith('/lists/') && navPath === '/lists')
      || (path.startsWith('/schools/') && navPath === '/dossiers')
      || (path.startsWith('/admin') && navPath === '/admin');
    link.classList.toggle('active', active);
  });
}

function metric(label, value) {
  return `<div class="metric"><span class="muted">${label}</span><strong>${value}</strong></div>`;
}

function badge(text, type='') {
  return `<span class="badge ${type}">${missing(text)}</span>`;
}

function table(headers, tableRows, key) {
  const head = headers.map(h => `<th data-key="${h.key}" data-table="${key}">${h.label}</th>`).join('');
  const body = tableRows.map(row => `<tr>${headers.map(h => `<td>${h.render(row)}</td>`).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${headers.length}">No rows</td></tr>`}</tbody></table></div>`;
}

function optionTags(values, selected) {
  return values.map(value => `<option value="${value}" ${value === selected ? 'selected' : ''}>${value}</option>`).join('');
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function safeText(value) {
  return String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function attr(value) {
  return safeText(value).replace(/"/g, '&quot;');
}

function labelize(value) {
  const text = String(value || '').trim();
  if (!text) return 'Unselected';
  return text.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function nowIso() {
  return new Date().toISOString();
}

function schoolId(item) {
  return item.school?.school_id || item.ranking?.school_id || '';
}

function schoolById(id) {
  return rows('schools').find(item => schoolId(item) === id);
}

function visibilityFor(item) {
  const id = schoolId(item);
  return visibilityState[id] || {
    school_id: id,
    school_name: item.school?.school_name || '',
    visibility_state: 'visible',
    visibility_reason: '',
    hidden_at: '',
    updated_at: '',
    source: 'browser_session',
    notes: '',
  };
}

function isSchoolHidden(item) {
  return visibilityFor(item).visibility_state === 'hidden';
}

function visibilityBadge(item) {
  return isSchoolHidden(item) ? badge('Hidden', 'warn') : badge('Visible', 'good');
}

function setSchoolVisibility(id, visibilityStateValue, reason='') {
  const item = schoolById(id);
  if (!item) return;
  if (visibilityStateValue === 'visible') {
    delete visibilityState[id];
    return;
  }
  const previous = visibilityState[id] || {};
  const timestamp = nowIso();
  visibilityState[id] = {
    export_schema_version: 'school_visibility_v1',
    school_id: id,
    school_name: item.school.school_name || previous.school_name || '',
    visibility_state: visibilityStateValue,
    visibility_reason: reason || previous.visibility_reason || 'Not a current fit',
    hidden_at: previous.hidden_at || timestamp,
    updated_at: timestamp,
    source: 'browser_session',
    notes: previous.notes || '',
  };
}

function updateVisibilityReason(id, value) {
  const item = schoolById(id);
  if (!item) return;
  if (!visibilityState[id]) setSchoolVisibility(id, 'hidden', value);
  visibilityState[id].visibility_reason = value;
  visibilityState[id].updated_at = nowIso();
}

function hiddenSchools() {
  return rows('schools').filter(item => isSchoolHidden(item));
}

function visibilityExportRecords() {
  const exportedAt = nowIso();
  return Object.values(visibilityState)
    .filter(record => record.visibility_state !== 'visible')
    .sort((a, b) => String(a.school_name).localeCompare(String(b.school_name)))
    .map(record => ({
      export_schema_version: 'school_visibility_v1',
      exported_at: exportedAt,
      school_id: record.school_id,
      school_name: record.school_name,
      visibility_state: record.visibility_state,
      visibility_reason: record.visibility_reason,
      hidden_at: record.hidden_at,
      updated_at: record.updated_at,
      source: record.source || 'browser_session',
      notes: record.notes || '',
    }));
}

function downloadVisibilityExport() {
  downloadCsv('school_visibility_export.csv', VISIBILITY_EXPORT_HEADERS, visibilityExportRecords());
}

function dossierFor(item) {
  const id = schoolId(item);
  return dossierState[id] || {};
}

function ensureDossierRecord(id) {
  const item = schoolById(id);
  if (!item) return null;
  if (!dossierState[id]) {
    dossierState[id] = {
      school_id: id,
      school_name: item.school.school_name || '',
      research_status: '',
      interest_level: '',
      four_year_happiness: '',
      location_fit: '',
      culture_fit: '',
      regret_index: '',
      hard_no_flag: '',
      hard_no_reason: '',
      application_decision_status: '',
      notes: '',
    };
  }
  return dossierState[id];
}

function updateDossierField(id, field, value) {
  if (!DOSSIER_FIELDS.includes(field)) return;
  const record = ensureDossierRecord(id);
  if (!record) return;
  record[field] = value;
}

function hasDossierEdits(record) {
  return DOSSIER_FIELDS.some(field => String(record[field] || '').trim());
}

function dossierExportRecords() {
  const exportedAt = nowIso();
  return Object.values(dossierState)
    .filter(hasDossierEdits)
    .sort((a, b) => String(a.school_name).localeCompare(String(b.school_name)))
    .map(record => ({
      export_schema_version: 'school_dossier_edits_v1',
      exported_at: exportedAt,
      school_id: record.school_id,
      school_name: record.school_name,
      research_status: record.research_status || '',
      interest_level: record.interest_level || '',
      four_year_happiness: record.four_year_happiness || '',
      location_fit: record.location_fit || '',
      culture_fit: record.culture_fit || '',
      regret_index: record.regret_index || '',
      hard_no_flag: record.hard_no_flag || '',
      hard_no_reason: record.hard_no_reason || '',
      application_decision_status: record.application_decision_status || '',
      notes: record.notes || '',
    }));
}

function downloadDossierExport() {
  downloadCsv('school_dossier_edits_export.csv', DOSSIER_EXPORT_HEADERS, dossierExportRecords());
}

function missingDossierSections(item) {
  const missingSections = [];
  const dossier = dossierFor(item);
  if (!(item.ranking?.published_mcat_average || item.admissions_stats?.published_mcat_average)) missingSections.push('MCAT avg');
  if (!(item.ranking?.published_gpa_average || item.admissions_stats?.published_gpa_average)) missingSections.push('GPA avg');
  if (!(item.cost_and_debt?.estimated_coa_out_state || item.cost_and_debt?.out_state_tuition_fees_insurance || item.ranking?.cost_basis)) missingSections.push('cost');
  if (!Number(item.derived?.admissions_policy_count || 0)) missingSections.push('admissions policy');
  if (!Number(item.derived?.letter_requirement_count || 0)) missingSections.push('letters');
  if (!dossier.research_status) missingSections.push('research status');
  if (!dossier.notes) missingSections.push('notes');
  return missingSections;
}

function researchStatusFor(item) {
  return dossierFor(item).research_status || 'not_started';
}

function nextResearchAction(item) {
  const dossier = dossierFor(item);
  const missingSections = missingDossierSections(item);
  if (isSchoolHidden(item)) return 'Review hidden status';
  if (!dossier.research_status) return 'Start dossier';
  if (!dossier.four_year_happiness) return 'Score four-year fit';
  if (!dossier.interest_level) return 'Set interest level';
  if (missingSections.length) return `Fill ${missingSections[0]}`;
  if (!dossier.application_decision_status) return 'Set decision status';
  return 'Ready for shortlist review';
}

function bandMidpoint(label, kind) {
  const text = String(label || '').trim();
  if (!text) return null;
  if (text.startsWith('Greater than')) {
    const value = parseScore(text.replace('Greater than', ''));
    if (value === null) return null;
    return kind === 'gpa' ? Math.min(4, value + 0.10) : value + 2;
  }
  if (text.startsWith('Less than')) {
    const value = parseScore(text.replace('Less than', ''));
    if (value === null) return null;
    return kind === 'gpa' ? Math.max(0, value - 0.05) : value - 1;
  }
  const parts = text.split('-').map(part => parseScore(part));
  if (parts.length === 2 && parts[0] !== null && parts[1] !== null) {
    return (parts[0] + parts[1]) / 2;
  }
  return null;
}

function configuredWeights(group) {
  return payload.scoring_config?.preference_weights_by_group?.[group] || [];
}

function scoreValue(item, column, overrides={}) {
  if (Object.prototype.hasOwnProperty.call(overrides, column)) return overrides[column];
  const rankingValue = parseScore(item.ranking?.[column]);
  if (rankingValue !== null) return rankingValue;
  const schoolValue = parseScore(item.school?.[column]);
  if (schoolValue !== null) return schoolValue;
  return null;
}

function weightedAverage(item, group, overrides={}) {
  const weights = configuredWeights(group);
  let numerator = 0;
  let denominator = 0;
  let possible = 0;
  weights.forEach(({column_name, weight}) => {
    const numericWeight = parseScore(weight) || 0;
    possible += numericWeight;
    const value = scoreValue(item, column_name, overrides);
    if (value === null) return;
    numerator += value * numericWeight;
    denominator += numericWeight;
  });
  if (!denominator) return {score: null, coverage: 0};
  return {score: numerator / denominator, coverage: possible ? denominator / possible : 0};
}

function schoolState(item) {
  return item.school.state_abbrev || item.ranking.state_abbrev || '';
}

function selectorCostBasis(item) {
  const cost = item.cost_and_debt || {};
  const sameState = selectorState.applicantState && selectorState.applicantState === schoolState(item);
  const fields = sameState
    ? ['estimated_coa_in_state', 'in_state_tuition_fees_insurance', 'estimated_coa_out_state', 'out_state_tuition_fees_insurance']
    : ['estimated_coa_out_state', 'out_state_tuition_fees_insurance'];
  for (const field of fields) {
    const value = parseScore(cost[field]);
    if (value !== null) return value;
  }
  return null;
}

function selectorReady() {
  return Boolean(selectorState.mcatBand && selectorState.gpaBand && selectorState.applicantState);
}

function selectorOosScore(item) {
  if (!selectorState.applicantState) return null;
  if (selectorState.applicantState === schoolState(item)) return 10;
  if (truthy(item.school.accepts_oos)) return 6;
  const policyText = (item.admissions_policies || [])
    .filter(row => row.policy_field === 'out_of_state_applicants')
    .map(row => row.policy_value || '')
    .join(' ')
    .toLowerCase();
  if (policyText.includes('does not accept') || policyText.includes('not accepted') || policyText.includes('not considered') || policyText.includes('only in-state')) return 1;
  if (policyText.trim()) return 6;
  return 4;
}

function activeMdSchools() {
  return filteredSchools().filter(item => (
    item.school.degree_type === 'MD'
    && !truthy(item.school.manual_exclusion_flag)
    && !truthy(item.ranking.excluded_from_rank)
    && !isSchoolHidden(item)
  ));
}

function selectorRankedRows() {
  const mdRows = activeMdSchools();
  const mcatValue = bandMidpoint(selectorState.mcatBand, 'mcat');
  const gpaValue = bandMidpoint(selectorState.gpaBand, 'gpa');
  const costBasisBySchool = new Map(mdRows.map(item => [item.school.school_id, selectorCostBasis(item)]));
  const costValues = [...costBasisBySchool.values()].filter(value => value !== null).sort((a, b) => a - b);
  const minCost = costValues.length ? costValues[0] : null;
  const maxCost = costValues.length ? costValues[costValues.length - 1] : null;
  const computed = mdRows.map(item => {
    const schoolMcat = parseScore(item.ranking.school_mcat_for_fit || item.ranking.published_mcat_average || item.admissions_stats.published_mcat_average);
    const schoolGpa = parseScore(item.ranking.school_gpa_for_fit || item.ranking.published_gpa_average || item.admissions_stats.published_gpa_average);
    const overrides = {};
    if (mcatValue !== null && schoolMcat !== null) overrides.admissions_mcat_fit_score = clamp(7 + (mcatValue - schoolMcat) / 2);
    if (gpaValue !== null && schoolGpa !== null) overrides.admissions_gpa_fit_score = clamp(7 + (gpaValue - schoolGpa) / 0.08);
    const oosScore = selectorOosScore(item);
    if (oosScore !== null) overrides.admissions_oos_friendliness_score = oosScore;
    const costBasis = costBasisBySchool.get(item.school.school_id);
    if (costBasis !== null && minCost !== null && maxCost !== null) {
      const costScore = minCost === maxCost ? 10 : 10 - 9 * ((costBasis - minCost) / (maxCost - minCost));
      overrides.attendance_cost_score = costScore;
      overrides.debt_burden_score = costScore;
    }
    const admissions = weightedAverage(item, 'Admissions Score', overrides);
    overrides.admissions_score = admissions.score;
    const attendance = weightedAverage(item, 'Attendance Score', overrides);
    overrides.attendance_score = attendance.score;
    const overall = weightedAverage(item, 'Overall School Value', overrides);
    return {item, overrides, admissions, attendance, overall, costBasis};
  }).filter(row => row.overall.score !== null);

  computed.sort((a, b) => b.overall.score - a.overall.score);
  let rank = 0;
  let previousScore = null;
  computed.forEach((row, index) => {
    const rounded = Number(row.overall.score.toFixed(4));
    if (previousScore === null || rounded !== previousScore) {
      rank = index + 1;
      previousScore = rounded;
    }
    row.decisionRank = rank;
  });
  return computed;
}

function csvEscape(value) {
  const text = String(value ?? '');
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function downloadCsv(filename, headers, records) {
  const lines = [
    headers.join(','),
    ...records.map(record => headers.map(header => csvEscape(record[header])).join(',')),
  ];
  const blob = new Blob([lines.join('\n') + '\n'], {type: 'text/csv'});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function sortRows(tableRows, tableKey, defaultKey, defaultDir='asc') {
  const state = sortState[tableKey] || {key: defaultKey, dir: defaultDir};
  const valueFor = (row) => state.get ? state.get(row) : state.key.split('.').reduce((o,k)=>o?.[k], row);
  return [...tableRows].sort((a, b) => {
    const rawA = valueFor(a);
    const rawB = valueFor(b);
    const aMissing = rawA === undefined || rawA === null || String(rawA).trim() === '';
    const bMissing = rawB === undefined || rawB === null || String(rawB).trim() === '';
    if (aMissing && bMissing) return 0;
    if (aMissing) return 1;
    if (bMissing) return -1;
    const av = String(rawA).toLowerCase();
    const bv = String(rawB).toLowerCase();
    const an = Number(av), bn = Number(bv);
    const result = !Number.isNaN(an) && !Number.isNaN(bn) ? an - bn : av.localeCompare(bv);
    return state.dir === 'desc' ? -result : result;
  });
}

function dataQualityRows() { return rows('data_quality_report'); }
function warningCount() { return dataQualityRows().filter(i => i.severity === 'warning').length; }
function errorCount() { return dataQualityRows().filter(i => i.severity === 'error').length; }
function sourceStatus() { return payload.source_status || {}; }
function sourceMetric(path, fallback='0') {
  const value = path.split('.').reduce((obj, key) => obj?.[key], sourceStatus());
  return value === undefined || value === null || value === '' ? fallback : value;
}

function linkSchool(item) {
  return `<a href="${item.profile_route || `#/schools/${item.school_slug}`}">${item.school.school_name}</a>`;
}

function readinessBadge(list) {
  return badge(list.readiness_label, list.readiness_label);
}

function rankingFilters() {
  const degrees = [...new Set(rows('schools').map(s => s.school.degree_type).filter(Boolean))].sort();
  const states = [...new Set(rows('schools').map(s => s.school.state).filter(Boolean))].sort();
  const tiers = [...new Set(rows('schools').map(s => s.derived.admissions_fit_tier).filter(Boolean))].sort();
  const buckets = [...new Set(rows('schools').map(s => s.derived.application_bucket).filter(Boolean))].sort();
  const qualities = [...new Set(rows('schools').map(s => s.derived.admissions_data_quality_band).filter(Boolean))].sort();
  const mcatBands = [...new Set(rows('schools').map(s => s.derived.published_mcat_band).filter(Boolean))].sort();
  const gpaBands = [...new Set(rows('schools').map(s => s.derived.published_gpa_band).filter(Boolean))].sort();
  const aamcRateBands = [...new Set(rows('schools').map(s => s.derived.aamc_acceptance_rate_band).filter(Boolean))].sort();
  const f = filters.rankings;
  const adminFilters = ADMIN_ENABLED ? `
      <label>Hard No <select id="rankHardNo"><option value="" ${f.hardNo === '' ? 'selected' : ''}>All</option><option value="yes" ${f.hardNo === 'yes' ? 'selected' : ''}>Yes</option><option value="no" ${f.hardNo === 'no' ? 'selected' : ''}>No</option></select></label>
      <label>Rankable <select id="rankExcluded"><option value="" ${f.excluded === '' ? 'selected' : ''}>All</option><option value="yes" ${f.excluded === 'yes' ? 'selected' : ''}>Excluded</option><option value="no" ${f.excluded === 'no' ? 'selected' : ''}>Rankable</option></select></label>
      <label>Warnings <select id="rankWarnings"><option value="" ${f.warnings === '' ? 'selected' : ''}>All</option><option value="yes" ${f.warnings === 'yes' ? 'selected' : ''}>Has warnings</option><option value="no" ${f.warnings === 'no' ? 'selected' : ''}>No warnings</option></select></label>
      <label>Partner <select id="rankPartner"><option value="" ${f.partner === '' ? 'selected' : ''}>All</option><option value="present" ${f.partner === 'present' ? 'selected' : ''}>Present</option><option value="missing" ${f.partner === 'missing' ? 'selected' : ''}>Missing</option></select></label>` : '';
  return `
    <div class="filters">
      <label>Degree <select id="rankDegree"><option value="" ${f.degree === '' ? 'selected' : ''}>All</option>${optionTags(degrees, f.degree)}</select></label>
      <label>State <select id="rankState"><option value="" ${f.state === '' ? 'selected' : ''}>All</option>${optionTags(states, f.state)}</select></label>
      <label>Tier <select id="rankTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
      <label>Bucket <select id="rankBucket"><option value="" ${f.bucket === '' ? 'selected' : ''}>All</option>${optionTags(buckets, f.bucket)}</select></label>
      <label>Visibility <select id="rankVisibility"><option value="visible" ${f.visibility === 'visible' ? 'selected' : ''}>Visible</option><option value="all" ${f.visibility === 'all' ? 'selected' : ''}>All</option><option value="hidden" ${f.visibility === 'hidden' ? 'selected' : ''}>Hidden</option></select></label>
      ${adminFilters}
      <label>Stats Quality <select id="rankQuality"><option value="" ${f.quality === '' ? 'selected' : ''}>All</option>${optionTags(qualities, f.quality)}</select></label>
      <label>MCAT Band <select id="rankMcatBand"><option value="" ${f.mcatBand === '' ? 'selected' : ''}>All</option>${optionTags(mcatBands, f.mcatBand)}</select></label>
      <label>GPA Band <select id="rankGpaBand"><option value="" ${f.gpaBand === '' ? 'selected' : ''}>All</option>${optionTags(gpaBands, f.gpaBand)}</select></label>
      <label>AAMC Rate Band <select id="rankAamcRateBand"><option value="" ${f.aamcRateBand === '' ? 'selected' : ''}>All</option>${optionTags(aamcRateBands, f.aamcRateBand)}</select></label>
      <label>Missing Scores <select id="rankMissingScore"><option value="" ${f.missingScore === '' ? 'selected' : ''}>All</option><option value="missing" ${f.missingScore === 'missing' ? 'selected' : ''}>Missing</option><option value="complete" ${f.missingScore === 'complete' ? 'selected' : ''}>Complete</option></select></label>
      <label>Score Warnings <select id="rankScoreWarning"><option value="" ${f.scoreWarning === '' ? 'selected' : ''}>All</option><option value="warning" ${f.scoreWarning === 'warning' ? 'selected' : ''}>Has warnings</option><option value="clear" ${f.scoreWarning === 'clear' ? 'selected' : ''}>Clear</option></select></label>
    </div>`;
}

function rankingsRows() {
  const {degree, state, tier, bucket, visibility, hardNo, excluded, warnings, partner, quality, mcatBand, gpaBand, aamcRateBand, missingScore, scoreWarning} = filters.rankings;
  return filteredSchools().filter(s => {
    if (degree && s.school.degree_type !== degree) return false;
    if (state && s.school.state !== state) return false;
    if (tier && s.derived.admissions_fit_tier !== tier) return false;
    if (bucket && s.derived.application_bucket !== bucket) return false;
    if (visibility === 'visible' && isSchoolHidden(s)) return false;
    if (visibility === 'hidden' && !isSchoolHidden(s)) return false;
    if (ADMIN_ENABLED && hardNo === 'yes' && !s.derived.hard_no_flag) return false;
    if (ADMIN_ENABLED && hardNo === 'no' && s.derived.hard_no_flag) return false;
    if (ADMIN_ENABLED && excluded === 'yes' && !s.derived.excluded_from_rank) return false;
    if (ADMIN_ENABLED && excluded === 'no' && s.derived.excluded_from_rank) return false;
    if (ADMIN_ENABLED && warnings === 'yes' && s.derived.warning_count < 1) return false;
    if (ADMIN_ENABLED && warnings === 'no' && s.derived.warning_count > 0) return false;
    if (ADMIN_ENABLED && partner && s.derived.partner_input_status !== partner) return false;
    if (quality && s.derived.admissions_data_quality_band !== quality) return false;
    if (mcatBand && s.derived.published_mcat_band !== mcatBand) return false;
    if (gpaBand && s.derived.published_gpa_band !== gpaBand) return false;
    if (aamcRateBand && s.derived.aamc_acceptance_rate_band !== aamcRateBand) return false;
    if (missingScore && s.derived.missing_score_status !== missingScore) return false;
    if (scoreWarning && s.derived.score_warning_status !== scoreWarning) return false;
    return true;
  });
}

function mdSelectorControls() {
  const mcatBands = unique(rows('aamc_mcat_gpa_grid').map(row => row.mcat_band));
  const gpaBands = unique(rows('aamc_mcat_gpa_grid').map(row => row.gpa_band));
  const states = unique(rows('schools').map(item => item.school.state_abbrev || item.ranking.state_abbrev)).sort();
  const ready = selectorReady();
  const selectorStatus = ready
    ? `${selectorRankedRows().length} active MD schools in selector view`
    : 'Select MCAT band, GPA band, and applicant state to calculate the MD selector ranking.';
  return `<div class="panel selector-panel">
      <h3>MD Band Selector ${badge('local/private-derived', 'warn')}</h3>
      <div class="caveat">MD-only proof of concept. DO schools are excluded from this interactive reranking view. Selected-profile rankings stay in browser memory and are not written back.</div>
      <div class="filters">
        <label>MCAT Band <select id="selectorMcatBand"><option value="" ${selectorState.mcatBand === '' ? 'selected' : ''}>Unselected</option>${optionTags(mcatBands, selectorState.mcatBand)}</select></label>
        <label>GPA Band <select id="selectorGpaBand"><option value="" ${selectorState.gpaBand === '' ? 'selected' : ''}>Unselected</option>${optionTags(gpaBands, selectorState.gpaBand)}</select></label>
        <label>Applicant State <select id="selectorApplicantState"><option value="" ${selectorState.applicantState === '' ? 'selected' : ''}>Unselected</option>${optionTags(states, selectorState.applicantState)}</select></label>
      </div>
      <div class="selector-actions">
        <button type="button" id="downloadSelectorAssumptions">Download Assumptions CSV</button>
        <button type="button" id="downloadSelectorRows" ${ready ? '' : 'disabled title="Select all assumptions first"'}>Download Current MD Ranking CSV</button>
        <span class="muted">${selectorStatus}</span>
      </div>
      <div id="mdSelectorTable"></div>
    </div>`;
}

function renderMdSelectorTable() {
  if (!selectorReady()) {
    $('mdSelectorTable').innerHTML = '<div class="empty-state">No selected-profile ranking is shown until MCAT band, GPA band, and applicant state are selected. This prevents unselected assumptions from looking like a real Decision Rank.</div>';
    return;
  }
  const selectedRows = selectorRankedRows().slice(0, 50);
  const columns = [
    {key:'selector.decisionRank', label:'Decision Rank', render:r=>r.decisionRank},
    {key:'item.school.school_name', label:'School', render:r=>linkSchool(r.item)},
    {key:'item.school.city', label:'Location', render:r=>`${missing(r.item.school.city)}, ${missing(r.item.school.state)}`},
    {key:'selector.overall', label:'Selected Overall', render:r=>r.overall.score.toFixed(2)},
    {key:'selector.admissions', label:'Admissions', render:r=>r.admissions.score === null ? 'Missing' : r.admissions.score.toFixed(2)},
    {key:'selector.attendance', label:'Attendance', render:r=>r.attendance.score === null ? 'Missing' : r.attendance.score.toFixed(2)},
    {key:'selector.mcat', label:'MCAT Fit', render:r=>r.overrides.admissions_mcat_fit_score === undefined ? 'Missing' : r.overrides.admissions_mcat_fit_score.toFixed(1)},
    {key:'selector.gpa', label:'GPA Fit', render:r=>r.overrides.admissions_gpa_fit_score === undefined ? 'Missing' : r.overrides.admissions_gpa_fit_score.toFixed(1)},
    {key:'selector.oos', label:'OOS Fit', render:r=>r.overrides.admissions_oos_friendliness_score === undefined ? 'Missing' : r.overrides.admissions_oos_friendliness_score.toFixed(1)},
    {key:'selector.cost', label:'Cost Fit', render:r=>r.overrides.attendance_cost_score === undefined ? 'Missing' : r.overrides.attendance_cost_score.toFixed(1)},
    {key:'ranking.rank_confidence', label:'Rank Confidence', render:r=>badge(r.item.ranking.rank_confidence)},
  ];
  $('mdSelectorTable').innerHTML = table(columns, selectedRows, 'mdSelector');
}

function selectedAssumptionRecords() {
  return [{
    scope: 'active_md_only',
    mcat_band: selectorState.mcatBand,
    gpa_band: selectorState.gpaBand,
    applicant_state: selectorState.applicantState,
    weight_basis: payload.scoring_config?.weight_basis || 'present_components_only',
    privacy_label: 'local/private-derived',
    aamc_context: payload.copy.aamc_grid_caveat,
  }];
}

function selectedRankingRecords() {
  if (!selectorReady()) return [];
  return selectorRankedRows().map(row => ({
    decision_rank: row.decisionRank,
    school_id: row.item.school.school_id,
    school_name: row.item.school.school_name,
    degree_type: row.item.school.degree_type,
    city: row.item.school.city,
    state: row.item.school.state,
    selected_overall_school_value: row.overall.score.toFixed(4),
    selected_admissions_score: row.admissions.score === null ? '' : row.admissions.score.toFixed(4),
    selected_attendance_score: row.attendance.score === null ? '' : row.attendance.score.toFixed(4),
    selected_mcat_fit_score: row.overrides.admissions_mcat_fit_score === undefined ? '' : row.overrides.admissions_mcat_fit_score.toFixed(1),
    selected_gpa_fit_score: row.overrides.admissions_gpa_fit_score === undefined ? '' : row.overrides.admissions_gpa_fit_score.toFixed(1),
    selected_oos_fit_score: row.overrides.admissions_oos_friendliness_score === undefined ? '' : row.overrides.admissions_oos_friendliness_score.toFixed(1),
    selected_cost_fit_score: row.overrides.attendance_cost_score === undefined ? '' : row.overrides.attendance_cost_score.toFixed(1),
    mcat_band: selectorState.mcatBand,
    gpa_band: selectorState.gpaBand,
    applicant_state: selectorState.applicantState,
    privacy_label: 'local/private-derived',
  }));
}

function renderVisibilityPanel() {
  const hidden = hiddenSchools();
  const hiddenTable = hidden.length ? table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'visibility.visibility_reason', label:'Reason', render:s=>`<input data-visibility-reason="${attr(schoolId(s))}" value="${attr(visibilityFor(s).visibility_reason)}" placeholder="Why hidden">`},
    {key:'visibility.hidden_at', label:'Hidden At', render:s=>missing(visibilityFor(s).hidden_at)},
    {key:'actions', label:'Actions', render:s=>`<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(s))}">Restore</button>`},
  ], hidden, 'hiddenSchools') : '<div class="empty-state">No schools are hidden in this browser session.</div>';
  return `<div class="panel selector-panel">
    <div class="inline-actions">
      <h3 style="margin:0">Visibility Controls</h3>
      ${badge(`${hidden.length} hidden`, hidden.length ? 'warn' : 'good')}
      <button type="button" id="downloadVisibilityExport">Download Visibility CSV</button>
    </div>
    <p>Visibility is local to this browser session. Export the CSV before closing the page if you want to preserve hide/restore decisions.</p>
    <div style="margin-top:10px">${hiddenTable}</div>
  </div>`;
}

function renderRankings() {
  $('rankings').innerHTML = `<h2>Rankings</h2><div class="caveat">${payload.copy.aamc_grid_caveat}</div>${renderVisibilityPanel()}${mdSelectorControls()}${rankingFilters()}<div id="rankTable"></div>`;
  const bindings = {
    rankDegree: 'degree',
    rankState: 'state',
    rankTier: 'tier',
    rankBucket: 'bucket',
    rankVisibility: 'visibility',
    rankQuality: 'quality',
    rankMcatBand: 'mcatBand',
    rankGpaBand: 'gpaBand',
    rankAamcRateBand: 'aamcRateBand',
    rankMissingScore: 'missingScore',
    rankScoreWarning: 'scoreWarning',
  };
  if (ADMIN_ENABLED) {
    bindings.rankHardNo = 'hardNo';
    bindings.rankExcluded = 'excluded';
    bindings.rankWarnings = 'warnings';
    bindings.rankPartner = 'partner';
  }
  Object.entries(bindings).forEach(([id, key]) => $(id)?.addEventListener('change', event => {
    filters.rankings[key] = event.target.value;
    renderRankingTable();
  }));
  const selectorBindings = {
    selectorMcatBand: 'mcatBand',
    selectorGpaBand: 'gpaBand',
    selectorApplicantState: 'applicantState',
  };
  Object.entries(selectorBindings).forEach(([id, key]) => $(id)?.addEventListener('change', event => {
    selectorState[key] = event.target.value;
    renderRankings();
  }));
  $('downloadSelectorAssumptions')?.addEventListener('click', () => {
    downloadCsv('selected-profile-assumptions.csv', Object.keys(selectedAssumptionRecords()[0]), selectedAssumptionRecords());
  });
  $('downloadSelectorRows')?.addEventListener('click', () => {
    const records = selectedRankingRecords();
    if (!records.length) return;
    downloadCsv('selected-md-decision-rankings.csv', Object.keys(records[0]), records);
  });
  $('downloadVisibilityExport')?.addEventListener('click', downloadVisibilityExport);
  renderMdSelectorTable();
  renderRankingTable();
}

function renderRankingTable() {
  const visibleRows = sortRows(rankingsRows(), 'rankings', 'ranking.overall_rank');
  const columns = [
    {key:'ranking.overall_rank', label:'Decision Rank', render:s=>missing(s.ranking.decision_rank || s.ranking.overall_rank)},
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'ranking.rank_band', label:'Rank Band', render:s=>missing(s.ranking.rank_band)},
    {key:'ranking.rank_confidence', label:'Confidence', render:s=>badge(s.ranking.rank_confidence)},
    {key:'ranking.admissions_fit_tier', label:'Admissions Tier', render:s=>missing(s.ranking.admissions_fit_tier || s.ranking.dynamic_tier)},
    {key:'ranking.application_bucket', label:'Bucket', render:s=>missing(s.ranking.application_bucket || s.ranking.suggested_funnel_bucket)},
    {key:'visibility.visibility_state', label:'Visibility', render:s=>visibilityBadge(s)},
    {key:'ranking.overall_school_value', label:'Overall', render:s=>missing(s.ranking.overall_school_value)},
    {key:'ranking.admissions_score', label:'Admissions', render:s=>missing(s.ranking.admissions_score)},
    {key:'ranking.attendance_score', label:'Attendance', render:s=>missing(s.ranking.attendance_score)},
    {key:'ranking.admissions_mcat_fit_score', label:'MCAT Fit', render:s=>missing(s.ranking.admissions_mcat_fit_score)},
    {key:'ranking.admissions_gpa_fit_score', label:'GPA Fit', render:s=>missing(s.ranking.admissions_gpa_fit_score)},
    {key:'ranking.admissions_oos_friendliness_score', label:'OOS Fit', render:s=>missing(s.ranking.admissions_oos_friendliness_score)},
    {key:'ranking.attendance_cost_score', label:'Cost Fit', render:s=>missing(s.ranking.attendance_cost_score)},
    {key:'ranking.data_completeness_score', label:'Data', render:s=>missing(s.ranking.data_completeness_score)},
    {key:'derived.admissions_data_quality_band', label:'Stats Quality', render:s=>badge(s.derived.admissions_data_quality_band)},
    {key:'ranking.published_mcat_average', label:'MCAT Avg', render:s=>missing(s.ranking.published_mcat_average || s.admissions_stats.published_mcat_average)},
    {key:'ranking.published_gpa_average', label:'GPA Avg', render:s=>missing(s.ranking.published_gpa_average || s.admissions_stats.published_gpa_average)},
    {key:'ranking.profile_aamc_acceptance_rate', label:'Profile AAMC', render:s=>missing(s.ranking.profile_aamc_acceptance_rate)},
    {key:'derived.aamc_acceptance_rate_band', label:'AAMC Band', render:s=>missing(s.ranking.profile_aamc_acceptance_rate_band || s.derived.aamc_acceptance_rate_band)},
    {key:'ranking.score_warnings', label:'Score Warnings', render:s=>s.ranking.score_warnings ? badge('Has warnings', 'warn') : 'Clear'},
    {key:'actions', label:'Actions', render:s=>`<div class="inline-actions"><a href="${s.profile_route || `#/schools/${s.school_slug}`}">Dossier</a>${isSchoolHidden(s) ? `<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(s))}">Restore</button>` : `<button type="button" data-action="hide-school" data-school-id="${attr(schoolId(s))}">Hide</button>`}</div>`},
  ];
  if (ADMIN_ENABLED) {
    columns.push(
      {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
      {key:'derived.excluded_from_rank', label:'Excluded', render:s=>s.derived.excluded_from_rank ? badge('Excluded', 'warn') : ''},
      {key:'derived.hard_no_flag', label:'Hard No', render:s=>s.derived.hard_no_flag ? badge('Hard No', 'error') : ''},
      {key:'derived.partner_input_status', label:'Partner', render:s=>s.derived.partner_input_status}
    );
  }
  const label = filters.rankings.visibility === 'hidden' ? 'hidden schools' : filters.rankings.visibility === 'all' ? 'schools' : 'visible schools';
  $('rankTable').innerHTML = `<p>${visibleRows.length} ${label}</p>` + table(columns, visibleRows, 'rankings');
}

function renderLists() {
  $('lists').innerHTML = `<h2>Curated Lists</h2>
    <div class="caveat">${payload.copy.curated_list_readiness.provisional}</div>
    ${table([
      {key:'title', label:'List', render:list=>`<a href="${list.route}">${list.title}</a>`},
      {key:'category', label:'Category', render:list=>missing(list.category)},
      {key:'readiness_label', label:'Readiness', render:list=>readinessBadge(list)},
      {key:'default_apply_mode', label:'Apply Mode', render:list=>missing(list.default_apply_mode)},
      {key:'missing_fields', label:'Missing Fields', render:list=>(list.missing_fields || []).join(', ') || 'None'},
      {key:'missing_data_behavior', label:'Missing Data Behavior', render:list=>missing(list.missing_data_behavior)},
    ], rows('curated_lists'), 'lists')}`;
}

function renderListDetail() {
  const list = rows('curated_lists').find(item => item.slug === currentRoute.slug);
  if (!list) {
    $('listDetail').innerHTML = '<h2>List not found</h2><p><a href="#/lists">Back to curated lists</a></p>';
    return;
  }
  $('listDetail').innerHTML = `<div class="route-tools"><a href="#/lists">All lists</a><a href="#/rankings">Rankings</a></div>
    <h2>${list.title} ${readinessBadge(list)}</h2>
    <p>${list.description}</p>
    <div class="detail-grid">
      ${detailPanel('Readiness', [
        ['Label', list.readiness_label],
        ['Confidence', list.confidence_label],
        ['Required fields', (list.required_fields || []).join(', ')],
        ['Available fields', (list.available_fields || []).join(', ') || 'None'],
        ['Missing fields', (list.missing_fields || []).join(', ') || 'None'],
      ])}
      ${detailPanel('Lens', [
        ['Scoring profile', list.scoring_profile_id],
        ['Default apply mode', list.default_apply_mode],
        ['Methodology', list.methodology_notes],
        ['Missing data behavior', list.missing_data_behavior],
      ])}
    </div>
    <div class="panel" style="margin-top:12px">
      <h3>School Universe Preview</h3>
      ${table([
        {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
        {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
        {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
        {key:'ranking.overall_school_value', label:'Overall', render:s=>missing(s.ranking.overall_school_value)},
        {key:'derived.admissions_data_quality_band', label:'Stats Quality', render:s=>badge(s.derived.admissions_data_quality_band)},
      ], sortRows(filteredSchools(), `list-${list.slug}`, 'ranking.overall_rank').slice(0, 50), `list-${list.slug}`)}
    </div>`;
}

function renderCompare() {
  $('compare').innerHTML = `<h2>Compare</h2>
    <p>Comparison routing is separated from admin views; selected-school state will be layered onto this product route in a later slice.</p>
    ${table([
      {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
      {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
      {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
      {key:'admissions_stats.published_mcat_average', label:'MCAT Avg', render:s=>missing(s.admissions_stats.published_mcat_average)},
      {key:'admissions_stats.published_gpa_average', label:'GPA Avg', render:s=>missing(s.admissions_stats.published_gpa_average)},
      {key:'cost_and_debt.estimated_coa_out_state', label:'OOS COA', render:s=>missing(s.cost_and_debt.estimated_coa_out_state)},
    ], sortRows(filteredSchools(), 'compare', 'ranking.overall_rank').slice(0, 25), 'compare')}`;
}

function scoreOptions(selected) {
  const options = [''].concat(Array.from({length: 10}, (_, index) => String(index + 1)));
  return options.map(value => `<option value="${value}" ${String(selected || '') === value ? 'selected' : ''}>${value || 'Unselected'}</option>`).join('');
}

function labeledOptions(values, selected) {
  return [''].concat(values).map(value => `<option value="${value}" ${String(selected || '') === value ? 'selected' : ''}>${labelize(value)}</option>`).join('');
}

function dossierSelect(item, field, label, values) {
  const id = schoolId(item);
  const dossier = dossierFor(item);
  const options = Array.isArray(values) ? labeledOptions(values, dossier[field]) : scoreOptions(dossier[field]);
  return `<label>${label}<select data-dossier-school="${attr(id)}" data-dossier-field="${attr(field)}">${options}</select></label>`;
}

function dossierInput(item, field, label, placeholder='') {
  const id = schoolId(item);
  const dossier = dossierFor(item);
  return `<label>${label}<input data-dossier-school="${attr(id)}" data-dossier-field="${attr(field)}" value="${attr(dossier[field] || '')}" placeholder="${attr(placeholder)}"></label>`;
}

function dossierTextarea(item, field, label, placeholder='') {
  const id = schoolId(item);
  const dossier = dossierFor(item);
  return `<label class="full-span">${label}<textarea data-dossier-school="${attr(id)}" data-dossier-field="${attr(field)}" placeholder="${attr(placeholder)}">${safeText(dossier[field] || '')}</textarea></label>`;
}

function renderDossierForm(item) {
  const editCount = dossierExportRecords().length;
  return `<div class="panel" style="margin-top:12px">
    <div class="inline-actions">
      <h3 style="margin:0">Local Dossier</h3>
      ${badge(`${editCount} edited`, editCount ? 'warn' : '')}
      <button type="button" id="downloadDossierExport">Download Dossier Edits CSV</button>
      ${isSchoolHidden(item)
        ? `<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(item))}">Restore School</button>`
        : `<button type="button" data-action="hide-school" data-school-id="${attr(schoolId(item))}">Hide School</button>`}
    </div>
    <p>These edits stay in browser memory until exported. They do not change the source ranking model.</p>
    <div class="field-grid" style="margin-top:10px">
      ${dossierSelect(item, 'research_status', 'Research status', RESEARCH_STATUSES)}
      ${dossierSelect(item, 'interest_level', 'Interest level', INTEREST_LEVELS)}
      ${dossierSelect(item, 'four_year_happiness', 'Could live here 4 years', null)}
      ${dossierSelect(item, 'location_fit', 'Location fit', null)}
      ${dossierSelect(item, 'culture_fit', 'Culture fit', null)}
      ${dossierSelect(item, 'regret_index', 'Regret index', null)}
      ${dossierSelect(item, 'hard_no_flag', 'Hard no', ['TRUE', 'FALSE'])}
      ${dossierInput(item, 'hard_no_reason', 'Hard no reason', 'Only if hard no')}
      ${dossierSelect(item, 'application_decision_status', 'Application decision', DECISION_STATUSES)}
      ${dossierTextarea(item, 'notes', 'Dossier notes', 'School-specific research, subjective fit, unanswered questions')}
    </div>
  </div>`;
}

function dossierRows() {
  const f = filters.dossiers;
  return filteredSchools().filter(item => {
    if (f.visibility === 'visible' && isSchoolHidden(item)) return false;
    if (f.visibility === 'hidden' && !isSchoolHidden(item)) return false;
    if (f.status && researchStatusFor(item) !== f.status) return false;
    if (f.tier && (item.ranking.admissions_fit_tier || item.ranking.dynamic_tier || item.derived.admissions_fit_tier) !== f.tier) return false;
    if (f.rankBand && (item.ranking.rank_band || item.derived.rank_band) !== f.rankBand) return false;
    if (f.missing === 'missing' && !missingDossierSections(item).length) return false;
    if (f.missing === 'complete' && missingDossierSections(item).length) return false;
    return true;
  });
}

function renderDossierFilters() {
  const tiers = unique(rows('schools').map(s => s.ranking.admissions_fit_tier || s.ranking.dynamic_tier || s.derived.admissions_fit_tier)).sort();
  const rankBands = unique(rows('schools').map(s => s.ranking.rank_band || s.derived.rank_band)).sort();
  const f = filters.dossiers;
  return `<div class="filters">
    <label>Visibility <select id="dossierVisibility"><option value="visible" ${f.visibility === 'visible' ? 'selected' : ''}>Visible</option><option value="all" ${f.visibility === 'all' ? 'selected' : ''}>All</option><option value="hidden" ${f.visibility === 'hidden' ? 'selected' : ''}>Hidden</option></select></label>
    <label>Research Status <select id="dossierStatus">${labeledOptions(RESEARCH_STATUSES, f.status)}</select></label>
    <label>Missing Sections <select id="dossierMissing"><option value="" ${f.missing === '' ? 'selected' : ''}>All</option><option value="missing" ${f.missing === 'missing' ? 'selected' : ''}>Has missing</option><option value="complete" ${f.missing === 'complete' ? 'selected' : ''}>Complete</option></select></label>
    <label>Admissions Tier <select id="dossierTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
    <label>Rank Band <select id="dossierRankBand"><option value="" ${f.rankBand === '' ? 'selected' : ''}>All</option>${optionTags(rankBands, f.rankBand)}</select></label>
  </div>`;
}

function renderDossiers() {
  const tableRows = sortRows(dossierRows(), 'dossiers', 'ranking.overall_rank');
  $('dossiers').innerHTML = `<h2>School Dossiers</h2>
    <div class="caveat">Dossiers combine source-backed fields with local reviewer notes. Local edits are exported separately and do not mutate the seed data.</div>
    <div class="grid">
      ${metric('Visible schools', rows('schools').filter(item => !isSchoolHidden(item)).length)}
      ${metric('Hidden schools', hiddenSchools().length)}
      ${metric('Edited dossiers', dossierExportRecords().length)}
      ${metric('Rows in view', tableRows.length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" id="downloadDossierIndexExport">Download Dossier Edits CSV</button>
      <button type="button" id="downloadDossierVisibilityExport">Download Visibility CSV</button>
    </div>
    ${renderDossierFilters()}
    ${table([
      {key:'ranking.overall_rank', label:'Decision Rank', render:s=>missing(s.ranking.decision_rank || s.ranking.overall_rank)},
      {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
      {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
      {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
      {key:'ranking.admissions_fit_tier', label:'Admissions Tier', render:s=>missing(s.ranking.admissions_fit_tier || s.ranking.dynamic_tier || s.derived.admissions_fit_tier)},
      {key:'ranking.rank_confidence', label:'Confidence', render:s=>badge(s.ranking.rank_confidence || s.derived.rank_confidence)},
      {key:'dossier.research_status', label:'Research Status', render:s=>labelize(researchStatusFor(s))},
      {key:'visibility.visibility_state', label:'Visibility', render:s=>visibilityBadge(s)},
      {key:'dossier.missing', label:'Missing Sections', render:s=>missingDossierSections(s).join(', ') || 'Complete'},
      {key:'research.next', label:'Next Action', render:s=>nextResearchAction(s)},
      {key:'actions', label:'Actions', render:s=>`<div class="inline-actions"><a href="${s.profile_route || `#/schools/${s.school_slug}`}">Open</a>${isSchoolHidden(s) ? `<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(s))}">Restore</button>` : `<button type="button" data-action="hide-school" data-school-id="${attr(schoolId(s))}">Hide</button>`}</div>`},
    ], tableRows, 'dossiers')}`;
  const bindings = {
    dossierVisibility: 'visibility',
    dossierStatus: 'status',
    dossierMissing: 'missing',
    dossierTier: 'tier',
    dossierRankBand: 'rankBand',
  };
  Object.entries(bindings).forEach(([id, key]) => $(id)?.addEventListener('change', event => {
    filters.dossiers[key] = event.target.value;
    renderDossiers();
  }));
  $('downloadDossierIndexExport')?.addEventListener('click', downloadDossierExport);
  $('downloadDossierVisibilityExport')?.addEventListener('click', downloadVisibilityExport);
}

function researchQueueRows() {
  const f = filters.research;
  const actions = {
    start: 'Start dossier',
    score: 'Score four-year fit',
    interest: 'Set interest level',
    fill: 'Fill',
    decision: 'Set decision status',
    ready: 'Ready for shortlist review',
    hidden: 'Review hidden status',
  };
  return filteredSchools().map(item => ({
    item,
    status: researchStatusFor(item),
    missingSections: missingDossierSections(item),
    action: nextResearchAction(item),
  })).filter(row => {
    const item = row.item;
    if (f.visibility === 'visible' && isSchoolHidden(item)) return false;
    if (f.visibility === 'hidden' && !isSchoolHidden(item)) return false;
    if (f.status && row.status !== f.status) return false;
    if (f.tier && (item.ranking.admissions_fit_tier || item.ranking.dynamic_tier || item.derived.admissions_fit_tier) !== f.tier) return false;
    if (f.rankBand && (item.ranking.rank_band || item.derived.rank_band) !== f.rankBand) return false;
    if (f.action && !row.action.startsWith(actions[f.action])) return false;
    return true;
  }).sort((a, b) => {
    const hiddenDelta = Number(isSchoolHidden(a.item)) - Number(isSchoolHidden(b.item));
    if (hiddenDelta) return hiddenDelta;
    const rankA = parseScore(a.item.ranking.decision_rank || a.item.ranking.overall_rank) ?? 9999;
    const rankB = parseScore(b.item.ranking.decision_rank || b.item.ranking.overall_rank) ?? 9999;
    return rankA - rankB;
  });
}

function renderResearchFilters() {
  const tiers = unique(rows('schools').map(s => s.ranking.admissions_fit_tier || s.ranking.dynamic_tier || s.derived.admissions_fit_tier)).sort();
  const rankBands = unique(rows('schools').map(s => s.ranking.rank_band || s.derived.rank_band)).sort();
  const f = filters.research;
  return `<div class="filters">
    <label>Visibility <select id="researchVisibility"><option value="visible" ${f.visibility === 'visible' ? 'selected' : ''}>Visible</option><option value="all" ${f.visibility === 'all' ? 'selected' : ''}>All</option><option value="hidden" ${f.visibility === 'hidden' ? 'selected' : ''}>Hidden</option></select></label>
    <label>Research Status <select id="researchStatus">${labeledOptions(RESEARCH_STATUSES, f.status)}</select></label>
    <label>Next Action <select id="researchAction"><option value="" ${f.action === '' ? 'selected' : ''}>All</option><option value="start" ${f.action === 'start' ? 'selected' : ''}>Start dossier</option><option value="score" ${f.action === 'score' ? 'selected' : ''}>Score four-year fit</option><option value="interest" ${f.action === 'interest' ? 'selected' : ''}>Set interest level</option><option value="fill" ${f.action === 'fill' ? 'selected' : ''}>Fill source gap</option><option value="decision" ${f.action === 'decision' ? 'selected' : ''}>Set decision status</option><option value="ready" ${f.action === 'ready' ? 'selected' : ''}>Ready</option><option value="hidden" ${f.action === 'hidden' ? 'selected' : ''}>Hidden review</option></select></label>
    <label>Admissions Tier <select id="researchTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
    <label>Rank Band <select id="researchRankBand"><option value="" ${f.rankBand === '' ? 'selected' : ''}>All</option>${optionTags(rankBands, f.rankBand)}</select></label>
  </div>`;
}

function renderResearch() {
  const queueRows = researchQueueRows();
  const visibleRows = rows('schools').filter(item => !isSchoolHidden(item));
  const readyCount = visibleRows.filter(item => nextResearchAction(item) === 'Ready for shortlist review').length;
  $('research').innerHTML = `<h2>Research Queue</h2>
    <div class="caveat">The queue is deterministic: hidden status, missing source sections, and local dossier fields drive the next action.</div>
    <div class="grid">
      ${metric('Rows in queue', queueRows.length)}
      ${metric('Visible schools', visibleRows.length)}
      ${metric('Ready for shortlist review', readyCount)}
      ${metric('Edited dossiers', dossierExportRecords().length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" id="downloadResearchDossiers">Download Dossier Edits CSV</button>
      <button type="button" id="downloadResearchVisibility">Download Visibility CSV</button>
    </div>
    ${renderResearchFilters()}
    ${table([
      {key:'item.ranking.overall_rank', label:'Decision Rank', render:r=>missing(r.item.ranking.decision_rank || r.item.ranking.overall_rank)},
      {key:'item.school.school_name', label:'School', render:r=>linkSchool(r.item)},
      {key:'item.school.degree_type', label:'Degree', render:r=>badge(r.item.school.degree_type)},
      {key:'item.school.city', label:'Location', render:r=>`${missing(r.item.school.city)}, ${missing(r.item.school.state)}`},
      {key:'item.ranking.admissions_fit_tier', label:'Admissions Tier', render:r=>missing(r.item.ranking.admissions_fit_tier || r.item.ranking.dynamic_tier || r.item.derived.admissions_fit_tier)},
      {key:'item.ranking.rank_band', label:'Rank Band', render:r=>missing(r.item.ranking.rank_band || r.item.derived.rank_band)},
      {key:'item.ranking.rank_confidence', label:'Confidence', render:r=>badge(r.item.ranking.rank_confidence || r.item.derived.rank_confidence)},
      {key:'status', label:'Research Status', render:r=>labelize(r.status)},
      {key:'visibility', label:'Visibility', render:r=>visibilityBadge(r.item)},
      {key:'missing', label:'Missing Sections', render:r=>r.missingSections.join(', ') || 'Complete'},
      {key:'action', label:'Next Action', render:r=>r.action},
      {key:'actions', label:'Actions', render:r=>`<div class="inline-actions"><a href="${r.item.profile_route || `#/schools/${r.item.school_slug}`}">Open</a>${isSchoolHidden(r.item) ? `<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(r.item))}">Restore</button>` : `<button type="button" data-action="hide-school" data-school-id="${attr(schoolId(r.item))}">Hide</button>`}</div>`},
    ], queueRows, 'researchQueue')}`;
  const bindings = {
    researchVisibility: 'visibility',
    researchStatus: 'status',
    researchAction: 'action',
    researchTier: 'tier',
    researchRankBand: 'rankBand',
  };
  Object.entries(bindings).forEach(([id, key]) => $(id)?.addEventListener('change', event => {
    filters.research[key] = event.target.value;
    renderResearch();
  }));
  $('downloadResearchDossiers')?.addEventListener('click', downloadDossierExport);
  $('downloadResearchVisibility')?.addEventListener('click', downloadVisibilityExport);
}

function renderProfile() {
  const item = rows('schools').find(s => s.school_slug === currentRoute.slug) || rows('schools')[0];
  if (!item) { $('profile').innerHTML = '<p>No school selected.</p>'; return; }
  const sourceUrl = item.school.source_url ? `<a href="${item.school.source_url}" target="_blank">Source</a>` : 'Missing';
  const localDossier = dossierFor(item);
  const contributionRows = rows('score_contributions').filter(row => (
    row.school_id === item.school.school_id
    && row.applicant_profile_id === item.ranking.applicant_profile_id
    && row.score_model === 'Decision Rank'
  ));
  const adminPanels = ADMIN_ENABLED ? `
      ${detailPanel('Partner Review', [
        ['Could live here', item.partner_input?.could_live_here_4_years_score],
        ['Location fit', item.partner_input?.location_fit_score],
        ['Culture fit', item.partner_input?.culture_fit_score],
        ['Regret index', item.partner_input?.regret_index_score],
        ['Hard no', item.derived.hard_no_flag ? 'Yes' : 'No'],
        ['Reason', item.partner_input?.hard_no_reason],
        ['Notes', item.partner_input?.partner_notes],
      ])}
      ${detailPanel('Admin Source Review', [
        ['Source status', item.derived.source_queue_status],
        ['Candidate URL', item.admissions_source?.candidate_source_url],
        ['Source review rows', item.derived.source_review_count],
        ['Warnings', item.derived.warning_count],
        ['Errors', item.derived.error_count],
        ['Next action', item.derived.suggested_next_action],
      ])}` : '';
  const issuesPanel = ADMIN_ENABLED ? `<div class="panel" style="margin-top:12px">
      <h3>Issues</h3>
      ${table([
        {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
        {key:'file', label:'File', render:i=>i.file},
        {key:'field', label:'Field', render:i=>i.field},
        {key:'message', label:'Message', render:i=>i.message},
        {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
      ], item.data_quality || [], 'detailIssues')}
    </div>` : '';
  $('profile').innerHTML = `<div class="route-tools"><a href="#/dossiers">Dossiers</a><a href="#/research">Research Queue</a><a href="#/rankings">Rankings</a><a href="#/lists">Lists</a></div>
    <h2>${item.school.school_name}</h2>
    <p>${item.school.degree_type} · ${missing(item.school.city)}, ${missing(item.school.state)} · ${sourceUrl} · ${visibilityBadge(item)}</p>
    <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
    <div class="detail-grid">
      ${detailPanel('Identity', [
        ['School ID', item.school.school_id],
        ['Parent', item.school.parent_school_name],
        ['Campus', item.school.campus_name],
        ['Accreditation', item.school.accreditation_status],
      ])}
      ${detailPanel('Ranking', [
        ['Profile', item.ranking.profile_name],
        ['Decision rank', item.ranking.decision_rank || item.ranking.overall_rank],
        ['Rank band', item.ranking.rank_band],
        ['Rank confidence', item.ranking.rank_confidence],
        ['Admissions tier', item.ranking.admissions_fit_tier || item.ranking.dynamic_tier],
        ['Bucket', item.ranking.application_bucket || item.ranking.suggested_funnel_bucket],
        ['Admissions', item.ranking.admissions_score],
        ['Attendance', item.ranking.attendance_score],
        ['MCAT fit', item.ranking.admissions_mcat_fit_score],
        ['GPA fit', item.ranking.admissions_gpa_fit_score],
        ['OOS fit', item.ranking.admissions_oos_friendliness_score],
        ['Cost fit', item.ranking.attendance_cost_score],
        ['Data completeness', item.ranking.data_completeness_score],
        ['Missing score inputs', item.ranking.missing_score_inputs],
        ['Score warnings', item.ranking.score_warnings],
        ['Positive contributors', item.ranking.top_positive_contributors || item.ranking.top_positive_drivers],
        ['Negative contributors', item.ranking.top_negative_contributors || item.ranking.top_negative_drivers],
        ['Low-confidence drivers', item.ranking.missing_or_low_confidence_drivers],
        ['Rank summary', item.ranking.rank_summary],
      ])}
      ${detailPanel('Local Dossier Status', [
        ['Visibility', visibilityFor(item).visibility_state],
        ['Research status', labelize(researchStatusFor(item))],
        ['Interest level', labelize(localDossier.interest_level)],
        ['Application decision', labelize(localDossier.application_decision_status)],
        ['Missing dossier sections', missingDossierSections(item).join(', ') || 'Complete'],
        ['Next research action', nextResearchAction(item)],
      ])}
      ${detailPanel('Admissions Facts', [
        ['Stats present', item.derived.admissions_stats_present],
        ['Published source count', item.admissions_stats.published_source_count],
        ['Published MCAT average', item.ranking.published_mcat_average || item.admissions_stats.published_mcat_average],
        ['Published GPA average', item.ranking.published_gpa_average || item.admissions_stats.published_gpa_average],
        ['School MCAT used for fit', item.ranking.school_mcat_for_fit],
        ['School GPA used for fit', item.ranking.school_gpa_for_fit],
        ['Profile MCAT band', item.ranking.profile_aamc_mcat_band],
        ['Profile GPA band', item.ranking.profile_aamc_gpa_band],
        ['Profile AAMC national rate', item.ranking.profile_aamc_acceptance_rate],
        ['Profile AAMC national rate band', item.ranking.profile_aamc_acceptance_rate_band],
        ['MCAT band', item.ranking.published_mcat_band || item.admissions_stats.published_mcat_band],
        ['GPA band', item.ranking.published_gpa_band || item.admissions_stats.published_gpa_band],
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
        ['Applicant cost basis', item.ranking.cost_basis],
        ['Adjusted cost basis', item.ranking.cost_basis_adjusted],
        ['Confidence', item.cost_and_debt.data_confidence],
      ])}
      ${detailPanel('Public Source Coverage', [
        ['Admissions policy rows', item.derived.admissions_policy_count],
        ['Letter requirement rows', item.derived.letter_requirement_count],
      ])}
      ${adminPanels}
    </div>
    ${renderDossierForm(item)}
    <div class="panel" style="margin-top:12px">
      <h3>Why This Rank?</h3>
      ${table([
        {key:'score_group', label:'Score Group', render:r=>missing(r.score_group)},
        {key:'component_label', label:'Component', render:r=>missing(r.component_label)},
        {key:'normalized_score', label:'Score', render:r=>missing(r.normalized_score)},
        {key:'component_weight', label:'Weight', render:r=>missing(r.component_weight)},
        {key:'weighted_contribution', label:'Contribution', render:r=>missing(r.weighted_contribution)},
        {key:'component_coverage_status', label:'Status', render:r=>badge(r.component_coverage_status)},
        {key:'delta_band', label:'Fit Band', render:r=>missing(r.delta_band)},
        {key:'raw_context', label:'Context', render:r=>missing(r.raw_context)},
        {key:'data_confidence', label:'Confidence', render:r=>missing(r.data_confidence)},
        {key:'missing_reason', label:'Missing Reason', render:r=>missing(r.missing_reason)},
      ], contributionRows, 'profileContributions')}
    </div>
    ${issuesPanel}`;
  $('downloadDossierExport')?.addEventListener('click', downloadDossierExport);
}

function detailPanel(title, panelRows) {
  return `<div class="panel"><h3>${title}</h3>${panelRows.map(([k,v])=>`<p><strong>${k}:</strong> ${missing(v)}</p>`).join('')}</div>`;
}

function renderMethodology() {
  const readinessRows = Object.entries(payload.copy.curated_list_readiness || {}).map(([label, text]) => ({label, text}));
  const methodologyRows = rows('scoring_methodology');
  $('methodology').innerHTML = `<h2>Methodology</h2>
    <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
    <div class="panel" style="margin-bottom:12px">
      <h3>Scoring Methodology</h3>
      ${table([
        {key:'methodology_area', label:'Area', render:r=>missing(r.methodology_area)},
        {key:'input_band_or_condition', label:'Input Band Or Condition', render:r=>missing(r.input_band_or_condition)},
        {key:'score', label:'Score', render:r=>missing(r.score)},
        {key:'display_label', label:'Display Label', render:r=>missing(r.display_label)},
        {key:'notes', label:'Notes', render:r=>missing(r.notes)},
        {key:'formula_reference', label:'Formula', render:r=>missing(r.formula_reference)},
      ], methodologyRows, 'methodologyTable')}
    </div>
    <div class="panel">
      <h3>Curated List Readiness</h3>
      ${table([
        {key:'label', label:'Label', render:r=>badge(r.label, r.label)},
        {key:'text', label:'Meaning', render:r=>r.text},
      ], readinessRows, 'readiness')}
    </div>`;
}

function renderSources() {
  $('sources').innerHTML = `<h2>Sources</h2>
    <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
    ${table([
      {key:'source_name', label:'Source', render:s=>missing(s.source_name)},
      {key:'source_url', label:'URL', render:s=>s.source_url ? `<a href="${s.source_url}" target="_blank">Open</a>` : 'Missing'},
      {key:'row_count', label:'Rows', render:s=>missing(s.row_count)},
    ], rows('public_sources'), 'publicSources')}`;
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
    <p>Generated ${missing(payload.meta.generated_at)}.</p>
  </div>`;
}

function objectRows(obj) {
  return Object.entries(obj || {}).map(([key, value]) => ({key, value}));
}

function adminNav() {
  return `<div class="route-tools">
    <a href="#/admin">Overview</a>
    <a href="#/admin/sources">Source Review</a>
    <a href="#/admin/data-quality">Data Quality</a>
    <a href="#/admin/build">Build Status</a>
  </div>`;
}

function renderAdminOverview() {
  const schools = filteredSchools();
  const md = rows('schools').filter(s => s.school.degree_type === 'MD').length;
  const degreeDo = rows('schools').filter(s => s.school.degree_type === 'DO').length;
  const partnerPresent = rows('schools').filter(s => s.derived.partner_input_status === 'present').length;
  const hardNo = rows('schools').filter(s => s.derived.hard_no_flag).length;
  const sourceFound = rows('schools').filter(s => s.admissions_source?.candidate_source_url).length;
  const priority = schools.filter(s => s.derived.suggested_next_action !== 'review ranking').slice(0, 20);
  $('admin').innerHTML = `${adminNav()}<h2>Admin Overview</h2>
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
      <h3>Top Research Priorities</h3>
      ${table([
        {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
        {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
        {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
        {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
        {key:'derived.partner_input_status', label:'Partner', render:s=>s.derived.partner_input_status},
        {key:'derived.suggested_next_action', label:'Next Action', render:s=>s.derived.suggested_next_action},
      ], priority, 'adminPriority')}
    </div>`;
}

function renderAdminSources() {
  const current = filters.sources.sourceMissing;
  $('admin').innerHTML = `${adminNav()}<h2>Source Review</h2>
    <div class="filters"><label>Source URL <select id="sourceMissing"><option value="">All</option><option value="missing">Missing</option><option value="present">Present</option></select></label></div>
    <div id="sourceTable"></div>`;
  $('sourceMissing').value = current;
  $('sourceMissing').addEventListener('change', event => {
    filters.sources.sourceMissing = event.target.value;
    renderAdminSourceTable();
  });
  renderAdminSourceTable();
}

function renderAdminSourceTable() {
  const tableRows = filteredSchools().filter(s => {
    const filter = filters.sources.sourceMissing;
    return !filter || (filter === 'missing' ? !s.admissions_source?.candidate_source_url : !!s.admissions_source?.candidate_source_url);
  });
  $('sourceTable').innerHTML = table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'admissions_source.candidate_source_url', label:'Candidate URL', render:s=>s.admissions_source?.candidate_source_url ? `<a href="${s.admissions_source.candidate_source_url}" target="_blank">Open</a>` : 'Missing'},
    {key:'derived.source_queue_status', label:'Source Status', render:s=>s.derived.source_queue_status},
    {key:'derived.admissions_stats_present', label:'Stats', render:s=>s.derived.admissions_stats_present},
    {key:'admissions_source.notes', label:'Notes', render:s=>missing(s.admissions_source?.notes)},
  ], tableRows, 'adminSources');
}

function renderAdminQuality() {
  const severity = filters.quality.severity;
  const issueRows = dataQualityRows().filter(i => !severity || i.severity === severity);
  $('admin').innerHTML = `${adminNav()}<h2>Data Quality</h2>
    <div class="grid">${metric('Errors', errorCount())}${metric('Warnings', warningCount())}</div>
    <div class="filters"><label>Severity <select id="qualitySeverity"><option value="">All</option><option value="error">Error</option><option value="warning">Warning</option><option value="info">Info</option></select></label></div>
    <div id="qualityTable"></div>`;
  $('qualitySeverity').value = severity;
  $('qualitySeverity').addEventListener('change', event => {
    filters.quality.severity = event.target.value;
    renderAdminQuality();
  });
  $('qualityTable').innerHTML = table([
    {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
    {key:'file', label:'File', render:i=>i.file},
    {key:'row_id', label:'Row', render:i=>i.row_id},
    {key:'field', label:'Field', render:i=>i.field},
    {key:'message', label:'Message', render:i=>i.message},
    {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
  ], issueRows, 'adminQuality');
}

function renderAdminBuild() {
  const status = sourceStatus();
  const canonical = status.canonical_counts || {};
  const tuition = status.tuition || {};
  const mcat = status.mcat_gpa || {};
  const raw = status.raw_aamc_files || {};
  $('admin').innerHTML = `${adminNav()}<h2>Build Status</h2>
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
      ])}
      ${detailPanel('AAMC Tuition Source', [
        ['Parsed rows', tuition.parsed_rows],
        ['Patch candidates', tuition.patch_candidates],
        ['Safe after gap review', tuition.safe_rows_after_gap_review],
        ['Ambiguous high-confidence', tuition.ambiguous_high_confidence_rows],
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
        <h3>GPA/MCAT Sources</h3>
        ${table([
          {key:'key', label:'Source', render:r=>r.key},
          {key:'value', label:'Rows', render:r=>r.value},
        ], objectRows(mcat.source_counts), 'statusSources')}
      </div>
    </div>`;
}

function renderAdmin() {
  if (!ADMIN_ENABLED) {
    $('admin').innerHTML = '<h2>Not available</h2><p><a href="#/rankings">Back to rankings</a></p>';
    return;
  }
  if (currentRoute.path === '/admin/sources') return renderAdminSources();
  if (currentRoute.path === '/admin/data-quality') return renderAdminQuality();
  if (currentRoute.path === '/admin/build') return renderAdminBuild();
  return renderAdminOverview();
}

function render() {
  if (ensureDefaultRoute()) return;
  currentRoute = parseRoute();
  if (routeHash(currentRoute.path) !== window.location.hash && window.location.hash) {
    window.location.replace(routeHash(currentRoute.path));
    return;
  }
  $('summaryText').textContent = `${payload.meta.active_school_count} active schools · ${payload.meta.site_mode} mode`;
  setActiveNav(currentRoute.path);
  setActiveSection(currentRoute.view);
  if (currentRoute.view === 'rankings') renderRankings();
  if (currentRoute.view === 'dossiers') renderDossiers();
  if (currentRoute.view === 'research') renderResearch();
  if (currentRoute.view === 'lists') renderLists();
  if (currentRoute.view === 'listDetail') renderListDetail();
  if (currentRoute.view === 'compare') renderCompare();
  if (currentRoute.view === 'profile') renderProfile();
  if (currentRoute.view === 'methodology') renderMethodology();
  if (currentRoute.view === 'sources') renderSources();
  if (currentRoute.view === 'admin') renderAdmin();
}

window.addEventListener('hashchange', render);
$('globalSearch').addEventListener('input', render);
document.addEventListener('click', event => {
  const actionButton = event.target.closest('[data-action]');
  if (!actionButton) return;
  const action = actionButton.dataset.action;
  const id = actionButton.dataset.schoolId;
  if (!id) return;
  event.preventDefault();
  if (action === 'hide-school') {
    const reason = window.prompt('Reason for hiding this school?', 'Not a current fit');
    setSchoolVisibility(id, 'hidden', reason === null ? 'Not a current fit' : reason);
    render();
  }
  if (action === 'restore-school') {
    setSchoolVisibility(id, 'visible');
    render();
  }
});
document.addEventListener('input', event => {
  const visibilityReason = event.target.closest('[data-visibility-reason]');
  if (visibilityReason) {
    updateVisibilityReason(visibilityReason.dataset.visibilityReason, visibilityReason.value);
    return;
  }
  const dossierField = event.target.closest('[data-dossier-field]');
  if (dossierField) {
    updateDossierField(dossierField.dataset.dossierSchool, dossierField.dataset.dossierField, dossierField.value);
  }
});
document.addEventListener('change', event => {
  const dossierField = event.target.closest('[data-dossier-field]');
  if (!dossierField) return;
  updateDossierField(dossierField.dataset.dossierSchool, dossierField.dataset.dossierField, dossierField.value);
  if (currentRoute.view === 'dossiers' || currentRoute.view === 'research' || currentRoute.view === 'profile') render();
});
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


def build_site(site_mode: str = SITE_MODE_LOCAL_FULL) -> Path:
    site_mode = validate_site_mode(site_mode)
    OUT.mkdir(parents=True, exist_ok=True)
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_site_payload(site_mode=site_mode)
    write_site_json(payload, site_mode=site_mode)
    SITE_INDEX_HTML.write_text(render_site_html(payload), encoding="utf-8")
    return SITE_INDEX_HTML


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static medical school ranker site.")
    parser.add_argument(
        "--site-mode",
        choices=sorted(SITE_MODES),
        default=os.environ.get("MED_SCHOOL_SITE_MODE", SITE_MODE_LOCAL_FULL),
        help="Use local_full for local review or publish_safe for public-safe payload output.",
    )
    args = parser.parse_args()
    output = build_site(site_mode=args.site_mode)
    print(f"Wrote {output.relative_to(ROOT)} ({args.site_mode})")
