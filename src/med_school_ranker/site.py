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
    SCHOOL_DOSSIERS_CSV,
    SCHOOL_VISIBILITY_CSV,
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
    "school_visibility": SCHOOL_VISIBILITY_CSV,
    "school_dossiers": SCHOOL_DOSSIERS_CSV,
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
DEFAULT_ROUTE = "#/intake"
NODE_SCHEMA_VERSION = "site_nodes_v1"

AAMC_GRID_CAVEAT = (
    "AAMC MCAT/GPA grid context is national aggregate data for U.S. MD-granting medical "
    "school applicants and acceptees; it is not a school-specific acceptance probability."
)

PUBLIC_ROUTES = [
    {"path": "#/intake", "label": "Intake", "route_type": "public"},
    {"path": "#/rankings", "label": "Rankings", "route_type": "public"},
    {"path": "#/interested", "label": "Interested", "route_type": "public"},
    {"path": "#/applications", "label": "Applications", "route_type": "public"},
    {"path": "#/dossiers", "label": "Score Cards", "route_type": "public"},
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

PRODUCT_PUBLIC_NODE_KEYS = {
    "school_nodes",
    "school_card_nodes",
    "school_profile_nodes",
    "ranking_card_nodes",
    "compare_card_nodes",
    "list_nodes",
    "methodology_nodes",
}
ADMIN_LOCAL_NODE_KEYS = {"admin_status_nodes"}

PRODUCT_LOCAL_KEYS = {"applicant_profiles", "partner_inputs", "school_visibility", "school_dossiers"}
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


def format_currency_value(value: object) -> str:
    number = parse_number(str(value) if value is not None else "")
    if number is None or number <= 0:
        return ""
    return f"${number:,.0f}"


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
            "site_nodes",
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


def clean_node_value(value: object) -> str:
    return str(value or "").strip()


def first_present(*values: object) -> str:
    for value in values:
        text = clean_node_value(value)
        if text:
            return text
    return ""


def node_common(node_type: str, node_id: str, generated_at: str, site_mode: str) -> dict[str, object]:
    return {
        "node_schema_version": NODE_SCHEMA_VERSION,
        "node_type": node_type,
        "id": node_id,
        "generated_at": generated_at,
        "site_mode": site_mode,
        "publish_safe": site_mode == SITE_MODE_PUBLISH_SAFE,
    }


def node_bundle(
    node_type: str,
    nodes: list[dict[str, object]],
    generated_at: str,
    site_mode: str,
    source_tables: list[str],
    *,
    contains_admin_data: bool = False,
    contains_reviewer_state: bool = False,
    contains_private_derived_data: bool = False,
) -> dict[str, object]:
    return {
        "node_schema_version": NODE_SCHEMA_VERSION,
        "node_type": node_type,
        "generated_at": generated_at,
        "site_mode": site_mode,
        "source_tables": source_tables,
        "record_count": len(nodes),
        "publish_safe": site_mode == SITE_MODE_PUBLISH_SAFE,
        "contains_admin_data": contains_admin_data,
        "contains_reviewer_state": contains_reviewer_state,
        "contains_private_derived_data": contains_private_derived_data,
        "nodes": nodes,
    }


def item_school_id(item: dict[str, object]) -> str:
    school = item.get("school", {})
    if isinstance(school, dict):
        return clean_node_value(school.get("school_id"))
    return ""


def item_school_name(item: dict[str, object]) -> str:
    school = item.get("school", {})
    if isinstance(school, dict):
        return clean_node_value(school.get("school_name"))
    return ""


def source_refs_for_item(item: dict[str, object]) -> list[dict[str, str]]:
    source_refs: dict[tuple[str, str], dict[str, str]] = {}
    source_groups = [
        item.get("school", {}),
        item.get("admissions_stats", {}),
        item.get("cost_and_debt", {}),
    ]
    source_groups.extend(item.get("admissions_policies", []) if isinstance(item.get("admissions_policies"), list) else [])
    source_groups.extend(item.get("letter_requirements", []) if isinstance(item.get("letter_requirements"), list) else [])
    for row in source_groups:
        if not isinstance(row, dict):
            continue
        source_name = clean_node_value(row.get("source_name"))
        source_url = clean_node_value(row.get("source_url"))
        if not source_name and not source_url:
            continue
        key = (source_name, source_url)
        source_refs.setdefault(
            key,
            {
                "source_name": source_name or "Source",
                "source_url": source_url,
            },
        )
    return sorted(source_refs.values(), key=lambda row: (row["source_name"], row["source_url"]))


def node_missing_fields(item: dict[str, object]) -> list[str]:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    stats = item.get("admissions_stats", {}) if isinstance(item.get("admissions_stats"), dict) else {}
    cost = item.get("cost_and_debt", {}) if isinstance(item.get("cost_and_debt"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    missing_fields = []
    if not first_present(ranking.get("decision_rank"), ranking.get("overall_rank")):
        missing_fields.append("decision_rank")
    if not first_present(ranking.get("published_mcat_average"), stats.get("published_mcat_average")):
        missing_fields.append("mcat_average")
    if not first_present(ranking.get("published_gpa_average"), stats.get("published_gpa_average")):
        missing_fields.append("gpa_average")
    if not first_present(
        cost.get("estimated_coa_out_state"),
        cost.get("out_state_tuition_fees_insurance"),
        ranking.get("cost_basis"),
    ):
        missing_fields.append("cost")
    if not parse_number(clean_node_value(derived.get("admissions_policy_count"))):
        missing_fields.append("admissions_policy")
    if not parse_number(clean_node_value(derived.get("letter_requirement_count"))):
        missing_fields.append("letter_requirements")
    return missing_fields


def readiness_for_missing_fields(missing_fields: list[str]) -> str:
    if not missing_fields:
        return "ready"
    critical_missing = {"decision_rank", "mcat_average", "gpa_average"}
    if critical_missing.intersection(missing_fields):
        return "provisional"
    return "partial"


def confidence_for_item(item: dict[str, object], readiness: str) -> str:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    return first_present(ranking.get("rank_confidence"), derived.get("rank_confidence"), readiness)


def warning_chips_for_item(item: dict[str, object], missing_fields: list[str]) -> list[dict[str, str]]:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    chips = []
    if missing_fields:
        chips.append({"label": f"{len(missing_fields)} missing fields", "severity": "warn"})
    if clean_node_value(ranking.get("score_warnings")):
        chips.append({"label": "score warnings", "severity": "warn"})
    rank_confidence = first_present(ranking.get("rank_confidence"), derived.get("rank_confidence"))
    if rank_confidence in {"partial", "provisional"}:
        chips.append({"label": f"{rank_confidence} confidence", "severity": "warn"})
    if derived.get("hard_no_flag") is True:
        chips.append({"label": "hard no", "severity": "error"})
    return chips


def school_identity_summary(item: dict[str, object]) -> dict[str, str]:
    school = item.get("school", {}) if isinstance(item.get("school"), dict) else {}
    city = clean_node_value(school.get("city"))
    state = clean_node_value(school.get("state"))
    return {
        "school_id": clean_node_value(school.get("school_id")),
        "school_slug": clean_node_value(school.get("school_slug") or item.get("school_slug")),
        "display_name": clean_node_value(school.get("school_name")),
        "degree_type": clean_node_value(school.get("degree_type")),
        "campus_name": clean_node_value(school.get("campus_name")),
        "city": city,
        "state": state,
        "state_abbrev": clean_node_value(school.get("state_abbrev")),
        "region": clean_node_value(school.get("region")),
        "ownership_type": clean_node_value(school.get("ownership_type")),
        "location": ", ".join(part for part in [city, state] if part),
        "official_url": first_present(school.get("official_url"), school.get("school_url"), school.get("source_url")),
        "profile_route": clean_node_value(item.get("profile_route") or school.get("profile_route")),
    }


def build_school_node(item: dict[str, object], generated_at: str, site_mode: str) -> dict[str, object]:
    school = item.get("school", {}) if isinstance(item.get("school"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    identity = school_identity_summary(item)
    node = node_common("school", identity["school_id"], generated_at, site_mode)
    node.update(identity)
    node.update(
        {
            "route": identity["profile_route"],
            "active": clean_node_value(school.get("active_in_universe")) or "TRUE",
            "manual_exclusion_flag": clean_node_value(school.get("manual_exclusion_flag")),
            "source_confidence": first_present(
                derived.get("admissions_data_quality_band"),
                school.get("source_confidence"),
                "missing",
            ),
            "last_verified": first_present(school.get("last_verified"), school.get("updated_at")),
            "source_refs": source_refs_for_item(item),
        }
    )
    return node


def build_school_card_node(item: dict[str, object], generated_at: str, site_mode: str) -> dict[str, object]:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    stats = item.get("admissions_stats", {}) if isinstance(item.get("admissions_stats"), dict) else {}
    cost = item.get("cost_and_debt", {}) if isinstance(item.get("cost_and_debt"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    identity = school_identity_summary(item)
    missing_fields = node_missing_fields(item)
    readiness = readiness_for_missing_fields(missing_fields)
    node = node_common("school_card", identity["school_id"], generated_at, site_mode)
    node.update(
        {
            "school_id": identity["school_id"],
            "school_slug": identity["school_slug"],
            "route": identity["profile_route"],
            "identity": identity,
            "rank_summary": {
                "decision_rank": first_present(ranking.get("decision_rank"), ranking.get("overall_rank")),
                "rank_band": first_present(ranking.get("rank_band"), derived.get("rank_band")),
                "rank_confidence": first_present(ranking.get("rank_confidence"), derived.get("rank_confidence")),
                "admissions_fit_tier": first_present(
                    ranking.get("admissions_fit_tier"),
                    ranking.get("dynamic_tier"),
                    derived.get("admissions_fit_tier"),
                ),
                "application_bucket": first_present(
                    ranking.get("application_bucket"),
                    ranking.get("suggested_funnel_bucket"),
                    derived.get("application_bucket"),
                ),
            },
            "mcat_gpa_summary": {
                "mcat_average": first_present(ranking.get("published_mcat_average"), stats.get("published_mcat_average")),
                "mcat_band": first_present(ranking.get("published_mcat_band"), stats.get("published_mcat_band")),
                "gpa_average": first_present(ranking.get("published_gpa_average"), stats.get("published_gpa_average")),
                "gpa_band": first_present(ranking.get("published_gpa_band"), stats.get("published_gpa_band")),
                "aamc_rate_band": first_present(
                    ranking.get("profile_aamc_acceptance_rate_band"),
                    stats.get("aamc_acceptance_rate_band"),
                    derived.get("aamc_acceptance_rate_band"),
                ),
            },
            "cost_summary": {
                "in_state": first_present(cost.get("estimated_coa_in_state"), cost.get("in_state_tuition_fees_insurance")),
                "out_state": first_present(cost.get("estimated_coa_out_state"), cost.get("out_state_tuition_fees_insurance")),
                "cost_basis": first_present(ranking.get("cost_basis")),
            },
            "location_summary": {
                "city": identity["city"],
                "state": identity["state"],
                "region": identity["region"],
                "ownership_type": identity["ownership_type"],
            },
            "readiness": readiness,
            "confidence": confidence_for_item(item, readiness),
            "missing_fields": missing_fields,
            "warning_chips": warning_chips_for_item(item, missing_fields),
            "actions": {
                "profile_route": identity["profile_route"],
                "compare_action": "add_compare",
            },
            "source_refs": source_refs_for_item(item),
        }
    )
    return node


def build_ranking_card_node(item: dict[str, object], generated_at: str, site_mode: str) -> dict[str, object]:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    identity = school_identity_summary(item)
    missing_fields = node_missing_fields(item)
    node = node_common("ranking_card", identity["school_id"], generated_at, site_mode)
    node.update(
        {
            "school_id": identity["school_id"],
            "school_slug": identity["school_slug"],
            "route": identity["profile_route"],
            "display_name": identity["display_name"],
            "degree_type": identity["degree_type"],
            "decision_rank": first_present(ranking.get("decision_rank"), ranking.get("overall_rank")),
            "rank_band": first_present(ranking.get("rank_band"), derived.get("rank_band")),
            "rank_confidence": first_present(ranking.get("rank_confidence"), derived.get("rank_confidence")),
            "overall_school_value": clean_node_value(ranking.get("overall_school_value")),
            "admissions_score": clean_node_value(ranking.get("admissions_score")),
            "attendance_score": clean_node_value(ranking.get("attendance_score")),
            "admissions_fit_tier": first_present(
                ranking.get("admissions_fit_tier"),
                ranking.get("dynamic_tier"),
                derived.get("admissions_fit_tier"),
            ),
            "application_bucket": first_present(
                ranking.get("application_bucket"),
                ranking.get("suggested_funnel_bucket"),
                derived.get("application_bucket"),
            ),
            "top_positive_contributors": clean_node_value(
                ranking.get("top_positive_contributors") or ranking.get("top_positive_drivers")
            ),
            "top_negative_contributors": clean_node_value(
                ranking.get("top_negative_contributors") or ranking.get("top_negative_drivers")
            ),
            "missing_or_low_confidence_drivers": clean_node_value(ranking.get("missing_or_low_confidence_drivers")),
            "aamc_context_label": AAMC_GRID_CAVEAT,
            "missing_fields": missing_fields,
            "readiness": readiness_for_missing_fields(missing_fields),
        }
    )
    return node


def requirements_summary_for_item(item: dict[str, object]) -> dict[str, object]:
    policies = item.get("admissions_policies", []) if isinstance(item.get("admissions_policies"), list) else []
    letters = item.get("letter_requirements", []) if isinstance(item.get("letter_requirements"), list) else []
    policy_categories = sorted(
        {
            clean_node_value(row.get("policy_category") or row.get("policy_field"))
            for row in policies
            if isinstance(row, dict) and clean_node_value(row.get("policy_category") or row.get("policy_field"))
        }
    )
    return {
        "policy_count": len(policies),
        "letter_requirement_count": len(letters),
        "policy_categories": policy_categories,
    }


def reviewer_state_summary_for_item(item: dict[str, object]) -> dict[str, str]:
    visibility = item.get("visibility", {}) if isinstance(item.get("visibility"), dict) else {}
    dossier = item.get("dossier", {}) if isinstance(item.get("dossier"), dict) else {}
    return {
        "visibility_state": clean_node_value(visibility.get("visibility_state")) or "visible",
        "research_status": clean_node_value(dossier.get("research_status")),
        "interest_level": clean_node_value(dossier.get("interest_level")),
        "application_decision_status": clean_node_value(dossier.get("application_decision_status")),
        "four_year_happiness": clean_node_value(dossier.get("four_year_happiness")),
    }


def build_compare_card_node(item: dict[str, object], generated_at: str, site_mode: str) -> dict[str, object]:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    stats = item.get("admissions_stats", {}) if isinstance(item.get("admissions_stats"), dict) else {}
    cost = item.get("cost_and_debt", {}) if isinstance(item.get("cost_and_debt"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    identity = school_identity_summary(item)
    missing_fields = node_missing_fields(item)
    node = node_common("compare_card", identity["school_id"], generated_at, site_mode)
    node.update(
        {
            "school_id": identity["school_id"],
            "school_slug": identity["school_slug"],
            "route": identity["profile_route"],
            "identity": identity,
            "rank_fit": {
                "decision_rank": first_present(ranking.get("decision_rank"), ranking.get("overall_rank")),
                "rank_band": first_present(ranking.get("rank_band"), derived.get("rank_band")),
                "rank_confidence": first_present(ranking.get("rank_confidence"), derived.get("rank_confidence")),
                "admissions_score": clean_node_value(ranking.get("admissions_score")),
                "attendance_score": clean_node_value(ranking.get("attendance_score")),
                "admissions_fit_tier": first_present(
                    ranking.get("admissions_fit_tier"),
                    ranking.get("dynamic_tier"),
                    derived.get("admissions_fit_tier"),
                ),
            },
            "admissions_facts": {
                "mcat_average": first_present(ranking.get("published_mcat_average"), stats.get("published_mcat_average")),
                "mcat_band": first_present(ranking.get("published_mcat_band"), stats.get("published_mcat_band")),
                "gpa_average": first_present(ranking.get("published_gpa_average"), stats.get("published_gpa_average")),
                "gpa_band": first_present(ranking.get("published_gpa_band"), stats.get("published_gpa_band")),
                "aamc_rate_band": first_present(
                    ranking.get("profile_aamc_acceptance_rate_band"),
                    stats.get("aamc_acceptance_rate_band"),
                    derived.get("aamc_acceptance_rate_band"),
                ),
            },
            "cost_facts": {
                "in_state": first_present(cost.get("estimated_coa_in_state"), cost.get("in_state_tuition_fees_insurance")),
                "out_state": first_present(cost.get("estimated_coa_out_state"), cost.get("out_state_tuition_fees_insurance")),
                "cost_basis": clean_node_value(ranking.get("cost_basis")),
            },
            "requirements_summary": requirements_summary_for_item(item),
            "missing_data_summary": {
                "missing_fields": missing_fields,
                "readiness": readiness_for_missing_fields(missing_fields),
            },
        }
    )
    if site_mode == SITE_MODE_LOCAL_FULL:
        node["reviewer_state"] = reviewer_state_summary_for_item(item)
    return node


def snapshot_cards_for_item(item: dict[str, object]) -> list[dict[str, str]]:
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    stats = item.get("admissions_stats", {}) if isinstance(item.get("admissions_stats"), dict) else {}
    cost = item.get("cost_and_debt", {}) if isinstance(item.get("cost_and_debt"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    cost_basis_display = format_currency_value(ranking.get("cost_basis"))
    return [
        {
            "card_id": "decision_rank",
            "label": "Decision Rank",
            "value": first_present(ranking.get("decision_rank"), ranking.get("overall_rank"), "Unranked"),
            "context": first_present(ranking.get("rank_confidence"), derived.get("rank_confidence")),
        },
        {
            "card_id": "mcat_average",
            "label": "MCAT average",
            "value": first_present(ranking.get("published_mcat_average"), stats.get("published_mcat_average"), "Missing"),
            "context": first_present(ranking.get("published_mcat_band"), stats.get("published_mcat_band")),
        },
        {
            "card_id": "gpa_average",
            "label": "GPA average",
            "value": first_present(ranking.get("published_gpa_average"), stats.get("published_gpa_average"), "Missing"),
            "context": first_present(ranking.get("published_gpa_band"), stats.get("published_gpa_band")),
        },
        {
            "card_id": "in_state_estimated_cost",
            "label": "In-state estimated cost",
            "value": first_present(
                format_currency_value(cost.get("estimated_coa_in_state")),
                format_currency_value(cost.get("in_state_tuition_fees_insurance")),
                "Missing",
            ),
            "context": "Source-backed school cost field when available.",
        },
        {
            "card_id": "out_state_estimated_cost",
            "label": "Out-of-state estimated cost",
            "value": first_present(
                format_currency_value(cost.get("estimated_coa_out_state")),
                format_currency_value(cost.get("out_state_tuition_fees_insurance")),
                "Missing",
            ),
            "context": f"Cost used for selected score: {cost_basis_display}" if cost_basis_display else "Cost field used for selected score when available.",
        },
        {
            "card_id": "data_quality",
            "label": "Data Quality",
            "value": first_present(derived.get("admissions_data_quality_band"), "Missing"),
            "context": first_present(derived.get("rank_band")),
        },
    ]


def profile_sections_for_item(item: dict[str, object], site_mode: str) -> list[dict[str, object]]:
    identity = school_identity_summary(item)
    ranking = item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}
    stats = item.get("admissions_stats", {}) if isinstance(item.get("admissions_stats"), dict) else {}
    cost = item.get("cost_and_debt", {}) if isinstance(item.get("cost_and_debt"), dict) else {}
    derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
    sections = [
        {
            "section_id": "overview",
            "title": "Overview",
            "readiness": "ready" if identity["display_name"] else "missing",
            "facts": identity,
            "missing_fields": [] if identity["display_name"] else ["display_name"],
            "source_refs": source_refs_for_item(item),
        },
        {
            "section_id": "applicant_fit",
            "title": "Applicant Fit",
            "readiness": readiness_for_missing_fields(
                [field for field in node_missing_fields(item) if field in {"decision_rank", "mcat_average", "gpa_average"}]
            ),
            "facts": {
                "decision_rank": first_present(ranking.get("decision_rank"), ranking.get("overall_rank")),
                "admissions_score": clean_node_value(ranking.get("admissions_score")),
                "attendance_score": clean_node_value(ranking.get("attendance_score")),
                "admissions_fit_tier": first_present(
                    ranking.get("admissions_fit_tier"),
                    ranking.get("dynamic_tier"),
                    derived.get("admissions_fit_tier"),
                ),
                "aamc_context": AAMC_GRID_CAVEAT,
            },
            "missing_fields": [field for field in node_missing_fields(item) if field in {"decision_rank", "mcat_average", "gpa_average"}],
            "source_refs": [],
        },
        {
            "section_id": "admissions_stats",
            "title": "Admissions Stats",
            "readiness": "ready" if first_present(stats.get("published_mcat_average"), stats.get("published_gpa_average")) else "missing",
            "facts": {
                "mcat_average": first_present(ranking.get("published_mcat_average"), stats.get("published_mcat_average")),
                "mcat_band": first_present(ranking.get("published_mcat_band"), stats.get("published_mcat_band")),
                "gpa_average": first_present(ranking.get("published_gpa_average"), stats.get("published_gpa_average")),
                "gpa_band": first_present(ranking.get("published_gpa_band"), stats.get("published_gpa_band")),
                "data_quality_band": first_present(derived.get("admissions_data_quality_band")),
            },
            "missing_fields": [field for field in node_missing_fields(item) if field in {"mcat_average", "gpa_average"}],
            "source_refs": source_refs_for_item(item),
        },
        {
            "section_id": "cost_and_debt",
            "title": "Cost and Debt",
            "readiness": "ready" if "cost" not in node_missing_fields(item) else "missing",
            "facts": {
                "estimated_coa_in_state": clean_node_value(cost.get("estimated_coa_in_state")),
                "estimated_coa_out_state": clean_node_value(cost.get("estimated_coa_out_state")),
                "in_state_tuition_fees_insurance": clean_node_value(cost.get("in_state_tuition_fees_insurance")),
                "out_state_tuition_fees_insurance": clean_node_value(cost.get("out_state_tuition_fees_insurance")),
                "cost_basis": clean_node_value(ranking.get("cost_basis")),
            },
            "missing_fields": ["cost"] if "cost" in node_missing_fields(item) else [],
            "source_refs": source_refs_for_item(item),
        },
        {
            "section_id": "requirements",
            "title": "Requirements and Policies",
            "readiness": "ready" if requirements_summary_for_item(item)["policy_count"] or requirements_summary_for_item(item)["letter_requirement_count"] else "missing",
            "facts": requirements_summary_for_item(item),
            "missing_fields": [
                field
                for field in ["admissions_policy", "letter_requirements"]
                if field in node_missing_fields(item)
            ],
            "source_refs": source_refs_for_item(item),
        },
        {
            "section_id": "source_confidence",
            "title": "Source Confidence",
            "readiness": first_present(derived.get("rank_confidence"), "missing"),
            "facts": {
                "rank_confidence": first_present(derived.get("rank_confidence")),
                "admissions_data_quality_band": first_present(derived.get("admissions_data_quality_band")),
                "missing_fields": ", ".join(node_missing_fields(item)),
            },
            "missing_fields": node_missing_fields(item),
            "source_refs": source_refs_for_item(item),
        },
        {
            "section_id": "methodology",
            "title": "Methodology",
            "readiness": "ready",
            "facts": {
                "aamc_context": AAMC_GRID_CAVEAT,
                "weight_basis": "present_components_only",
            },
            "missing_fields": [],
            "source_refs": [],
        },
    ]
    if site_mode == SITE_MODE_LOCAL_FULL:
        sections.append(
            {
                "section_id": "reviewer_state",
                "title": "Reviewer State",
                "readiness": "partial",
                "facts": reviewer_state_summary_for_item(item),
                "missing_fields": [],
                "source_refs": [],
            }
        )
    return sections


def build_school_profile_node(item: dict[str, object], generated_at: str, site_mode: str) -> dict[str, object]:
    identity = school_identity_summary(item)
    missing_fields = node_missing_fields(item)
    node = node_common("school_profile", identity["school_id"], generated_at, site_mode)
    node.update(
        {
            "school_id": identity["school_id"],
            "school_slug": identity["school_slug"],
            "route": identity["profile_route"],
            "header": identity,
            "snapshot_cards": snapshot_cards_for_item(item),
            "sections": profile_sections_for_item(item, site_mode),
            "source_confidence": confidence_for_item(item, readiness_for_missing_fields(missing_fields)),
            "methodology_refs": ["methodology_scoring", "methodology_aamc_context"],
            "missing_fields": missing_fields,
            "readiness": readiness_for_missing_fields(missing_fields),
        }
    )
    if site_mode == SITE_MODE_LOCAL_FULL:
        derived = item.get("derived", {}) if isinstance(item.get("derived"), dict) else {}
        node["admin_refs"] = {
            "source_review_count": clean_node_value(derived.get("source_review_count")),
            "source_queue_status": clean_node_value(derived.get("source_queue_status")),
            "warning_count": clean_node_value(derived.get("warning_count")),
            "error_count": clean_node_value(derived.get("error_count")),
        }
    return node


def build_list_node(
    row: dict[str, object],
    generated_at: str,
    site_mode: str,
    ranked_school_ids: list[str],
) -> dict[str, object]:
    list_id = clean_node_value(row.get("list_id"))
    readiness = clean_node_value(row.get("readiness_label")) or "provisional"
    school_ids = ranked_school_ids[:25] if readiness in {"ready", "partial"} else []
    node = node_common("list", list_id, generated_at, site_mode)
    node.update(
        {
            "list_id": list_id,
            "slug": clean_node_value(row.get("slug")),
            "route": clean_node_value(row.get("route")),
            "title": clean_node_value(row.get("title")),
            "description": clean_node_value(row.get("description")),
            "readiness_label": readiness,
            "eligibility_summary": clean_node_value(row.get("methodology_notes")),
            "required_fields": list(row.get("required_fields", [])) if isinstance(row.get("required_fields"), list) else [],
            "missing_or_low_confidence_fields": list(row.get("missing_fields", [])) if isinstance(row.get("missing_fields"), list) else [],
            "school_ids": school_ids,
            "top_card_ids": school_ids[:10],
        }
    )
    return node


def build_methodology_nodes(
    scoring_methodology: list[dict[str, str]],
    generated_at: str,
    site_mode: str,
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in scoring_methodology:
        area = clean_node_value(row.get("methodology_area") or row.get("score_group") or "scoring")
        grouped[area].append(row)
    if not grouped:
        grouped["scoring"] = []
    nodes = []
    for area, rows in sorted(grouped.items()):
        node = node_common("methodology", f"methodology_{slugify(area)}", generated_at, site_mode)
        node.update(
            {
                "scoring_group": area,
                "formula_summary": first_present(*(row.get("formula") for row in rows), "See scoring methodology table."),
                "weight_basis": "present_components_only",
                "component_rows": rows,
                "aamc_caveat": AAMC_GRID_CAVEAT,
                "confidence_labels": ["high", "medium", "partial", "provisional", "excluded"],
                "private_public_note": "Public outputs use template/public-safe profile context; private-derived ranks stay local-only.",
            }
        )
        nodes.append(node)
    caveat_node = node_common("methodology", "methodology_aamc_context", generated_at, site_mode)
    caveat_node.update(
        {
            "scoring_group": "AAMC Context",
            "formula_summary": AAMC_GRID_CAVEAT,
            "weight_basis": "not_applicable",
            "component_rows": [],
            "aamc_caveat": AAMC_GRID_CAVEAT,
            "confidence_labels": ["national aggregate context"],
            "private_public_note": "AAMC grid values are context, not school-specific probability.",
        }
    )
    nodes.append(caveat_node)
    return nodes


def build_admin_status_node(
    status: dict[str, object],
    project_subplans: list[dict[str, str]],
    data_quality: list[dict[str, str]],
    generated_at: str,
    site_mode: str,
) -> dict[str, object]:
    plan_counts = Counter(row.get("status", "") or "unknown" for row in project_subplans)
    severity_counts = Counter(row.get("severity", "") or "unknown" for row in data_quality)
    canonical = status.get("canonical_counts", {}) if isinstance(status.get("canonical_counts"), dict) else {}
    node = node_common("admin_status", "admin_status", generated_at, site_mode)
    node.update(
        {
            "source_integration_status": {
                "source_table_count": status.get("source_table_count", 0),
                "source_diff_file_count": status.get("source_diff_file_count", 0),
                "manual_override_count": status.get("manual_override_count", 0),
            },
            "validation_counts": {
                "errors": severity_counts.get("error", 0),
                "warnings": severity_counts.get("warning", 0),
                "info": severity_counts.get("info", 0),
            },
            "source_review_counts": {
                "source_review_queue_rows": canonical.get("source_review_queue_rows", 0),
                "open_source_review_rows": canonical.get("open_source_review_rows", 0),
            },
            "raw_source_counts": status.get("raw_aamc_files", {}),
            "plan_status_counts": dict(sorted(plan_counts.items())),
            "build_metadata": {
                "generated_at": status.get("generated_at", generated_at),
                "site_mode": site_mode,
            },
        }
    )
    return node


def build_site_nodes(
    schools: list[dict[str, object]],
    curated_lists: list[dict[str, object]],
    scoring_methodology: list[dict[str, str]],
    status: dict[str, object],
    project_subplans: list[dict[str, str]],
    data_quality: list[dict[str, str]],
    generated_at: str,
    site_mode: str,
) -> dict[str, dict[str, object]]:
    sorted_schools = sorted(schools, key=lambda item: (item_school_name(item), item_school_id(item)))
    ranked_schools = sorted(
        sorted_schools,
        key=lambda item: parse_number(
            clean_node_value(
                (item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}).get("decision_rank")
                or (item.get("ranking", {}) if isinstance(item.get("ranking"), dict) else {}).get("overall_rank")
            )
        )
        or 9999,
    )
    ranked_school_ids = [item_school_id(item) for item in ranked_schools if item_school_id(item)]
    publish_safe = site_mode == SITE_MODE_PUBLISH_SAFE
    nodes: dict[str, dict[str, object]] = {
        "school_nodes": node_bundle(
            "school",
            [build_school_node(item, generated_at, site_mode) for item in sorted_schools],
            generated_at,
            site_mode,
            ["data/school_master.csv"],
        ),
        "school_card_nodes": node_bundle(
            "school_card",
            [build_school_card_node(item, generated_at, site_mode) for item in sorted_schools],
            generated_at,
            site_mode,
            ["data/school_master.csv", "outputs/calculated_rankings.csv", "data/normalized/admissions_stats.csv", "data/normalized/cost_and_debt.csv"],
        ),
        "school_profile_nodes": node_bundle(
            "school_profile",
            [build_school_profile_node(item, generated_at, site_mode) for item in sorted_schools],
            generated_at,
            site_mode,
            ["data/school_master.csv", "outputs/calculated_rankings.csv", "data/normalized/admissions_stats.csv", "data/normalized/cost_and_debt.csv", "data/normalized/admissions_policies.csv", "data/normalized/letter_requirements.csv"],
            contains_reviewer_state=not publish_safe,
        ),
        "ranking_card_nodes": node_bundle(
            "ranking_card",
            [build_ranking_card_node(item, generated_at, site_mode) for item in sorted_schools],
            generated_at,
            site_mode,
            ["outputs/calculated_rankings.csv", "outputs/score_contributions.csv"],
        ),
        "compare_card_nodes": node_bundle(
            "compare_card",
            [build_compare_card_node(item, generated_at, site_mode) for item in sorted_schools],
            generated_at,
            site_mode,
            ["data/school_master.csv", "outputs/calculated_rankings.csv", "data/normalized/admissions_stats.csv", "data/normalized/cost_and_debt.csv", "data/normalized/admissions_policies.csv", "data/normalized/letter_requirements.csv"],
            contains_reviewer_state=not publish_safe,
        ),
        "list_nodes": node_bundle(
            "list",
            [build_list_node(row, generated_at, site_mode, ranked_school_ids) for row in curated_lists],
            generated_at,
            site_mode,
            ["generated curated list definitions", "outputs/calculated_rankings.csv"],
        ),
        "methodology_nodes": node_bundle(
            "methodology",
            build_methodology_nodes(scoring_methodology, generated_at, site_mode),
            generated_at,
            site_mode,
            ["outputs/scoring_methodology.csv"],
        ),
    }
    if site_mode == SITE_MODE_LOCAL_FULL:
        nodes["admin_status_nodes"] = node_bundle(
            "admin_status",
            [build_admin_status_node(status, project_subplans, data_quality, generated_at, site_mode)],
            generated_at,
            site_mode,
            ["outputs/data_quality_report.csv", "data/project_subplans.csv", "data/manual/source_review_queue.csv"],
            contains_admin_data=True,
        )
    return nodes


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
    school_visibility = read_csv(SCHOOL_VISIBILITY_CSV)
    school_dossiers = read_csv(SCHOOL_DOSSIERS_CSV)
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
    school_visibility = with_school_route(school_visibility)
    school_dossiers = with_school_route(school_dossiers)
    source_match_overrides = with_school_route(source_match_overrides)
    source_review_queue = with_school_route(source_review_queue)
    source_queue = with_school_route(source_queue)
    data_quality = with_school_route(data_quality)

    rankings_by_school = first_by_school(rankings)
    partner_by_school = first_by_school(partner_inputs)
    visibility_by_school = first_by_school(school_visibility)
    dossier_by_school = first_by_school(school_dossiers)
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
        visibility_row = visibility_by_school.get(school_id, {})
        dossier_row = dossier_by_school.get(school_id, {})
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
            if visibility_row:
                item["visibility"] = visibility_row
            if dossier_row:
                item["dossier"] = dossier_row
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
    site_nodes = build_site_nodes(
        schools,
        curated_lists,
        scoring_methodology,
        status,
        project_subplans,
        data_quality,
        clean_node_value(status.get("generated_at")),
        site_mode,
    )
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
        "site_nodes": site_nodes,
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
                "school_visibility": school_visibility,
                "school_dossiers": school_dossiers,
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
    site_nodes = payload.get("site_nodes", {})
    if isinstance(site_nodes, dict):
        node_keys = PRODUCT_PUBLIC_NODE_KEYS | (ADMIN_LOCAL_NODE_KEYS if site_mode == SITE_MODE_LOCAL_FULL else set())
        for key in sorted(node_keys):
            if key in site_nodes:
                write_json(data_dir / "nodes" / f"{key}.json", site_nodes[key])
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
    <section id="intake" class="view"></section>
    <section id="rankings" class="view"></section>
    <section id="consideringList" class="view"></section>
    <section id="dossiers" class="view"></section>
    <section id="research" class="view"></section>
    <section id="applicationList" class="view"></section>
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
  min-width: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
}
.metric strong { display: block; font-size: 24px; color: var(--header); overflow-wrap: anywhere; }
.filters { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 12px; align-items: end; }
.selector-panel { margin: 0 0 14px; }
.selector-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 10px; }
.field-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 10px; }
.field-grid label { display: grid; gap: 4px; color: var(--muted); font-size: 12px; }
.full-span { grid-column: 1 / -1; }
.intake-layout { display: grid; grid-template-columns: minmax(280px, 380px) minmax(0, 1fr); gap: 14px; align-items: stretch; height: var(--intake-layout-height, calc(100vh - 190px)); min-height: 420px; overflow: hidden; }
.intake-form { display: grid; gap: 10px; height: 100%; min-height: 0; overflow-y: auto; overscroll-behavior: contain; scrollbar-gutter: stable; }
.intake-results { min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding-right: 2px; }
.rankings-layout { display: grid; grid-template-columns: minmax(280px, 380px) minmax(0, 1fr); gap: 14px; align-items: stretch; height: var(--rankings-layout-height, calc(100vh - 190px)); min-height: 420px; overflow: hidden; }
.rankings-menu { display: grid; gap: 10px; align-content: start; height: 100%; min-height: 0; overflow-y: auto; overscroll-behavior: contain; scrollbar-gutter: stable; }
.rankings-results { min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding-right: 2px; }
.rankings-results-header { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; align-items: center; margin-bottom: 10px; }
.hidden-schools-panel { margin-top: 14px; }
.hidden-schools-panel summary { cursor: pointer; color: var(--header); font-weight: 700; }
.intake-form fieldset { border: 1px solid var(--border); border-radius: 8px; padding: 10px; margin: 0; background: #fbfdff; }
.intake-form legend { color: var(--header); font-weight: 700; font-size: 13px; padding: 0 4px; }
.intake-check-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); gap: 6px; }
.intake-check-grid label, .checkline { display: flex; gap: 6px; align-items: center; color: #203347; font-size: 13px; }
.intake-card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 12px; }
.guided-group { margin-bottom: 14px; }
.guided-group-header { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; align-items: center; width: 100%; text-align: left; }
.guided-group-header strong { color: var(--header); }
.guided-group-header.active strong, .guided-group-header.active span { color: #fff; }
.school-review-card { display: grid; gap: 10px; min-height: 100%; min-width: 0; overflow: hidden; }
.school-review-card h3 { margin-bottom: 0; overflow-wrap: anywhere; }
.card-chip-row { display: flex; flex-wrap: wrap; gap: 6px; }
.card-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: auto; }
.card-actions select { max-width: 180px; }
.card-note { border-top: 1px solid var(--border); padding-top: 8px; }
.inline-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.compact-select { min-width: 150px; padding: 6px 8px; font-size: 12px; }
.control-stack { display: grid; gap: 6px; min-width: 170px; }
.compare-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: 12px; margin: 12px 0; }
.compare-card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 12px; min-width: 0; overflow: hidden; overflow-wrap: anywhere; }
.compare-row { display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr); gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--border); min-width: 0; }
.compare-row:last-child { border-bottom: 0; }
.compare-row strong { color: var(--header); font-size: 12px; }
.compare-row strong, .compare-row span { min-width: 0; overflow-wrap: anywhere; }
.table-wrap { overflow: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); }
table { width: 100%; border-collapse: collapse; min-width: 1100px; }
#rankTable table { min-width: 1500px; }
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
.node-card-header { display: flex; justify-content: space-between; gap: 8px; align-items: start; margin-bottom: 8px; }
.node-card-header h3 { margin: 0; overflow-wrap: anywhere; }
.node-metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 160px), 1fr)); gap: 10px; margin: 12px 0; }
.node-metric strong { display: block; font-size: 20px; color: var(--header); line-height: 1.15; overflow-wrap: anywhere; }
.node-fact-row { display: grid; grid-template-columns: minmax(0, 0.85fr) minmax(0, 1fr); gap: 10px; padding: 6px 0; border-bottom: 1px solid var(--border); min-width: 0; }
.node-fact-row:last-child { border-bottom: 0; }
.node-fact-row strong { color: var(--header); font-size: 12px; }
.node-fact-row strong, .node-fact-row span { min-width: 0; overflow-wrap: anywhere; }
.node-missing { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
.node-source-list { margin: 8px 0 0; padding-left: 18px; color: var(--muted); }
a { color: var(--accent); }
@media (max-width: 760px) {
  .app-header { display: grid; align-items: stretch; }
  .search-label { min-width: 0; }
  main { padding: 12px; }
  .intake-layout { grid-template-columns: 1fr; height: auto; min-height: 0; overflow: visible; }
  .rankings-layout { grid-template-columns: 1fr; height: auto; min-height: 0; overflow: visible; }
  .intake-form, .intake-results { height: auto; overflow: visible; }
  .rankings-menu, .rankings-results { height: auto; overflow: visible; }
  .compare-row, .node-fact-row { grid-template-columns: 1fr; gap: 2px; }
}
"""


JS = r"""
const payload = JSON.parse(document.getElementById('site-data').textContent);
const DEFAULT_ROUTE = payload.routes?.default || '#/rankings';
const ADMIN_ENABLED = (payload.routes?.admin || []).length > 0;
let currentRoute = {view: 'rankings', path: '/rankings'};
let sortState = {};
let filters = {
  rankings: {degree: '', state: '', tier: '', bucket: '', hardNo: '', excluded: '', warnings: '', quality: '', mcatBand: '', gpaBand: '', aamcRateBand: '', missingScore: '', scoreWarning: ''},
  consideringList: {visibility: 'visible', degree: 'MD', tier: '', rankBand: '', interest: '', maxRank: ''},
  dossiers: {visibility: 'visible', status: '', missing: '', tier: '', rankBand: ''},
  research: {visibility: 'visible', status: '', tier: '', rankBand: '', action: ''},
  applicationList: {visibility: 'visible', degree: 'MD', status: 'active', tier: '', rankBand: '', interest: '', priority: '', maxRank: ''},
  sources: {sourceMissing: ''},
  quality: {severity: ''},
};
let selectorState = {
  mcatBand: '',
  gpaBand: '',
  applicantState: '',
};
let compareState = {
  selectedIds: [],
};
let visibilityState = {};
let dossierState = {};
let intakeState = null;
let guidedGroupOpenState = {};
let lastRenderedPath = '';

const INTAKE_STORAGE_KEY = 'med_school_ranker_intake_v1';
const INTAKE_DISCLOSURE_STORAGE_KEY = 'med_school_ranker_guided_groups_v1';
const INTAKE_SCHEMA_VERSION = 'guided_intake_v1';
const INTAKE_STATE_HIDE_PREFIX = 'Intake state avoid: ';
const GUIDED_GROUPS = [
  {id: 'start_here', label: 'Start Here', defaultOpen: true},
  {id: 'florida_options', label: 'Florida Options', defaultOpen: true},
  {id: 'reach_schools_to_research', label: 'Reach Schools To Research', defaultOpen: true},
  {id: 'compare_next', label: 'Compare Next', defaultOpen: true},
  {id: 'need_more_data', label: 'Need More Data', defaultOpen: false},
  {id: 'lower_priority_or_hidden', label: 'Lower Priority Or Hidden', defaultOpen: false},
];
const STRATEGY_OPTIONS = ['safer_list', 'balanced_list', 'reach_heavy_list'];
const STRATEGY_DETAILS = {
  safer_list: {
    label: 'More Likely Schools',
    summary: 'Prioritizes schools where the applicant profile appears more realistic before adding many reaches.',
    changes: 'Smaller first review set, more conservative compare set, fewer reach schools in the early pass.',
  },
  balanced_list: {
    label: 'Balanced Mix',
    summary: 'Keeps a practical blend of likely, target, and reach schools for the first serious review.',
    changes: 'Uses the target application count as the main review size and keeps a moderate reach buffer.',
  },
  reach_heavy_list: {
    label: 'More Reach Schools',
    summary: 'Keeps more high-upside schools visible for research before narrowing to the final list.',
    changes: 'Larger first review set, larger reach buffer, and more schools promoted into compare/research.',
  },
};

const VISIBILITY_EXPORT_HEADERS = ['export_schema_version', 'exported_at', 'school_id', 'school_name', 'visibility_state', 'visibility_reason', 'hidden_at', 'updated_at', 'source', 'notes'];
const DOSSIER_EXPORT_HEADERS = ['export_schema_version', 'exported_at', 'school_id', 'school_name', 'research_status', 'interest_level', 'four_year_happiness', 'location_fit', 'culture_fit', 'regret_index', 'hard_no_flag', 'hard_no_reason', 'application_decision_status', 'notes'];
const APPLICATION_EXPORT_HEADERS = ['school_id', 'school_name', 'degree_type', 'city', 'state', 'current_bucket', 'status', 'why_kept', 'why_cut', 'assigned_research_owner', 'next_action', 'priority', 'application_service', 'primary_deadline', 'secondary_fee', 'submitted_primary', 'secondary_received', 'secondary_submitted', 'interview_invite', 'decision', 'notes'];
const DOSSIER_FIELDS = DOSSIER_EXPORT_HEADERS.filter(field => !['export_schema_version', 'exported_at', 'school_id', 'school_name'].includes(field));
const RESEARCH_STATUSES = ['not_started', 'skimmed', 'needs_deep_research', 'researched', 'ready_to_decide', 'excluded', 'applied'];
const INTEREST_LEVELS = ['high', 'medium', 'low', 'none'];
const DECISION_STATUSES = ['interested', 'applying'];
const APPLICATION_INTERESTED_STATUSES = ['interested', 'considering'];
const APPLICATION_APPLYING_STATUSES = ['applying'];
const APPLICATION_ACTIVE_STATUSES = ['interested', 'considering', 'applying', 'applied', 'interview', 'accepted', 'waitlisted'];
const APPLICATION_EXCLUDED_STATUSES = ['rejected', 'withdrawn', 'not_applying'];
const INTERESTED_LIMIT = 50;
const APPLYING_LIMIT = 25;

const $ = (id) => document.getElementById(id);
const rows = (key) => Array.isArray(payload[key]) ? payload[key] : [];
function getNodeFamilies(payload) {
  return payload?.site_nodes || {};
}

function nodeFamilyNodes(familyName) {
  const family = getNodeFamilies(payload)[familyName];
  return Array.isArray(family?.nodes) ? family.nodes : [];
}

function indexNodesById(nodes) {
  return Object.fromEntries((nodes || [])
    .filter(node => node && (node.school_id || node.id))
    .map(node => [node.school_id || node.id, node]));
}

function indexNodesBySlug(nodes) {
  return Object.fromEntries((nodes || [])
    .filter(node => node && node.school_slug)
    .map(node => [node.school_slug, node]));
}

const nodeFamilies = getNodeFamilies(payload);
const schoolNodesById = indexNodesById(nodeFamilyNodes('school_nodes'));
const schoolProfileNodesById = indexNodesById(nodeFamilyNodes('school_profile_nodes'));
const schoolProfileNodesBySlug = indexNodesBySlug(nodeFamilyNodes('school_profile_nodes'));
const schoolCardNodesById = indexNodesById(nodeFamilyNodes('school_card_nodes'));
const rankingCardNodesById = indexNodesById(nodeFamilyNodes('ranking_card_nodes'));
const compareCardNodesById = indexNodesById(nodeFamilyNodes('compare_card_nodes'));

function getSchoolProfileNode(schoolIdOrSlug) {
  return schoolProfileNodesById[schoolIdOrSlug] || schoolProfileNodesBySlug[schoolIdOrSlug] || null;
}

function getSchoolCardNode(schoolId) {
  return schoolCardNodesById[schoolId] || null;
}

function getRankingCardNode(schoolId) {
  return rankingCardNodesById[schoolId] || null;
}

function getCompareCardNode(schoolId) {
  return compareCardNodesById[schoolId] || null;
}

visibilityState = Object.fromEntries(rows('school_visibility')
  .filter(record => record.school_id)
  .map(record => [record.school_id, {
    export_schema_version: 'school_visibility_v1',
    school_id: record.school_id,
    school_name: record.school_name || '',
    visibility_state: record.visibility_state || 'visible',
    visibility_reason: record.visibility_reason || '',
    hidden_at: record.hidden_at || '',
    updated_at: record.updated_at || '',
    source: record.source || 'manual/school_visibility.csv',
    notes: record.notes || '',
  }]));
dossierState = Object.fromEntries(rows('school_dossiers')
  .filter(record => record.school_id)
  .map(record => [record.school_id, {
    school_id: record.school_id,
    school_name: record.school_name || '',
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
    updated_at: record.updated_at || '',
    source: record.source || 'manual/school_dossiers.csv',
  }]));
intakeState = loadIntakeState();
guidedGroupOpenState = loadGuidedGroupOpenState();
syncSelectorFromIntake();
syncStateAvoidVisibility();
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
  if (path === '/intake') return {view: 'intake', path};
  if (path === '/rankings') return {view: 'rankings', path};
  if (path === '/interested' || path === '/considering') return {view: 'consideringList', path};
  if (path === '/dossiers') return {view: 'dossiers', path};
  if (path === '/research') return {view: 'research', path};
  if (path === '/applications' || path === '/application-list') return {view: 'applicationList', path};
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
      || (path === '/considering' && navPath === '/interested')
      || (path === '/application-list' && navPath === '/applications')
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
  return `<span class="badge ${type}">${safeText(missing(text))}</span>`;
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

const FIELD_LABELS = {
  admissions_data_quality_band: 'Admissions data quality band',
  admissions_fit_tier: 'Admissions fit tier',
  admissions_score: 'Admissions score',
  aamc_context: 'AAMC context',
  aamc_rate_band: 'AAMC acceptance-rate band',
  application_bucket: 'Application bucket',
  attendance_score: 'Attendance score',
  cost_basis: 'Cost used for selected score',
  data_quality_band: 'Data quality band',
  decision_rank: 'Decision Rank',
  estimated_coa_in_state: 'In-state estimated cost',
  estimated_coa_out_state: 'Out-of-state estimated cost',
  gpa_average: 'GPA average',
  gpa_band: 'GPA band',
  in_state: 'In-state estimated cost',
  in_state_tuition_fees_insurance: 'In-state tuition, fees, and insurance',
  mcat_average: 'MCAT average',
  mcat_band: 'MCAT band',
  missing_fields: 'Missing fields',
  out_state: 'Out-of-state estimated cost',
  out_state_tuition_fees_insurance: 'Out-of-state tuition, fees, and insurance',
  rank_band: 'Rank band',
  rank_confidence: 'Rank confidence',
};

function labelize(value) {
  const text = String(value || '').trim();
  if (!text) return 'Unselected';
  if (STRATEGY_DETAILS[text]) return STRATEGY_DETAILS[text].label;
  if (FIELD_LABELS[text]) return FIELD_LABELS[text];
  return text.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function isCurrencyFieldKey(key) {
  return [
    'cost',
    'coa',
    'tuition',
    'debt',
    'in_state',
    'out_state',
  ].some(part => String(key || '').toLowerCase().includes(part));
}

function formatCurrency(value) {
  const number = parseScore(value);
  if (number === null || number <= 0) return 'Missing';
  return `$${Math.round(number).toLocaleString()}`;
}

function firstPositiveNumber(...values) {
  for (const value of values) {
    const number = parseScore(value);
    if (number !== null && number > 0) return number;
  }
  return null;
}

function nodeDisplayValueForKey(key, value) {
  if (isCurrencyFieldKey(key)) return safeText(formatCurrency(value));
  return nodeDisplayValue(value);
}

function safeLocalRead(key) {
  try {
    return window.localStorage?.getItem(key) || '';
  } catch {
    return '';
  }
}

function safeLocalWrite(key, value) {
  try {
    window.localStorage?.setItem(key, value);
  } catch {
    // Local storage can be unavailable in private windows or locked-down browsers.
  }
}

function safeLocalRemove(key) {
  try {
    window.localStorage?.removeItem(key);
  } catch {
    // Local storage can be unavailable in private windows or locked-down browsers.
  }
}

function schoolStateOptions() {
  return unique(rows('schools').map(item => item.school.state_abbrev || item.ranking.state_abbrev)).sort();
}

function mcatBandOptions() {
  return unique(rows('aamc_mcat_gpa_grid').map(row => row.mcat_band));
}

function gpaBandOptions() {
  return unique(rows('aamc_mcat_gpa_grid').map(row => row.gpa_band));
}

function defaultIntakeState() {
  const states = schoolStateOptions();
  return {
    schema_version: INTAKE_SCHEMA_VERSION,
    degree_goal: 'md_only',
    applicant_state: states.includes('FL') ? 'FL' : '',
    mcat_band: '',
    gpa_band: '',
    application_strategy: 'balanced_list',
    target_application_count: '25',
    include_reach_schools: 'yes',
    urbanicity_preference: 'urban_preferred',
    cost_sensitivity: 'medium',
    states_to_avoid: [],
    career_optionality: 'em_leaning',
    school_environment_preferences: [],
    dealbreakers: [],
    updated_at: '',
  };
}

function arrayValue(value) {
  return Array.isArray(value) ? value.map(String).filter(Boolean) : [];
}

function normalizeIntakeState(raw) {
  const defaults = defaultIntakeState();
  const parsed = raw && typeof raw === 'object' ? raw : {};
  const normalized = {...defaults, ...parsed, schema_version: INTAKE_SCHEMA_VERSION};
  normalized.states_to_avoid = arrayValue(parsed.states_to_avoid);
  normalized.school_environment_preferences = arrayValue(parsed.school_environment_preferences);
  normalized.dealbreakers = arrayValue(parsed.dealbreakers);
  if (!['md_only'].includes(normalized.degree_goal)) normalized.degree_goal = defaults.degree_goal;
  if (!STRATEGY_OPTIONS.includes(normalized.application_strategy)) normalized.application_strategy = defaults.application_strategy;
  if (!['15', '20', '25', '30', '35'].includes(String(normalized.target_application_count))) normalized.target_application_count = defaults.target_application_count;
  if (!['yes', 'no'].includes(normalized.include_reach_schools)) normalized.include_reach_schools = defaults.include_reach_schools;
  if (!['urban_preferred', 'suburban_ok', 'rural_ok', 'no_preference'].includes(normalized.urbanicity_preference)) normalized.urbanicity_preference = defaults.urbanicity_preference;
  if (!['low', 'medium', 'high', 'debt_averse'].includes(normalized.cost_sensitivity)) normalized.cost_sensitivity = defaults.cost_sensitivity;
  if (!['undecided', 'em_leaning', 'competitive_optionality', 'academic_research'].includes(normalized.career_optionality)) normalized.career_optionality = defaults.career_optionality;
  return normalized;
}

function loadIntakeState() {
  const stored = safeLocalRead(INTAKE_STORAGE_KEY);
  if (!stored) return normalizeIntakeState({});
  try {
    return normalizeIntakeState(JSON.parse(stored));
  } catch {
    return normalizeIntakeState({});
  }
}

function persistIntakeState() {
  if (!intakeState) return;
  intakeState.updated_at = nowIso();
  safeLocalWrite(INTAKE_STORAGE_KEY, JSON.stringify(intakeState));
}

function loadGuidedGroupOpenState() {
  const defaults = Object.fromEntries(GUIDED_GROUPS.map(group => [group.id, group.defaultOpen]));
  const stored = safeLocalRead(INTAKE_DISCLOSURE_STORAGE_KEY);
  if (!stored) return defaults;
  try {
    return {...defaults, ...JSON.parse(stored)};
  } catch {
    return defaults;
  }
}

function persistGuidedGroupOpenState() {
  safeLocalWrite(INTAKE_DISCLOSURE_STORAGE_KEY, JSON.stringify(guidedGroupOpenState));
}

function clearIntakeStateAvoidVisibility() {
  rows('schools').forEach(item => {
    const current = visibilityFor(item);
    const reason = String(current.visibility_reason || '');
    if (current.visibility_state === 'hidden' && reason.startsWith(INTAKE_STATE_HIDE_PREFIX)) {
      setSchoolVisibility(schoolId(item), 'visible', 'Intake reset');
    }
  });
}

function resetIntakeState() {
  clearIntakeStateAvoidVisibility();
  safeLocalRemove(INTAKE_STORAGE_KEY);
  safeLocalRemove(INTAKE_DISCLOSURE_STORAGE_KEY);
  intakeState = normalizeIntakeState({});
  guidedGroupOpenState = loadGuidedGroupOpenState();
  syncSelectorFromIntake();
}

function syncSelectorFromIntake() {
  if (!intakeState) return;
  selectorState.mcatBand = intakeState.mcat_band || '';
  selectorState.gpaBand = intakeState.gpa_band || '';
  selectorState.applicantState = intakeState.applicant_state || '';
}

function intakeReady() {
  if (!intakeState) return false;
  return Boolean(
    intakeState.degree_goal
    && intakeState.applicant_state
    && intakeState.mcat_band
    && intakeState.gpa_band
    && intakeState.application_strategy
    && intakeState.target_application_count
    && intakeState.urbanicity_preference
    && intakeState.cost_sensitivity
  );
}

function setIntakeField(field, value) {
  if (!intakeState) intakeState = normalizeIntakeState({});
  intakeState[field] = value;
  if (field === 'applicant_state') {
    intakeState.states_to_avoid = arrayValue(intakeState.states_to_avoid).filter(state => state !== value);
  }
  persistIntakeState();
  syncSelectorFromIntake();
  if (field === 'states_to_avoid' || field === 'applicant_state') syncStateAvoidVisibility();
}

function toggleIntakeArrayField(field, value, checked) {
  if (!intakeState) intakeState = normalizeIntakeState({});
  const current = new Set(arrayValue(intakeState[field]));
  if (checked) current.add(value);
  else current.delete(value);
  setIntakeField(field, [...current].sort());
}

function syncStateAvoidVisibility() {
  if (!intakeState) return;
  const avoided = new Set(arrayValue(intakeState.states_to_avoid));
  rows('schools').forEach(item => {
    if (item.school.degree_type !== 'MD') return;
    const id = schoolId(item);
    const state = schoolState(item);
    const current = visibilityFor(item);
    const reason = String(current.visibility_reason || '');
    if (state && avoided.has(state)) {
      setSchoolVisibility(id, 'hidden', `${INTAKE_STATE_HIDE_PREFIX}${state}`);
      return;
    }
    if (current.visibility_state === 'hidden' && reason.startsWith(INTAKE_STATE_HIDE_PREFIX)) {
      setSchoolVisibility(id, 'visible', 'Intake state avoid cleared');
    }
  });
}

function intakeExportRecord() {
  const grouped = intakeReady() ? guidedRowsByGroup() : {};
  return {
    export_schema_version: INTAKE_SCHEMA_VERSION,
    exported_at: nowIso(),
    privacy_label: 'browser_local_user_answers',
    answers: intakeState,
    selected_context: selectedAssumptionRecords()[0],
    group_counts: Object.fromEntries(GUIDED_GROUPS.map(group => [group.label, (grouped[group.id] || []).length])),
    caveat: payload.copy.aamc_grid_caveat,
  };
}

function nodeDisplayValue(value) {
  if (Array.isArray(value)) {
    const text = value.filter(part => part !== undefined && part !== null && String(part).trim() !== '').join(', ');
    return safeText(missing(text));
  }
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (value && typeof value === 'object') return safeText(JSON.stringify(value));
  return safeText(missing(value));
}

function nodeStatusChip(value) {
  const text = String(value || '').trim();
  const type = ['ready', 'partial', 'provisional', 'missing', 'high', 'medium', 'low'].includes(text) ? text : '';
  return badge(text || 'missing', type);
}

function renderCardShell(title, body, meta='') {
  return `<div class="panel">
    <div class="node-card-header"><h3>${safeText(title)}</h3>${meta || ''}</div>
    ${body}
  </div>`;
}

function renderMetricCard(card) {
  return `<div class="panel node-metric">
    <span class="muted">${safeText(card?.label || card?.card_id || 'Metric')}</span>
    <strong>${nodeDisplayValue(card?.value)}</strong>
    ${card?.context ? `<p>${safeText(card.context)}</p>` : ''}
  </div>`;
}

function renderFactRows(facts) {
  const entries = Object.entries(facts || {}).filter(([key]) => key !== 'source_refs');
  if (!entries.length) return '<div class="empty-state">No facts available in this node section.</div>';
  return entries.map(([key, value]) => `<div class="node-fact-row"><strong>${safeText(labelize(key))}</strong><span>${nodeDisplayValueForKey(key, value)}</span></div>`).join('');
}

function renderMissingFieldsBlock(missingFields) {
  const fields = Array.isArray(missingFields) ? missingFields.filter(Boolean) : [];
  if (!fields.length) return '';
  return `<div class="node-missing">${fields.map(field => badge(labelize(field), 'warn')).join('')}</div>`;
}

function renderSourceCaveatBlock(sourceRefs) {
  const refs = Array.isArray(sourceRefs) ? sourceRefs.filter(ref => ref?.source_name || ref?.source_url) : [];
  if (!refs.length) return '';
  return `<ul class="node-source-list">${refs.slice(0, 5).map(ref => {
    const label = safeText(ref.source_name || 'Source');
    return `<li>${ref.source_url ? `<a href="${attr(ref.source_url)}" target="_blank">${label}</a>` : label}</li>`;
  }).join('')}</ul>`;
}

function renderProfileSectionBlock(section) {
  return renderCardShell(
    section?.title || section?.section_id || 'Profile Section',
    `${renderFactRows(section?.facts || {})}
     ${renderMissingFieldsBlock(section?.missing_fields)}
     ${renderSourceCaveatBlock(section?.source_refs)}`,
    nodeStatusChip(section?.readiness)
  );
}

function renderSchoolCardNodePreview(schoolId) {
  const schoolCard = getSchoolCardNode(schoolId);
  const rankingCard = getRankingCardNode(schoolId);
  if (!schoolCard && !rankingCard) return '';
  const schoolRows = schoolCard ? [
    ['Readiness', schoolCard.readiness],
    ['Confidence', schoolCard.confidence],
    ['Application bucket', schoolCard.rank_summary?.application_bucket],
    ['MCAT and GPA', [schoolCard.mcat_gpa_summary?.mcat_average, schoolCard.mcat_gpa_summary?.gpa_average].filter(Boolean).join(' / ')],
    ['Cost used for selected score', formatCurrency(schoolCard.cost_summary?.cost_basis)],
    ['In-state estimated cost', formatCurrency(schoolCard.cost_summary?.in_state)],
    ['Out-of-state estimated cost', formatCurrency(schoolCard.cost_summary?.out_state)],
  ] : [];
  const rankingRows = rankingCard ? [
    ['Decision rank', rankingCard.decision_rank],
    ['Rank band', rankingCard.rank_band],
    ['Admissions score', rankingCard.admissions_score],
    ['Attendance score', rankingCard.attendance_score],
    ['Positive contributors', rankingCard.top_positive_contributors],
    ['Low-confidence drivers', rankingCard.missing_or_low_confidence_drivers],
  ] : [];
  return `<div class="detail-grid" style="margin-top:12px">
    ${schoolCard ? detailPanel('School Summary', schoolRows) : ''}
    ${rankingCard ? detailPanel('Ranking Summary', rankingRows) : ''}
  </div>`;
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
    const previous = visibilityState[id] || {};
    if (!previous.visibility_state || previous.visibility_state === 'visible') {
      delete visibilityState[id];
      return;
    }
    visibilityState[id] = {
      export_schema_version: 'school_visibility_v1',
      school_id: id,
      school_name: item.school.school_name || previous.school_name || '',
      visibility_state: 'visible',
      visibility_reason: reason || previous.visibility_reason || '',
      hidden_at: previous.hidden_at || '',
      updated_at: nowIso(),
      source: 'browser_session',
      notes: previous.notes || '',
    };
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
  record.updated_at = nowIso();
  record.source = 'browser_session';
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
  if (!dossier.research_status) return 'Start score card';
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
    if (value !== null && value > 0) return value;
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

function activeMdSchools(options={}) {
  const includeHidden = options.includeHidden === true;
  return filteredSchools().filter(item => (
    item.school.degree_type === 'MD'
    && !truthy(item.school.manual_exclusion_flag)
    && !truthy(item.ranking.excluded_from_rank)
    && (includeHidden || !isSchoolHidden(item))
  ));
}

function selectorRankedRows(options={}) {
  const mdRows = activeMdSchools(options);
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

function downloadJson(filename, record) {
  const blob = new Blob([JSON.stringify(record, null, 2) + '\n'], {type: 'application/json'});
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

function dossierInlineSelect(item, field, values, label='') {
  const id = schoolId(item);
  const dossier = dossierFor(item);
  const title = label ? ` title="${attr(label)}"` : '';
  return `<select class="compact-select" data-dossier-school="${attr(id)}" data-dossier-field="${attr(field)}"${title}>${labeledOptions(values, dossier[field])}</select>`;
}

function dossierInlineScoreSelect(item, field, label='') {
  const id = schoolId(item);
  const dossier = dossierFor(item);
  const title = label ? ` title="${attr(label)}"` : '';
  return `<select class="compact-select" data-dossier-school="${attr(id)}" data-dossier-field="${attr(field)}"${title}>${scoreOptions(dossier[field])}</select>`;
}

function setApplicationStatus(id, status) {
  updateDossierField(id, 'application_decision_status', status);
}

function applicationStatusBadge(item) {
  const status = applicationStatusFor(item);
  if (APPLICATION_INTERESTED_STATUSES.includes(status)) return badge('Interested', 'good');
  if (APPLICATION_APPLYING_STATUSES.includes(status)) return badge('Applying', 'good');
  if (status && status !== 'unselected') return badge(labelize(status), '');
  return badge('Not listed', '');
}

function applicationStatusButton(item, status, label) {
  const current = applicationStatusFor(item);
  const active = (status === 'interested' && APPLICATION_INTERESTED_STATUSES.includes(current))
    || (status === 'applying' && APPLICATION_APPLYING_STATUSES.includes(current))
    || current === status;
  if (active) return badge(label, 'good');
  const counts = applicationStatusCounts();
  if (status === 'interested' && counts.interested >= INTERESTED_LIMIT) return `<button type="button" disabled title="Remove a school from Interested before adding another.">${safeText(label)}</button>`;
  if (status === 'applying' && counts.applying >= APPLYING_LIMIT) return `<button type="button" disabled title="Remove a school from Applying before adding another.">${safeText(label)}</button>`;
  return `<button type="button" data-action="set-application-status" data-school-id="${attr(schoolId(item))}" data-application-status="${attr(status)}">${safeText(label)}</button>`;
}

function removeFromApplicationListButton(item, label='None') {
  return `<button type="button" data-action="set-application-status" data-school-id="${attr(schoolId(item))}" data-application-status="">${safeText(label)}</button>`;
}

function statusSwitchActions(item) {
  return `<div class="inline-actions">${applicationStatusButton(item, 'interested', 'Interested')}${applicationStatusButton(item, 'applying', 'Applying')}${removeFromApplicationListButton(item, 'None')}</div>`;
}

function interestControl(item) {
  return dossierInlineSelect(item, 'interest_level', INTEREST_LEVELS, 'Interest level');
}

function researchStatusControl(item) {
  return dossierInlineSelect(item, 'research_status', RESEARCH_STATUSES, 'Research status');
}

function selectedCompareItems() {
  return compareState.selectedIds
    .map(id => schoolById(id))
    .filter(Boolean);
}

function isCompareSelected(item) {
  return compareState.selectedIds.includes(schoolId(item));
}

function setCompareSelected(id, selected) {
  const current = compareState.selectedIds.filter(existing => existing !== id);
  if (selected && current.length < 4) current.push(id);
  compareState.selectedIds = current;
}

function compareButton(item) {
  const id = schoolId(item);
  const selected = isCompareSelected(item);
  const disabled = !selected && compareState.selectedIds.length >= 4 ? ' disabled title="Compare is limited to 4 schools"' : '';
  return `<button type="button" data-action="${selected ? 'remove-compare' : 'add-compare'}" data-school-id="${attr(id)}"${disabled}>${selected ? 'Remove Compare' : 'Compare'}</button>`;
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
      <label>Warnings <select id="rankWarnings"><option value="" ${f.warnings === '' ? 'selected' : ''}>All</option><option value="yes" ${f.warnings === 'yes' ? 'selected' : ''}>Has warnings</option><option value="no" ${f.warnings === 'no' ? 'selected' : ''}>No warnings</option></select></label>` : '';
  return `
    <div class="field-grid">
      <label>Degree <select id="rankDegree"><option value="" ${f.degree === '' ? 'selected' : ''}>All</option>${optionTags(degrees, f.degree)}</select></label>
      <label>State <select id="rankState"><option value="" ${f.state === '' ? 'selected' : ''}>All</option>${optionTags(states, f.state)}</select></label>
      <label>Tier <select id="rankTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
      <label>Bucket <select id="rankBucket"><option value="" ${f.bucket === '' ? 'selected' : ''}>All</option>${optionTags(buckets, f.bucket)}</select></label>
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
  const {degree, state, tier, bucket, hardNo, excluded, warnings, quality, mcatBand, gpaBand, aamcRateBand, missingScore, scoreWarning} = filters.rankings;
  return filteredSchools().filter(s => {
    if (degree && s.school.degree_type !== degree) return false;
    if (state && s.school.state !== state) return false;
    if (tier && s.derived.admissions_fit_tier !== tier) return false;
    if (bucket && s.derived.application_bucket !== bucket) return false;
    if (isSchoolHidden(s)) return false;
    if (ADMIN_ENABLED && hardNo === 'yes' && !s.derived.hard_no_flag) return false;
    if (ADMIN_ENABLED && hardNo === 'no' && s.derived.hard_no_flag) return false;
    if (ADMIN_ENABLED && excluded === 'yes' && !s.derived.excluded_from_rank) return false;
    if (ADMIN_ENABLED && excluded === 'no' && s.derived.excluded_from_rank) return false;
    if (ADMIN_ENABLED && warnings === 'yes' && s.derived.warning_count < 1) return false;
    if (ADMIN_ENABLED && warnings === 'no' && s.derived.warning_count > 0) return false;
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
  return `<fieldset class="selector-panel">
      <legend>MD Band Selector</legend>
      <div class="caveat">MD-only proof of concept. DO schools are excluded from this interactive reranking view. Selected-profile rankings stay in browser memory and are not written back.</div>
      <div class="field-grid">
        <label>MCAT Band <select id="selectorMcatBand"><option value="" ${selectorState.mcatBand === '' ? 'selected' : ''}>Unselected</option>${optionTags(mcatBands, selectorState.mcatBand)}</select></label>
        <label>GPA Band <select id="selectorGpaBand"><option value="" ${selectorState.gpaBand === '' ? 'selected' : ''}>Unselected</option>${optionTags(gpaBands, selectorState.gpaBand)}</select></label>
        <label>Applicant State <select id="selectorApplicantState"><option value="" ${selectorState.applicantState === '' ? 'selected' : ''}>Unselected</option>${optionTags(states, selectorState.applicantState)}</select></label>
      </div>
      <div class="selector-actions">
        <button type="button" id="downloadSelectorAssumptions">Download Assumptions CSV</button>
        <button type="button" id="downloadSelectorRows" ${ready ? '' : 'disabled title="Select all assumptions first"'}>Download Current MD Ranking CSV</button>
        ${badge('local/private-derived', 'warn')}
        <span class="muted">${selectorStatus}</span>
      </div>
      <div id="mdSelectorTable"></div>
    </fieldset>`;
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
    {key:'selector.oos', label:'Out-of-state fit', render:r=>r.overrides.admissions_oos_friendliness_score === undefined ? 'Missing' : r.overrides.admissions_oos_friendliness_score.toFixed(1)},
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

function renderHiddenSchoolsPanel() {
  const hidden = hiddenSchools();
  const hiddenTable = hidden.length ? table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'visibility.visibility_reason', label:'Reason', render:s=>`<input data-visibility-reason="${attr(schoolId(s))}" value="${attr(visibilityFor(s).visibility_reason)}" placeholder="Why hidden">`},
    {key:'visibility.hidden_at', label:'Hidden At', render:s=>missing(visibilityFor(s).hidden_at)},
    {key:'actions', label:'Actions', render:s=>`<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(s))}">Restore</button>`},
  ], hidden, 'hiddenSchools') : '<div class="empty-state">No schools are hidden in this browser session.</div>';
  return `<details class="panel hidden-schools-panel">
    <summary>Hidden Schools ${badge(`${hidden.length} hidden`, hidden.length ? 'warn' : 'good')}</summary>
    <div class="inline-actions" style="margin-top:10px">
      <button type="button" id="downloadVisibilityExport">Download Visibility CSV</button>
    </div>
    <p>Visibility is local to this browser session. Export the CSV before closing the page if you want to preserve hide/restore decisions.</p>
    <div style="margin-top:10px">${hiddenTable}</div>
  </details>`;
}

function intakeSelect(field, label, values, selected=intakeState?.[field] || '') {
  const selectedValue = String(selected || '');
  const optionValues = values.includes('') ? values : [''].concat(values);
  const options = optionValues.map(value => `<option value="${attr(value)}" ${value === selectedValue ? 'selected' : ''}>${value ? safeText(labelize(value)) : 'Unselected'}</option>`).join('');
  return `<label>${safeText(label)}<select data-intake-field="${attr(field)}">${options}</select></label>`;
}

function intakeCheckboxGroup(field, values, selectedValues) {
  const selected = new Set(arrayValue(selectedValues));
  if (!values.length) return '<div class="empty-state">No options available from the current data.</div>';
  return `<div class="intake-check-grid">${values.map(value => `<label><input type="checkbox" data-intake-multi="${attr(field)}" value="${attr(value)}" ${selected.has(value) ? 'checked' : ''}>${safeText(value)}</label>`).join('')}</div>`;
}

function intakeDisclosureGroup(field, values, selectedValues) {
  const selected = new Set(arrayValue(selectedValues));
  return `<div class="intake-check-grid">${values.map(value => `<label class="checkline"><input type="checkbox" data-intake-multi="${attr(field)}" value="${attr(value)}" ${selected.has(value) ? 'checked' : ''}>${safeText(labelize(value))}</label>`).join('')}</div>`;
}

function intakeSummaryChips() {
  if (!intakeState) return '';
  const chips = [
    'MD only',
    `${intakeState.applicant_state || 'No state'} applicant`,
    `${intakeState.mcat_band || 'No MCAT band'} MCAT`,
    `${intakeState.gpa_band || 'No GPA band'} GPA`,
    labelize(intakeState.application_strategy),
    `${intakeState.target_application_count} target apps`,
    labelize(intakeState.urbanicity_preference),
    `${labelize(intakeState.cost_sensitivity)} cost sensitivity`,
  ];
  if (intakeState.states_to_avoid.length) chips.push(`Avoiding ${intakeState.states_to_avoid.join(', ')}`);
  return `<div class="card-chip-row">${chips.map(text => badge(text)).join('')}</div>`;
}

function renderIntakeMenu() {
  const states = schoolStateOptions();
  const stateAvoidOptions = states.filter(state => state !== intakeState.applicant_state);
  return `<div class="panel intake-form">
    <div>
      <h3>Build A Review List</h3>
      <p>Answers stay in this browser and change the review lens, not the source CSVs.</p>
    </div>
    <fieldset>
      <legend>Academic Context</legend>
      <div class="field-grid">
        ${intakeSelect('degree_goal', 'Degree Goal', ['md_only'])}
        ${intakeSelect('applicant_state', 'Applicant State', states)}
        ${intakeSelect('mcat_band', 'MCAT Band', mcatBandOptions())}
        ${intakeSelect('gpa_band', 'GPA Band', gpaBandOptions())}
      </div>
    </fieldset>
    <fieldset>
      <legend>List Strategy</legend>
      <div class="field-grid">
        ${intakeSelect('application_strategy', 'Review Strategy', STRATEGY_OPTIONS)}
        ${intakeSelect('target_application_count', 'Target Count', ['15', '20', '25', '30', '35'])}
        ${intakeSelect('include_reach_schools', 'Include Reaches', ['yes', 'no'])}
        ${intakeSelect('cost_sensitivity', 'Cost Sensitivity', ['low', 'medium', 'high', 'debt_averse'])}
      </div>
    </fieldset>
    <fieldset>
      <legend>Location And Fit</legend>
      <div class="field-grid">
        ${intakeSelect('urbanicity_preference', 'Setting Preference', ['urban_preferred', 'suburban_ok', 'rural_ok', 'no_preference'])}
        ${intakeSelect('career_optionality', 'Career Optionality', ['undecided', 'em_leaning', 'competitive_optionality', 'academic_research'])}
      </div>
      <p class="muted" style="margin-top:8px">States to avoid are reversible local hides.</p>
      ${intakeCheckboxGroup('states_to_avoid', stateAvoidOptions, intakeState.states_to_avoid)}
    </fieldset>
    <fieldset>
      <legend>Awareness Prompts</legend>
      ${intakeDisclosureGroup('school_environment_preferences', ['true_pass_fail', 'low_mandatory_attendance', 'recorded_lectures', 'research_heavy', 'clinical_focus', 'large_academic_center', 'community_focus'], intakeState.school_environment_preferences)}
    </fieldset>
    <fieldset>
      <legend>Dealbreakers</legend>
      ${intakeDisclosureGroup('dealbreakers', ['hide_rural', 'hide_high_cost', 'hide_low_confidence', 'hide_state', 'hide_already_ruled_out'], intakeState.dealbreakers)}
    </fieldset>
    <div class="inline-actions">
      <button type="button" data-action="download-intake-json">Download Intake JSON</button>
      <button type="button" data-action="reset-intake">Reset Intake</button>
      <a href="#/rankings">Open Rankings</a>
      <a href="#/interested">Interested</a>
      <a href="#/applications">Applications</a>
    </div>
  </div>`;
}

function guidedStrategySettings() {
  const target = Number(intakeState?.target_application_count || 25) || 25;
  const strategy = intakeState?.application_strategy || 'balanced_list';
  if (strategy === 'safer_list') {
    return {
      startLimit: Math.max(6, Math.ceil(target * 0.32)),
      compareLimit: Math.max(10, Math.ceil(target * 0.8)),
      reachLimit: target + 4,
      label: STRATEGY_DETAILS.safer_list.label,
    };
  }
  if (strategy === 'reach_heavy_list') {
    return {
      startLimit: Math.max(10, Math.ceil(target * 0.48)),
      compareLimit: target,
      reachLimit: target + 20,
      label: STRATEGY_DETAILS.reach_heavy_list.label,
    };
  }
  return {
    startLimit: Math.max(8, Math.ceil(target * 0.4)),
    compareLimit: target,
    reachLimit: target + 10,
    label: STRATEGY_DETAILS.balanced_list.label,
  };
}

function guidedMissingData(row) {
  const item = row.item;
  const hasMcat = Boolean(item.ranking?.published_mcat_average || item.admissions_stats?.published_mcat_average);
  const hasGpa = Boolean(item.ranking?.published_gpa_average || item.admissions_stats?.published_gpa_average);
  const lowCoverage = row.overall?.score === null || (row.overall?.coverage ?? 0) < 0.35;
  return lowCoverage || !hasMcat || !hasGpa;
}

function guidedGroupForRow(row) {
  const item = row.item;
  const settings = guidedStrategySettings();
  const rank = Number(row.decisionRank || 9999);
  const sameState = intakeState?.applicant_state && schoolState(item) === intakeState.applicant_state;
  const avoided = new Set(arrayValue(intakeState?.states_to_avoid));
  if (isSchoolHidden(item) || avoided.has(schoolState(item))) return 'lower_priority_or_hidden';
  if (guidedMissingData(row)) return 'need_more_data';
  if (sameState && intakeState.applicant_state === 'FL') return 'florida_options';
  if (rank <= settings.startLimit) return 'start_here';
  if (rank > settings.compareLimit && rank <= settings.reachLimit && intakeState?.include_reach_schools !== 'no') return 'reach_schools_to_research';
  if (rank <= settings.compareLimit) return 'compare_next';
  return 'lower_priority_or_hidden';
}

function guidedRowsByGroup() {
  const grouped = Object.fromEntries(GUIDED_GROUPS.map(group => [group.id, []]));
  if (!intakeReady()) return grouped;
  syncSelectorFromIntake();
  const rankedRows = selectorRankedRows({includeHidden: true});
  const rankedIds = new Set(rankedRows.map(row => schoolId(row.item)));
  const unrankedRows = activeMdSchools({includeHidden: true})
    .filter(item => !rankedIds.has(schoolId(item)))
    .map(item => ({
      item,
      overrides: {},
      admissions: {score: null, coverage: 0},
      attendance: {score: null, coverage: 0},
      overall: {score: null, coverage: 0},
      costBasis: selectorCostBasis(item),
      decisionRank: '',
    }));
  [...rankedRows, ...unrankedRows].forEach(row => {
    grouped[guidedGroupForRow(row)].push(row);
  });
  return grouped;
}

function guidedReasonChips(row, groupId) {
  const item = row.item;
  const reasons = ['MD-only review', `${intakeState.mcat_band} / ${intakeState.gpa_band}`];
  if (row.decisionRank) reasons.push(`Selected rank ${row.decisionRank}`);
  if (groupId === 'florida_options') reasons.push('Florida option');
  if (schoolState(item) === intakeState.applicant_state) reasons.push('In-state context');
  if (row.overrides?.admissions_oos_friendliness_score !== undefined) reasons.push('State fit applied');
  if (row.overrides?.attendance_cost_score !== undefined) reasons.push('Cost context applied');
  if (intakeState.urbanicity_preference === 'urban_preferred') reasons.push('Urban preference noted');
  if (intakeState.career_optionality === 'em_leaning') reasons.push('EM interest awareness-only');
  return reasons.slice(0, 7);
}

function guidedRiskChips(row, groupId) {
  const item = row.item;
  const risks = [];
  if (isSchoolHidden(item)) risks.push(`Hidden: ${visibilityFor(item).visibility_reason || 'local decision'}`);
  if (groupId === 'need_more_data') risks.push('Incomplete data');
  if ((row.overall?.coverage ?? 0) < 0.5) risks.push('Low score coverage');
  if (row.costBasis && ['high', 'debt_averse'].includes(intakeState.cost_sensitivity) && row.costBasis > 90000) risks.push('High cost signal');
  if (row.decisionRank && Number(row.decisionRank) > Number(intakeState.target_application_count || 25)) risks.push('Outside target count');
  if (item.derived.admissions_data_quality_band && !['high', 'medium'].includes(item.derived.admissions_data_quality_band)) risks.push(`Stats quality ${item.derived.admissions_data_quality_band}`);
  if (item.ranking.score_warnings) risks.push('Score warning present');
  return risks.slice(0, 6);
}

function guidedMissingChips(row) {
  const missingParts = missingDossierSections(row.item);
  if (row.overall?.score === null) missingParts.unshift('selected rank');
  if (!row.item.ranking.published_mcat_average && !row.item.admissions_stats.published_mcat_average) missingParts.unshift('MCAT avg');
  if (!row.item.ranking.published_gpa_average && !row.item.admissions_stats.published_gpa_average) missingParts.unshift('GPA avg');
  return unique(missingParts).slice(0, 6);
}

function guidedNextAction(row, groupId) {
  if (groupId === 'need_more_data') return 'Open score card and fill missing research fields';
  if (groupId === 'lower_priority_or_hidden' && isSchoolHidden(row.item)) return 'Restore only if this school should return to review';
  if (groupId === 'reach_schools_to_research') return 'Research fit before adding to the 25-school target list';
  return applicationNextActionFor(row.item, applicationStatusFor(row.item));
}

function guidedCostFacts(row) {
  const cost = row.item.cost_and_debt || {};
  const inState = firstPositiveNumber(cost.estimated_coa_in_state, cost.in_state_tuition_fees_insurance);
  const outState = firstPositiveNumber(cost.estimated_coa_out_state, cost.out_state_tuition_fees_insurance);
  const selected = firstPositiveNumber(row.costBasis, row.item.ranking?.cost_basis, outState, inState);
  return {inState, outState, selected};
}

function renderGuidedSchoolCard(row, groupId) {
  const item = row.item;
  const id = schoolId(item);
  const reasonChips = guidedReasonChips(row, groupId).map(text => badge(text, 'good')).join('');
  const riskChips = guidedRiskChips(row, groupId).map(text => badge(text, 'warn')).join('') || badge('No current risk chip', 'good');
  const missingChips = guidedMissingChips(row).map(text => badge(text, 'warn')).join('') || badge('No major missing chip', 'good');
  const decisionRank = row.decisionRank || item.ranking.decision_rank || item.ranking.overall_rank || 'Missing';
  const overall = row.overall?.score === null ? 'Missing' : row.overall.score.toFixed(2);
  const admissions = row.admissions?.score === null ? 'Missing' : row.admissions.score.toFixed(2);
  const attendance = row.attendance?.score === null ? 'Missing' : row.attendance.score.toFixed(2);
  const costFacts = guidedCostFacts(row);
  return `<div class="panel school-review-card">
    <div>
      <h3>${linkSchool(item)}</h3>
      <p>${missing(item.school.degree_type)} · ${missing(item.school.city)}, ${missing(item.school.state)} · ${visibilityBadge(item)}</p>
    </div>
    <div class="node-fact-row"><strong>Decision Rank</strong><span>${missing(decisionRank)} · ${missing(item.ranking.rank_band || item.derived.rank_band)}</span></div>
    <div class="node-fact-row"><strong>Selected Scores</strong><span>Overall ${overall} · Admissions ${admissions} · Attendance ${attendance}</span></div>
    <div class="node-fact-row"><strong>MCAT and GPA</strong><span>${missing(item.ranking.published_mcat_average || item.admissions_stats.published_mcat_average)} / ${missing(item.ranking.published_gpa_average || item.admissions_stats.published_gpa_average)} · ${missing(item.ranking.profile_aamc_acceptance_rate_band || item.derived.aamc_acceptance_rate_band)}</span></div>
    <div class="node-fact-row"><strong>In-state estimated cost</strong><span>${formatCurrency(costFacts.inState)}</span></div>
    <div class="node-fact-row"><strong>Out-of-state estimated cost</strong><span>${formatCurrency(costFacts.outState)}</span></div>
    <div class="node-fact-row"><strong>Cost used for selected score</strong><span>${formatCurrency(costFacts.selected)}</span></div>
    <div class="card-note"><strong>Why here</strong><div class="card-chip-row">${reasonChips}</div></div>
    <div class="card-note"><strong>Risks</strong><div class="card-chip-row">${riskChips}</div></div>
    <div class="card-note"><strong>Missing data</strong><div class="card-chip-row">${missingChips}</div></div>
    <p><strong>Next action:</strong> ${guidedNextAction(row, groupId)}</p>
    <div class="card-actions">
      <a href="${item.profile_route || `#/schools/${item.school_slug}`}">Score Card</a>
      ${compareButton(item)}
      ${statusSwitchActions(item)}
      ${isSchoolHidden(item)
        ? `<button type="button" data-action="restore-school" data-school-id="${attr(id)}">Restore</button>`
        : `<button type="button" data-action="hide-school" data-school-id="${attr(id)}">Hide</button>`}
    </div>
  </div>`;
}

function renderGuidedGroup(group, groupedRows) {
  const rows = groupedRows[group.id] || [];
  const isOpen = guidedGroupOpenState[group.id] !== undefined ? guidedGroupOpenState[group.id] : group.defaultOpen;
  const body = isOpen
    ? rows.length
      ? `<div class="intake-card-grid">${rows.map(row => renderGuidedSchoolCard(row, group.id)).join('')}</div>`
      : '<div class="empty-state">No schools currently fall into this group.</div>'
    : '';
  return `<div class="guided-group">
    <button type="button" class="guided-group-header ${isOpen ? 'active' : ''}" data-action="toggle-guided-group" data-group-id="${attr(group.id)}">
      <strong>${safeText(group.label)}</strong>
      <span>${rows.length} schools · ${isOpen ? 'Collapse' : 'Expand'}</span>
    </button>
    ${body}
  </div>`;
}

function renderGuidedResults() {
  if (!intakeReady()) {
    return `<div class="empty-state">Choose MCAT band, GPA band, applicant state, and list preferences to generate grouped MD school cards.</div>`;
  }
  const grouped = guidedRowsByGroup();
  const totalRows = Object.values(grouped).reduce((sum, rows) => sum + rows.length, 0);
  const settings = guidedStrategySettings();
  return `<div class="grid">
      ${metric('Grouped MD schools', totalRows)}
      ${metric('Target applications', intakeState.target_application_count)}
      ${metric('Strategy', settings.label)}
      ${metric('Hidden schools', hiddenSchools().length)}
    </div>
    <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
    ${GUIDED_GROUPS.map(group => renderGuidedGroup(group, grouped)).join('')}`;
}

function updateSplitPaneHeight(selector, cssProperty) {
  const layout = document.querySelector(selector);
  if (!layout || window.matchMedia('(max-width: 760px)').matches) return;
  const top = layout.getBoundingClientRect().top;
  const available = Math.max(420, window.innerHeight - top - 12);
  layout.style.setProperty(cssProperty, `${available}px`);
}

function updateIntakePaneHeight() {
  updateSplitPaneHeight('.intake-layout', '--intake-layout-height');
}

function updateRankingsPaneHeight() {
  updateSplitPaneHeight('.rankings-layout', '--rankings-layout-height');
}

function captureScrollSnapshot() {
  const selectors = ['.view.active', '.intake-form', '.intake-results', '.rankings-menu', '.rankings-results', '.table-wrap'];
  return {
    windowX: window.scrollX,
    windowY: window.scrollY,
    elements: selectors.map(selector => {
      const element = document.querySelector(selector);
      return element ? {selector, top: element.scrollTop, left: element.scrollLeft} : null;
    }).filter(Boolean),
  };
}

function restoreScrollSnapshot(snapshot) {
  if (!snapshot) return;
  requestAnimationFrame(() => {
    window.scrollTo({top: snapshot.windowY || 0, left: snapshot.windowX || 0});
    snapshot.elements.forEach(record => {
      const element = document.querySelector(record.selector);
      if (element) {
        element.scrollTop = record.top || 0;
        element.scrollLeft = record.left || 0;
      }
    });
    if (currentRoute.view === 'intake') updateIntakePaneHeight();
    if (currentRoute.view === 'rankings') updateRankingsPaneHeight();
  });
}

function renderIntake() {
  $('intake').innerHTML = `<h2>Applicant Intake</h2>
    <div class="intake-layout">
      ${renderIntakeMenu()}
      <div class="intake-results">
        <div class="panel" style="margin-bottom:12px">
          <div class="inline-actions" style="justify-content:space-between">
            <h3 style="margin:0">Current Lens</h3>
            ${badge(intakeReady() ? 'Ready' : 'Needs required bands', intakeReady() ? 'good' : 'warn')}
          </div>
          ${intakeSummaryChips()}
        </div>
        ${renderGuidedResults()}
      </div>
    </div>`;
  updateIntakePaneHeight();
}

function renderRankings() {
  $('rankings').innerHTML = `<h2>Rankings</h2>
    <div class="rankings-layout">
      <div class="rankings-menu">${renderIntakeMenu()}</div>
      <div class="rankings-results">
        <div class="panel" style="margin-bottom:12px">
          <div class="inline-actions" style="justify-content:space-between">
            <h3 style="margin:0">Current Lens</h3>
            ${badge(intakeReady() ? 'Ready' : 'Needs required bands', intakeReady() ? 'good' : 'warn')}
          </div>
          ${intakeSummaryChips()}
        </div>
        <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
        <div id="rankTable"></div>
      </div>
    </div>
    ${renderHiddenSchoolsPanel()}`;
  const bindings = {
    rankDegree: 'degree',
    rankState: 'state',
    rankTier: 'tier',
    rankBucket: 'bucket',
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
  $('downloadRankingDossiers')?.addEventListener('click', downloadDossierExport);
  $('downloadRankingVisibility')?.addEventListener('click', downloadVisibilityExport);
  $('downloadVisibilityExport')?.addEventListener('click', downloadVisibilityExport);
  if ($('mdSelectorTable')) renderMdSelectorTable();
  renderRankingTable();
  updateRankingsPaneHeight();
}

function renderRankingTable() {
  const selectedRows = selectorReady() ? selectorRankedRows() : [];
  const selectedById = new Map(selectedRows.map(row => [schoolId(row.item), row]));
  let visibleRows = selectorReady() ? selectedRows.map(row => row.item) : rankingsRows();
  if (!selectorReady() || sortState.rankings?.key) {
    visibleRows = sortRows(visibleRows, 'rankings', 'ranking.overall_rank');
  }
  const columns = [
    {key:'ranking.overall_rank', label:'Decision Rank', render:s=>missing(selectedById.get(schoolId(s))?.decisionRank || s.ranking.decision_rank || s.ranking.overall_rank)},
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'ranking.admissions_fit_tier', label:'Admissions Tier', render:s=>missing(s.ranking.admissions_fit_tier || s.ranking.dynamic_tier)},
    {key:'ranking.overall_school_value', label:'Overall', render:s=>selectedById.get(schoolId(s))?.overall?.score?.toFixed(2) || missing(s.ranking.overall_school_value)},
    {key:'ranking.published_mcat_average', label:'MCAT average', render:s=>missing(s.ranking.published_mcat_average || s.admissions_stats.published_mcat_average)},
    {key:'ranking.published_gpa_average', label:'GPA average', render:s=>missing(s.ranking.published_gpa_average || s.admissions_stats.published_gpa_average)},
    {key:'derived.aamc_acceptance_rate_band', label:'AAMC Band', render:s=>missing(s.ranking.profile_aamc_acceptance_rate_band || s.derived.aamc_acceptance_rate_band)},
    {key:'cost_and_debt.estimated_coa_in_state', label:'In-state estimated cost', render:s=>formatCurrency(s.cost_and_debt.estimated_coa_in_state || s.cost_and_debt.in_state_tuition_fees_insurance)},
    {key:'cost_and_debt.estimated_coa_out_state', label:'Out-of-state estimated cost', render:s=>formatCurrency(s.cost_and_debt.estimated_coa_out_state || s.cost_and_debt.out_state_tuition_fees_insurance)},
    {key:'derived.admissions_data_quality_band', label:'Data Quality', render:s=>badge(s.derived.admissions_data_quality_band)},
    {key:'dossier.application_decision_status', label:'Status', render:s=>statusSwitchActions(s)},
    {key:'actions', label:'Actions', render:s=>`<div class="inline-actions"><a href="${s.profile_route || `#/schools/${s.school_slug}`}">Score Card</a>${compareButton(s)}</div>`},
  ];
  if (ADMIN_ENABLED) {
    columns.push(
      {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
      {key:'derived.excluded_from_rank', label:'Excluded', render:s=>s.derived.excluded_from_rank ? badge('Excluded', 'warn') : ''},
      {key:'derived.hard_no_flag', label:'Hard No', render:s=>s.derived.hard_no_flag ? badge('Hard No', 'error') : ''}
    );
  }
  $('rankTable').innerHTML = `<div class="rankings-results-header">
    <p style="margin:0">${selectorReady() ? `${visibleRows.length} MD schools match the selected intake lens.` : `${visibleRows.length} visible schools match the current selections.`}</p>
    ${badge(`${hiddenSchools().length} hidden`, hiddenSchools().length ? 'warn' : 'good')}
  </div>` + table(columns, visibleRows, 'rankings');
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

function compareDetailRows(item) {
  const compareNode = getCompareCardNode(schoolId(item));
  if (compareNode) {
    return [
      ['Decision rank', compareNode.rank_fit?.decision_rank],
      ['Application decision', labelize(applicationStatusFor(item))],
      ['Research status', labelize(researchStatusFor(item))],
      ['Interest', labelize(dossierFor(item).interest_level)],
      ['Admissions tier', compareNode.rank_fit?.admissions_fit_tier],
      ['Rank band', compareNode.rank_fit?.rank_band],
      ['Admissions score', compareNode.rank_fit?.admissions_score],
      ['Attendance score', compareNode.rank_fit?.attendance_score],
      ['MCAT average', compareNode.admissions_facts?.mcat_average],
      ['GPA average', compareNode.admissions_facts?.gpa_average],
      ['AAMC band', compareNode.admissions_facts?.aamc_rate_band],
      ['In-state estimated cost', formatCurrency(compareNode.cost_facts?.in_state)],
      ['Out-of-state estimated cost', formatCurrency(compareNode.cost_facts?.out_state)],
      ['Cost used for selected score', formatCurrency(compareNode.cost_facts?.cost_basis)],
      ['Policy rows', compareNode.requirements_summary?.policy_count],
      ['Letter rows', compareNode.requirements_summary?.letter_requirement_count],
      ['Missing sections', compareNode.missing_data_summary?.missing_fields?.join(', ') || 'Complete'],
      ['Next action', applicationNextActionFor(item, applicationStatusFor(item))],
      ['Notes', dossierFor(item).notes],
    ];
  }
  // Defensive fallback for older payloads that do not yet include compare_card_nodes.
  return [
    ['Decision rank', item.ranking.decision_rank || item.ranking.overall_rank],
    ['Application decision', labelize(applicationStatusFor(item))],
    ['Research status', labelize(researchStatusFor(item))],
    ['Interest', labelize(dossierFor(item).interest_level)],
    ['Admissions tier', item.ranking.admissions_fit_tier || item.ranking.dynamic_tier || item.derived.admissions_fit_tier],
    ['Rank band', item.ranking.rank_band || item.derived.rank_band],
    ['Overall value', item.ranking.overall_school_value],
    ['Admissions score', item.ranking.admissions_score],
    ['Attendance score', item.ranking.attendance_score],
    ['MCAT average', item.ranking.published_mcat_average || item.admissions_stats.published_mcat_average],
    ['GPA average', item.ranking.published_gpa_average || item.admissions_stats.published_gpa_average],
    ['AAMC band', item.ranking.profile_aamc_acceptance_rate_band || item.derived.aamc_acceptance_rate_band],
    ['In-state estimated cost', formatCurrency(item.cost_and_debt.estimated_coa_in_state || item.cost_and_debt.in_state_tuition_fees_insurance)],
    ['Out-of-state estimated cost', formatCurrency(item.cost_and_debt.estimated_coa_out_state || item.cost_and_debt.out_state_tuition_fees_insurance)],
    ['Cost used for selected score', formatCurrency(item.ranking.cost_basis)],
    ['Stats quality', item.derived.admissions_data_quality_band],
    ['Rank confidence', item.ranking.rank_confidence || item.derived.rank_confidence],
      ['Missing score-card sections', missingDossierSections(item).join(', ') || 'Complete'],
    ['Next action', applicationNextActionFor(item, applicationStatusFor(item))],
    ['Notes', dossierFor(item).notes],
  ];
}

function renderCompareCard(item) {
  const compareNode = getCompareCardNode(schoolId(item));
  const identity = compareNode?.identity || {};
  const degree = identity.degree_type || item.school.degree_type;
  const city = identity.city || item.school.city;
  const state = identity.state || item.school.state;
  return `<div class="compare-card">
    <div class="inline-actions" style="justify-content:space-between">
      <h3 style="margin:0">${linkSchool(item)}</h3>
      ${compareButton(item)}
    </div>
    <p>${missing(degree)} · ${missing(city)}, ${missing(state)} · ${visibilityBadge(item)} ${compareNode ? nodeStatusChip(compareNode.missing_data_summary?.readiness) : ''}</p>
    ${compareDetailRows(item).map(([label, value]) => `<div class="compare-row"><strong>${label}</strong><span>${missing(value)}</span></div>`).join('')}
  </div>`;
}

function renderCompare() {
  const selected = selectedCompareItems();
  const candidates = sortRows(filteredSchools(), 'compareCandidates', 'ranking.overall_rank').slice(0, 50);
  const selectedMarkup = selected.length
    ? `<div class="compare-grid">${selected.map(renderCompareCard).join('')}</div>`
    : '<div class="empty-state">Select 2-4 schools from the table below, Rankings, Interested, or Applications to compare them side by side.</div>';
  const compareStatus = selected.length < 2
    ? 'Select at least 2 schools for a useful comparison.'
    : `${selected.length} schools selected for side-by-side review.`;
  $('compare').innerHTML = `<h2>Compare</h2>
    <div class="caveat">Compare state is browser-local. It is for review only and does not write to source CSVs.</div>
    <div class="grid">
      ${metric('Selected', `${selected.length}/4`)}
      ${metric('Candidate rows', candidates.length)}
      ${metric('Visible schools', filteredSchools().filter(item => !isSchoolHidden(item)).length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" data-action="clear-compare">Clear Compare</button>
      <a href="#/rankings">Back to Rankings</a>
      <a href="#/interested">Interested</a>
      <a href="#/applications">Applications</a>
      <span class="muted">${compareStatus}</span>
    </div>
    ${selectedMarkup}
    <h3>Choose Schools</h3>
    ${table([
      {key:'compare.selected', label:'Compare', render:s=>compareButton(s)},
      {key:'ranking.overall_rank', label:'Decision Rank', render:s=>missing(s.ranking.decision_rank || s.ranking.overall_rank)},
      {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
      {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
      {key:'school.city', label:'Location', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
      {key:'dossier.application_decision_status', label:'Status', render:s=>statusSwitchActions(s)},
      {key:'dossier.interest_level', label:'Interest', render:s=>interestControl(s)},
      {key:'ranking.admissions_fit_tier', label:'Admissions Tier', render:s=>missing(s.ranking.admissions_fit_tier || s.ranking.dynamic_tier || s.derived.admissions_fit_tier)},
      {key:'ranking.published_mcat_average', label:'MCAT average', render:s=>missing(s.ranking.published_mcat_average || s.admissions_stats.published_mcat_average)},
      {key:'ranking.published_gpa_average', label:'GPA average', render:s=>missing(s.ranking.published_gpa_average || s.admissions_stats.published_gpa_average)},
      {key:'cost_and_debt.estimated_coa_in_state', label:'In-state estimated cost', render:s=>formatCurrency(s.cost_and_debt.estimated_coa_in_state || s.cost_and_debt.in_state_tuition_fees_insurance)},
      {key:'cost_and_debt.estimated_coa_out_state', label:'Out-of-state estimated cost', render:s=>formatCurrency(s.cost_and_debt.estimated_coa_out_state || s.cost_and_debt.out_state_tuition_fees_insurance)},
      {key:'derived.admissions_data_quality_band', label:'Stats Quality', render:s=>badge(s.derived.admissions_data_quality_band)},
    ], candidates, 'compareCandidates')}`;
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
      <h3 style="margin:0">Local Score Card</h3>
      ${badge(`${editCount} edited`, editCount ? 'warn' : '')}
      <button type="button" id="downloadDossierExport">Download Score Card Edits CSV</button>
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
      <label>List status ${statusSwitchActions(item)}</label>
      ${dossierTextarea(item, 'notes', 'Score card notes', 'School-specific research, subjective fit, unanswered questions')}
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
  $('dossiers').innerHTML = `<h2>School Score Cards</h2>
    <div class="caveat">Score cards combine source-backed fields with local reviewer notes. Local edits are exported separately and do not mutate the seed data.</div>
    <div class="grid">
      ${metric('Visible schools', rows('schools').filter(item => !isSchoolHidden(item)).length)}
      ${metric('Hidden schools', hiddenSchools().length)}
      ${metric('Edited score cards', dossierExportRecords().length)}
      ${metric('Rows in view', tableRows.length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" id="downloadDossierIndexExport">Download Score Card Edits CSV</button>
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
      {key:'dossier.missing', label:'Missing Score-Card Sections', render:s=>missingDossierSections(s).join(', ') || 'Complete'},
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
    start: 'Start score card',
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
    <label>Next Action <select id="researchAction"><option value="" ${f.action === '' ? 'selected' : ''}>All</option><option value="start" ${f.action === 'start' ? 'selected' : ''}>Start score card</option><option value="score" ${f.action === 'score' ? 'selected' : ''}>Score four-year fit</option><option value="interest" ${f.action === 'interest' ? 'selected' : ''}>Set interest level</option><option value="fill" ${f.action === 'fill' ? 'selected' : ''}>Fill source gap</option><option value="decision" ${f.action === 'decision' ? 'selected' : ''}>Set decision status</option><option value="ready" ${f.action === 'ready' ? 'selected' : ''}>Ready</option><option value="hidden" ${f.action === 'hidden' ? 'selected' : ''}>Hidden review</option></select></label>
    <label>Admissions Tier <select id="researchTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
    <label>Rank Band <select id="researchRankBand"><option value="" ${f.rankBand === '' ? 'selected' : ''}>All</option>${optionTags(rankBands, f.rankBand)}</select></label>
  </div>`;
}

function renderResearch() {
  const queueRows = researchQueueRows();
  const visibleRows = rows('schools').filter(item => !isSchoolHidden(item));
  const readyCount = visibleRows.filter(item => nextResearchAction(item) === 'Ready for shortlist review').length;
  $('research').innerHTML = `<h2>Research Queue</h2>
    <div class="caveat">The queue is deterministic: hidden status, missing source sections, and local score-card fields drive the next action.</div>
    <div class="grid">
      ${metric('Rows in queue', queueRows.length)}
      ${metric('Visible schools', visibleRows.length)}
      ${metric('Ready for shortlist review', readyCount)}
      ${metric('Edited score cards', dossierExportRecords().length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" id="downloadResearchDossiers">Download Score Card Edits CSV</button>
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

function applicationServiceFor(item) {
  const degree = String(item.school?.degree_type || '').toUpperCase();
  if (degree === 'MD') return 'AMCAS';
  if (degree === 'DO') return 'AACOMAS';
  return '';
}

function applicationStatusFor(item) {
  return dossierFor(item).application_decision_status || 'unselected';
}

function applicationStatusCounts() {
  return rows('schools').reduce((counts, item) => {
    const status = applicationStatusFor(item);
    if (APPLICATION_INTERESTED_STATUSES.includes(status)) counts.interested += 1;
    if (APPLICATION_APPLYING_STATUSES.includes(status)) counts.applying += 1;
    return counts;
  }, {interested: 0, applying: 0});
}

function applicationBucketFor(item) {
  return item.ranking.application_bucket || item.ranking.suggested_funnel_bucket || item.derived.application_bucket || '';
}

function applicationRankFor(item) {
  return parseScore(item.ranking.decision_rank || item.ranking.overall_rank) ?? 9999;
}

function isActiveApplicationStatus(status) {
  return APPLICATION_ACTIVE_STATUSES.includes(status);
}

function applicationPriorityFor(item, status) {
  const rank = applicationRankFor(item);
  if (['accepted', 'interview', 'applied', 'applying'].includes(status)) return rank <= 40 ? 'highest' : 'high';
  if (rank <= 25) return 'highest';
  if (rank <= 40) return 'high';
  if (rank <= 75) return 'medium';
  return 'low';
}

function applicationNextActionFor(item, status) {
  const researchStatus = researchStatusFor(item);
  if (status === 'accepted') return 'Compare offer and revisit final fit';
  if (status === 'waitlisted') return 'Track waitlist movement and update letters';
  if (status === 'interview') return 'Prepare for interview';
  if (status === 'applied') return 'Track secondary, interview, and decision updates';
  if (status === 'applying') return 'Submit primary and secondary materials';
  if (['researched', 'ready_to_decide'].includes(researchStatus)) return 'Decide whether to submit application';
  if (status === 'unselected') return nextResearchAction(item);
  return 'Research score card and decide whether to apply';
}

function applicationWhyKept(item, status) {
  const parts = [`Marked ${status === 'unselected' ? 'unselected' : status} in school score card`];
  const rank = item.ranking.decision_rank || item.ranking.overall_rank;
  if (rank) parts.push(`Decision Rank ${rank}`);
  const rankBand = item.ranking.rank_band || item.derived.rank_band;
  if (rankBand) parts.push(`rank band ${rankBand}`);
  const tier = item.ranking.admissions_fit_tier || item.ranking.dynamic_tier || item.derived.admissions_fit_tier;
  if (tier) parts.push(`admissions tier ${tier}`);
  const bucket = applicationBucketFor(item);
  if (bucket) parts.push(`bucket ${bucket}`);
  const interest = dossierFor(item).interest_level;
  if (interest) parts.push(`interest ${interest}`);
  return parts.join('; ') + '.';
}

function applicationWhyCut(item, status) {
  if (isSchoolHidden(item)) {
    const reason = visibilityFor(item).visibility_reason;
    return reason ? `Hidden: ${reason}` : 'Hidden from current review view.';
  }
  if (APPLICATION_EXCLUDED_STATUSES.includes(status)) return `Marked ${status} in school score card.`;
  if (truthy(dossierFor(item).hard_no_flag)) return dossierFor(item).hard_no_reason || 'Marked hard no in school score card.';
  return '';
}

function applicationWorkflowRows() {
  return filteredSchools().map(item => {
    const status = applicationStatusFor(item);
    const priority = applicationPriorityFor(item, status);
    return {
      item,
      status,
      priority,
      rank: applicationRankFor(item),
      dossier: dossierFor(item),
      hidden: isSchoolHidden(item),
      bucket: applicationBucketFor(item),
      service: applicationServiceFor(item),
      nextAction: applicationNextActionFor(item, status),
      whyKept: applicationWhyKept(item, status),
      whyCut: applicationWhyCut(item, status),
    };
  });
}

function sortApplicationWorkflowRows(rowList) {
  return rowList.sort((a, b) => {
    const priorityOrder = {highest: 0, high: 1, medium: 2, low: 3};
    const priorityDelta = (priorityOrder[a.priority] ?? 9) - (priorityOrder[b.priority] ?? 9);
    if (priorityDelta) return priorityDelta;
    if (a.rank !== b.rank) return a.rank - b.rank;
    return String(a.item.school.school_name).localeCompare(String(b.item.school.school_name));
  });
}

function consideringListRows() {
  const f = filters.consideringList;
  return sortApplicationWorkflowRows(applicationWorkflowRows().filter(row => {
    const item = row.item;
    if (!APPLICATION_INTERESTED_STATUSES.includes(row.status)) return false;
    if (f.visibility === 'visible' && row.hidden) return false;
    if (f.visibility === 'hidden' && !row.hidden) return false;
    if (f.degree && item.school.degree_type !== f.degree) return false;
    if (f.tier && (item.ranking.admissions_fit_tier || item.ranking.dynamic_tier || item.derived.admissions_fit_tier) !== f.tier) return false;
    if (f.rankBand && (item.ranking.rank_band || item.derived.rank_band) !== f.rankBand) return false;
    if (f.interest && row.dossier.interest_level !== f.interest) return false;
    if (f.maxRank && row.rank > Number(f.maxRank)) return false;
    return true;
  }));
}

function applicationListRows() {
  const f = filters.applicationList;
  return sortApplicationWorkflowRows(applicationWorkflowRows().filter(row => {
    const item = row.item;
    if (!APPLICATION_APPLYING_STATUSES.includes(row.status)) return false;
    if (f.visibility === 'visible' && row.hidden) return false;
    if (f.visibility === 'hidden' && !row.hidden) return false;
    if (f.degree && item.school.degree_type !== f.degree) return false;
    if (f.tier && (item.ranking.admissions_fit_tier || item.ranking.dynamic_tier || item.derived.admissions_fit_tier) !== f.tier) return false;
    if (f.rankBand && (item.ranking.rank_band || item.derived.rank_band) !== f.rankBand) return false;
    if (f.interest && row.dossier.interest_level !== f.interest) return false;
    if (f.priority && row.priority !== f.priority) return false;
    if (f.maxRank && row.rank > Number(f.maxRank)) return false;
    return true;
  }));
}

function finalApplicationRecords() {
  return applicationListRows().map(row => ({
    school_id: schoolId(row.item),
    school_name: row.item.school.school_name || '',
    degree_type: row.item.school.degree_type || '',
    city: row.item.school.city || '',
    state: row.item.school.state || '',
    current_bucket: row.bucket,
    status: row.status === 'unselected' ? '' : row.status,
    why_kept: isActiveApplicationStatus(row.status) ? row.whyKept : '',
    why_cut: row.whyCut,
    assigned_research_owner: '',
    next_action: row.nextAction,
    priority: row.priority,
    application_service: row.service,
    primary_deadline: '',
    secondary_fee: '',
    submitted_primary: '',
    secondary_received: '',
    secondary_submitted: '',
    interview_invite: '',
    decision: row.status === 'unselected' ? '' : row.status,
    notes: row.dossier.notes || '',
  }));
}

function downloadFinalApplicationList() {
  downloadCsv('final_application_list_export.csv', APPLICATION_EXPORT_HEADERS, finalApplicationRecords());
}

function listLimitWarning(kind, count, limit) {
  if (count < limit) return '';
  return `<div class="caveat">${safeText(kind)} is at the hard limit of ${limit}. Remove a school from this list before adding another.</div>`;
}

function renderConsideringListFilters() {
  const degrees = unique(rows('schools').map(s => s.school.degree_type)).sort();
  const tiers = unique(rows('schools').map(s => s.ranking.admissions_fit_tier || s.ranking.dynamic_tier || s.derived.admissions_fit_tier)).sort();
  const rankBands = unique(rows('schools').map(s => s.ranking.rank_band || s.derived.rank_band)).sort();
  const f = filters.consideringList;
  return `<div class="filters">
    <label>Visibility <select id="consideringVisibility"><option value="visible" ${f.visibility === 'visible' ? 'selected' : ''}>Visible</option><option value="all" ${f.visibility === 'all' ? 'selected' : ''}>All</option><option value="hidden" ${f.visibility === 'hidden' ? 'selected' : ''}>Hidden</option></select></label>
    <label>Degree <select id="consideringDegree"><option value="" ${f.degree === '' ? 'selected' : ''}>All</option>${optionTags(degrees, f.degree)}</select></label>
    <label>Interest <select id="consideringInterest">${labeledOptions(INTEREST_LEVELS, f.interest)}</select></label>
    <label>Admissions Tier <select id="consideringTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
    <label>Rank Band <select id="consideringRankBand"><option value="" ${f.rankBand === '' ? 'selected' : ''}>All</option>${optionTags(rankBands, f.rankBand)}</select></label>
    <label>Max Rank <select id="consideringMaxRank"><option value="" ${f.maxRank === '' ? 'selected' : ''}>All</option><option value="25" ${f.maxRank === '25' ? 'selected' : ''}>Top 25</option><option value="35" ${f.maxRank === '35' ? 'selected' : ''}>Top 35</option><option value="50" ${f.maxRank === '50' ? 'selected' : ''}>Top 50</option><option value="75" ${f.maxRank === '75' ? 'selected' : ''}>Top 75</option></select></label>
  </div>`;
}

function renderConsideringList() {
  const tableRows = consideringListRows();
  const counts = applicationStatusCounts();
  const emptyMessage = tableRows.length ? '' : '<div class="empty-state" style="margin-bottom:12px">No schools are marked Interested yet. Add schools from Rankings, guided cards, or a school score card.</div>';
  $('consideringList').innerHTML = `<h2>Interested</h2>
    <div class="caveat">Interested is the working review list. Keep it under ${INTERESTED_LIMIT}, then promote only true applications to Applying.</div>
    ${listLimitWarning('Interested', counts.interested, INTERESTED_LIMIT)}
    <div class="grid">
      ${metric('Interested', `${counts.interested}/${INTERESTED_LIMIT}`)}
      ${metric('Applying', `${counts.applying}/${APPLYING_LIMIT}`)}
      ${metric('Rows in view', tableRows.length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" id="downloadConsideringDossiers">Download Score Card Edits CSV</button>
      <a href="#/rankings">Open Rankings</a>
      <a href="#/applications">Open Applications</a>
      <a href="#/compare">Open Compare</a>
    </div>
    ${renderConsideringListFilters()}
    ${emptyMessage}
    ${table([
      {key:'rank', label:'Decision Rank', render:r=>r.rank === 9999 ? 'Missing' : r.rank},
      {key:'item.school.school_name', label:'School', render:r=>linkSchool(r.item)},
      {key:'item.school.city', label:'Location', render:r=>`${missing(r.item.school.city)}, ${missing(r.item.school.state)}`},
      {key:'tier', label:'Admissions Tier', render:r=>missing(r.item.ranking.admissions_fit_tier || r.item.ranking.dynamic_tier || r.item.derived.admissions_fit_tier)},
      {key:'status', label:'Status', render:r=>statusSwitchActions(r.item)},
      {key:'interest', label:'Interest', render:r=>interestControl(r.item)},
      {key:'nextAction', label:'Next Action', render:r=>r.nextAction},
      {key:'actions', label:'Actions', render:r=>`<div class="inline-actions"><a href="${r.item.profile_route || `#/schools/${r.item.school_slug}`}">Score Card</a>${compareButton(r.item)}</div>`},
    ], tableRows, 'consideringList')}`;
  const bindings = {
    consideringVisibility: 'visibility',
    consideringDegree: 'degree',
    consideringInterest: 'interest',
    consideringTier: 'tier',
    consideringRankBand: 'rankBand',
    consideringMaxRank: 'maxRank',
  };
  Object.entries(bindings).forEach(([id, key]) => $(id)?.addEventListener('change', event => {
    filters.consideringList[key] = event.target.value;
    renderConsideringList();
  }));
  $('downloadConsideringDossiers')?.addEventListener('click', downloadDossierExport);
}

function renderApplicationListFilters() {
  const degrees = unique(rows('schools').map(s => s.school.degree_type)).sort();
  const tiers = unique(rows('schools').map(s => s.ranking.admissions_fit_tier || s.ranking.dynamic_tier || s.derived.admissions_fit_tier)).sort();
  const rankBands = unique(rows('schools').map(s => s.ranking.rank_band || s.derived.rank_band)).sort();
  const f = filters.applicationList;
  return `<div class="filters">
    <label>Visibility <select id="applicationVisibility"><option value="visible" ${f.visibility === 'visible' ? 'selected' : ''}>Visible</option><option value="all" ${f.visibility === 'all' ? 'selected' : ''}>All</option><option value="hidden" ${f.visibility === 'hidden' ? 'selected' : ''}>Hidden</option></select></label>
    <label>Degree <select id="applicationDegree"><option value="" ${f.degree === '' ? 'selected' : ''}>All</option>${optionTags(degrees, f.degree)}</select></label>
    <label>Interest <select id="applicationInterest">${labeledOptions(INTEREST_LEVELS, f.interest)}</select></label>
    <label>Priority <select id="applicationPriority"><option value="" ${f.priority === '' ? 'selected' : ''}>All</option><option value="highest" ${f.priority === 'highest' ? 'selected' : ''}>Highest</option><option value="high" ${f.priority === 'high' ? 'selected' : ''}>High</option><option value="medium" ${f.priority === 'medium' ? 'selected' : ''}>Medium</option><option value="low" ${f.priority === 'low' ? 'selected' : ''}>Low</option></select></label>
    <label>Admissions Tier <select id="applicationTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
    <label>Rank Band <select id="applicationRankBand"><option value="" ${f.rankBand === '' ? 'selected' : ''}>All</option>${optionTags(rankBands, f.rankBand)}</select></label>
    <label>Max Rank <select id="applicationMaxRank"><option value="" ${f.maxRank === '' ? 'selected' : ''}>All</option><option value="25" ${f.maxRank === '25' ? 'selected' : ''}>Top 25</option><option value="35" ${f.maxRank === '35' ? 'selected' : ''}>Top 35</option><option value="50" ${f.maxRank === '50' ? 'selected' : ''}>Top 50</option><option value="75" ${f.maxRank === '75' ? 'selected' : ''}>Top 75</option></select></label>
  </div>`;
}

function renderApplicationList() {
  const tableRows = applicationListRows();
  const counts = applicationStatusCounts();
  const emptyMessage = tableRows.length ? '' : '<div class="empty-state" style="margin-bottom:12px">No schools are marked Applying yet. Promote schools from Interested or a school score card.</div>';
  $('applicationList').innerHTML = `<h2>Applications</h2>
    <div class="caveat">Applications is the active submission list. Keep it under ${APPLYING_LIMIT}; remove a school before adding another once the cap is reached.</div>
    ${listLimitWarning('Applications', counts.applying, APPLYING_LIMIT)}
    <div class="grid">
      ${metric('Interested', `${counts.interested}/${INTERESTED_LIMIT}`)}
      ${metric('Applying', `${counts.applying}/${APPLYING_LIMIT}`)}
      ${metric('Rows in view', tableRows.length)}
    </div>
    <div class="inline-actions" style="margin-bottom:12px">
      <button type="button" id="downloadFinalApplicationList">Download Current View CSV</button>
      <button type="button" id="downloadApplicationDossiers">Download Score Card Edits CSV</button>
      <a href="#/interested">Open Interested</a>
      <a href="#/compare">Open Compare</a>
    </div>
    ${renderApplicationListFilters()}
    ${emptyMessage}
    ${table([
      {key:'rank', label:'Decision Rank', render:r=>r.rank === 9999 ? 'Missing' : r.rank},
      {key:'item.school.school_name', label:'School', render:r=>linkSchool(r.item)},
      {key:'item.school.city', label:'Location', render:r=>`${missing(r.item.school.city)}, ${missing(r.item.school.state)}`},
      {key:'priority', label:'Priority', render:r=>badge(labelize(r.priority), r.priority === 'highest' || r.priority === 'high' ? 'good' : '')},
      {key:'status', label:'Status', render:r=>statusSwitchActions(r.item)},
      {key:'research', label:'Research Status', render:r=>researchStatusControl(r.item)},
      {key:'interest', label:'Interest', render:r=>interestControl(r.item)},
      {key:'tier', label:'Admissions Tier', render:r=>missing(r.item.ranking.admissions_fit_tier || r.item.ranking.dynamic_tier || r.item.derived.admissions_fit_tier)},
      {key:'service', label:'Service', render:r=>missing(r.service)},
      {key:'nextAction', label:'Next Action', render:r=>r.nextAction},
      {key:'actions', label:'Actions', render:r=>`<div class="inline-actions"><a href="${r.item.profile_route || `#/schools/${r.item.school_slug}`}">Score Card</a>${compareButton(r.item)}</div>`},
    ], tableRows, 'applicationList')}`;
  const bindings = {
    applicationVisibility: 'visibility',
    applicationDegree: 'degree',
    applicationInterest: 'interest',
    applicationPriority: 'priority',
    applicationTier: 'tier',
    applicationRankBand: 'rankBand',
    applicationMaxRank: 'maxRank',
  };
  Object.entries(bindings).forEach(([id, key]) => $(id)?.addEventListener('change', event => {
    filters.applicationList[key] = event.target.value;
    renderApplicationList();
  }));
  $('downloadFinalApplicationList')?.addEventListener('click', downloadFinalApplicationList);
  $('downloadApplicationDossiers')?.addEventListener('click', downloadDossierExport);
}

function renderProfile() {
  const profileNode = getSchoolProfileNode(currentRoute.slug);
  const routeItem = rows('schools').find(s => s.school_slug === currentRoute.slug);
  const item = (profileNode ? schoolById(profileNode.school_id) : routeItem) || routeItem || rows('schools')[0];
  const node = profileNode || (item ? getSchoolProfileNode(schoolId(item)) : null);
  if (!item && !node) { $('profile').innerHTML = '<p>No school selected.</p>'; return; }

  const header = node?.header || {};
  const schoolIdValue = node?.school_id || (item ? schoolId(item) : '');
  const rankingCard = getRankingCardNode(schoolIdValue);
  const schoolName = header.display_name || item?.school?.school_name || 'School profile';
  const degreeType = header.degree_type || item?.school?.degree_type || '';
  const city = header.city || item?.school?.city || '';
  const state = header.state || item?.school?.state || '';
  const officialUrl = header.official_url || item?.school?.source_url || item?.school?.official_url || '';
  const sourceUrl = officialUrl ? `<a href="${attr(officialUrl)}" target="_blank">Source</a>` : 'Missing';
  const decisionRank = rankingCard?.decision_rank || item?.ranking?.decision_rank || item?.ranking?.overall_rank;
  const contributionRows = item ? rows('score_contributions').filter(row => (
    row.school_id === item.school.school_id
    && row.applicant_profile_id === item.ranking.applicant_profile_id
    && row.score_model === 'Decision Rank'
  )) : [];
  const localDossier = item ? dossierFor(item) : {};
  const adminPanels = ADMIN_ENABLED && item ? `
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
  const issuesPanel = ADMIN_ENABLED && item ? `<div class="panel" style="margin-top:12px">
      <h3>Issues</h3>
      ${table([
        {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
        {key:'file', label:'File', render:i=>i.file},
        {key:'field', label:'Field', render:i=>i.field},
        {key:'message', label:'Message', render:i=>i.message},
        {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
      ], item.data_quality || [], 'detailIssues')}
    </div>` : '';
  const profileActionPanel = item ? `<div class="panel" style="margin-bottom:12px">
      <div class="inline-actions">
        <h3 style="margin:0">Review Actions</h3>
        ${visibilityBadge(item)}
        ${applicationStatusBadge(item)}
        ${compareButton(item)}
        ${isSchoolHidden(item)
          ? `<button type="button" data-action="restore-school" data-school-id="${attr(schoolId(item))}">Restore School</button>`
          : `<button type="button" data-action="hide-school" data-school-id="${attr(schoolId(item))}">Hide School</button>`}
        <button type="button" id="downloadProfileDossierState">Download Score Card Edits CSV</button>
      </div>
      <div class="field-grid" style="margin-top:10px">
        <label>List status ${statusSwitchActions(item)}</label>
        <label>Interest ${interestControl(item)}</label>
        <label>Research status ${researchStatusControl(item)}</label>
        <label>Four-year happiness ${dossierInlineScoreSelect(item, 'four_year_happiness', 'Four-year happiness')}</label>
      </div>
      <p><strong>Next action:</strong> ${applicationNextActionFor(item, applicationStatusFor(item))}</p>
      <p><strong>Missing score-card sections:</strong> ${missingDossierSections(item).join(', ') || 'Complete'}</p>
    </div>` : '';
  const snapshotCards = Array.isArray(node?.snapshot_cards) ? node.snapshot_cards : [];
  const snapshotMarkup = snapshotCards.length
    ? `<div class="node-metric-grid">${snapshotCards.map(renderMetricCard).join('')}</div>`
    : '';
  const nodeSectionMarkup = node
    ? `<div class="detail-grid">${(node.sections || []).map(renderProfileSectionBlock).join('')}</div>${renderSchoolCardNodePreview(node.school_id)}`
    : `<div class="empty-state">Profile data is unavailable for this route; local controls are still available.</div>`;
  const legacyLocalStatus = item ? detailPanel('Local Score Card Status', [
    ['Visibility', visibilityFor(item).visibility_state],
    ['Research status', labelize(researchStatusFor(item))],
    ['Interest level', labelize(localDossier.interest_level)],
    ['Application decision', labelize(localDossier.application_decision_status)],
    ['Missing score-card sections', missingDossierSections(item).join(', ') || 'Complete'],
    ['Next research action', nextResearchAction(item)],
  ]) : '';

  // Primary profile path: route slug -> school_profile_node -> section blocks.
  $('profile').innerHTML = `<div class="route-tools"><a href="#/dossiers">Score Cards</a><a href="#/interested">Interested</a><a href="#/applications">Applications</a><a href="#/rankings">Rankings</a></div>
    <h2>${safeText(schoolName)}</h2>
    <p>${missing(degreeType)} · ${missing(city)}, ${missing(state)} · ${sourceUrl} · Decision Rank ${missing(decisionRank)}</p>
    <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
    ${profileActionPanel}
    ${snapshotMarkup}
    ${nodeSectionMarkup}
    <div class="detail-grid" style="margin-top:12px">
      ${legacyLocalStatus}
      ${adminPanels}
    </div>
    ${item ? renderDossierForm(item) : ''}
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
  $('downloadProfileDossierState')?.addEventListener('click', downloadDossierExport);
}

function detailPanel(title, panelRows) {
  return `<div class="panel"><h3>${title}</h3>${panelRows.map(([k,v])=>`<p><strong>${k}:</strong> ${missing(v)}</p>`).join('')}</div>`;
}

function renderMethodology() {
  const readinessRows = Object.entries(payload.copy.curated_list_readiness || {}).map(([label, text]) => ({label, text}));
  const methodologyRows = rows('scoring_methodology');
  const strategyRows = STRATEGY_OPTIONS.map(value => ({
    strategy: STRATEGY_DETAILS[value].label,
    summary: STRATEGY_DETAILS[value].summary,
    changes: STRATEGY_DETAILS[value].changes,
  }));
  $('methodology').innerHTML = `<h2>Methodology</h2>
    <div class="caveat">${payload.copy.aamc_grid_caveat}</div>
    <div class="panel" style="margin-bottom:12px">
      <h3>Review Strategy Options</h3>
      <p>The review strategy changes how the guided intake narrows schools for first-pass review. It does not change source data, and it is not a school-specific acceptance prediction.</p>
      ${table([
        {key:'strategy', label:'Strategy', render:r=>missing(r.strategy)},
        {key:'summary', label:'What it means', render:r=>missing(r.summary)},
        {key:'changes', label:'What changes in the site', render:r=>missing(r.changes)},
      ], strategyRows, 'strategyMethodology')}
    </div>
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

function render(options={}) {
  if (ensureDefaultRoute()) return;
  currentRoute = parseRoute();
  const pathChanged = currentRoute.path !== lastRenderedPath;
  const scrollSnapshot = options.preserveScroll && !pathChanged ? captureScrollSnapshot() : null;
  if (routeHash(currentRoute.path) !== window.location.hash && window.location.hash) {
    window.location.replace(routeHash(currentRoute.path));
    return;
  }
  $('summaryText').textContent = `${payload.meta.active_school_count} active schools · ${payload.meta.site_mode} mode`;
  setActiveNav(currentRoute.path);
  setActiveSection(currentRoute.view);
  if (currentRoute.view === 'intake') renderIntake();
  if (currentRoute.view === 'rankings') renderRankings();
  if (currentRoute.view === 'consideringList') renderConsideringList();
  if (currentRoute.view === 'dossiers') renderDossiers();
  if (currentRoute.view === 'research') renderResearch();
  if (currentRoute.view === 'applicationList') renderApplicationList();
  if (currentRoute.view === 'lists') renderLists();
  if (currentRoute.view === 'listDetail') renderListDetail();
  if (currentRoute.view === 'compare') renderCompare();
  if (currentRoute.view === 'profile') renderProfile();
  if (currentRoute.view === 'methodology') renderMethodology();
  if (currentRoute.view === 'sources') renderSources();
  if (currentRoute.view === 'admin') renderAdmin();
  if (pathChanged) {
    lastRenderedPath = currentRoute.path;
    requestAnimationFrame(() => {
      window.scrollTo({top: 0, left: 0});
      document.querySelectorAll('.view.active, .intake-form, .intake-results, .rankings-menu, .rankings-results, .table-wrap').forEach(element => {
        element.scrollTop = 0;
        element.scrollLeft = 0;
      });
      if (currentRoute.view === 'intake') updateIntakePaneHeight();
      if (currentRoute.view === 'rankings') updateRankingsPaneHeight();
    });
  } else if (scrollSnapshot) {
    restoreScrollSnapshot(scrollSnapshot);
  }
}

window.addEventListener('hashchange', render);
window.addEventListener('resize', () => {
  if (currentRoute.view === 'intake') updateIntakePaneHeight();
  if (currentRoute.view === 'rankings') updateRankingsPaneHeight();
});
$('globalSearch').addEventListener('input', render);
document.addEventListener('click', event => {
  const actionButton = event.target.closest('[data-action]');
  if (!actionButton) return;
  const action = actionButton.dataset.action;
  const id = actionButton.dataset.schoolId;
  event.preventDefault();
  if (action === 'download-intake-json') {
    downloadJson('guided_intake_export.json', intakeExportRecord());
    return;
  }
  if (action === 'reset-intake') {
    resetIntakeState();
    render({preserveScroll: true});
    return;
  }
  if (action === 'toggle-guided-group') {
    const groupId = actionButton.dataset.groupId;
    if (groupId) {
      guidedGroupOpenState[groupId] = !guidedGroupOpenState[groupId];
      persistGuidedGroupOpenState();
      render({preserveScroll: true});
    }
    return;
  }
  if (action === 'clear-compare') {
    compareState.selectedIds = [];
    render();
    return;
  }
  if (!id) return;
  if (action === 'set-application-status') {
    setApplicationStatus(id, actionButton.dataset.applicationStatus || '');
    render();
    return;
  }
  if (action === 'hide-school') {
    const reason = window.prompt('Reason for hiding this school?', 'Not a current fit');
    setSchoolVisibility(id, 'hidden', reason === null ? 'Not a current fit' : reason);
    render();
  }
  if (action === 'restore-school') {
    setSchoolVisibility(id, 'visible');
    render();
  }
  if (action === 'add-compare') {
    setCompareSelected(id, true);
    render();
  }
  if (action === 'remove-compare') {
    setCompareSelected(id, false);
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
  const intakeField = event.target.closest('[data-intake-field]');
  if (intakeField) {
    setIntakeField(intakeField.dataset.intakeField, intakeField.value);
    render({preserveScroll: true});
    return;
  }
  const intakeMulti = event.target.closest('[data-intake-multi]');
  if (intakeMulti) {
    toggleIntakeArrayField(intakeMulti.dataset.intakeMulti, intakeMulti.value, intakeMulti.checked);
    render({preserveScroll: true});
    return;
  }
  const dossierField = event.target.closest('[data-dossier-field]');
  if (!dossierField) return;
  updateDossierField(dossierField.dataset.dossierSchool, dossierField.dataset.dossierField, dossierField.value);
  if (['intake', 'rankings', 'consideringList', 'dossiers', 'research', 'applicationList', 'compare', 'profile'].includes(currentRoute.view)) render();
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
