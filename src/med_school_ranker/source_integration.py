from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from statistics import median
from typing import Iterable

from med_school_ranker.paths import (
    ADMISSIONS_POLICIES_CSV,
    ADMISSIONS_STATS_CANDIDATES_CSV,
    ADMISSIONS_STATS_CONFLICTS_CSV,
    ADMISSIONS_STATS_CSV,
    COST_AND_DEBT_CANDIDATES_CSV,
    COST_AND_DEBT_CSV,
    COST_AND_DEBT_REVIEW_CSV,
    DATA,
    LETTER_REQUIREMENTS_CSV,
    MANUAL_DATA,
    MASTER_CSV,
    OUT,
    ROOT,
    SOURCE_INTEGRATION_REPORT_CSV,
    SOURCE_MATCH_OVERRIDES_CSV,
    SOURCE_MATCH_REVIEW_CSV,
    SOURCE_REVIEW_QUEUE_CSV,
)


SOURCE_TABLE_DIR = DATA / "source_tables"
SOURCE_DIFFS_DIR = OUT / "source_diffs"
SOURCE_LAST_CHECKED_DEFAULT = "2026-06-05"
MATCH_CACHE: dict[tuple[str, str, str], "MatchResult"] = {}

PUBLISHED_STATS_SOURCE_KEYS = ["prospectivedoctor", "shemmassian", "matchguy"]
ALL_STATS_SOURCE_KEYS = PUBLISHED_STATS_SOURCE_KEYS + ["cycletrack_acceptance_median"]
SAFE_MATCH_LABELS = {"exact", "high_confidence", "override_accept"}
ALLOWED_OVERRIDE_ACTIONS = {"accept_match", "reject_match", "force_no_match", "ignore_source_row"}
PUBLISHED_SOURCE_INFO = {
    "prospectivedoctor": ("ProspectiveDoctor", "https://www.prospectivedoctor.com/gpa-and-mcat/"),
    "shemmassian": (
        "Shemmassian",
        "https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school",
    ),
    "matchguy": ("The Match Guy", "https://thematchguy.com/average-mcat-gpa-medical-school-acceptance/"),
}

SOURCE_REVIEW_QUEUE_COLUMNS = [
    "review_id",
    "review_status",
    "review_reason",
    "source_table",
    "source_row_number",
    "source_school_name",
    "source_state",
    "source_degree_type",
    "school_id",
    "school_name",
    "match_score",
    "second_match_score",
    "recommended_action",
    "created_date",
    "resolved_date",
    "resolution_notes",
]

SOURCE_MATCH_REVIEW_COLUMNS = [
    "source_table",
    "source_row_number",
    "source_school_name",
    "source_state",
    "source_degree_type",
    "best_school_id",
    "best_school_name",
    "best_match_score",
    "second_school_id",
    "second_school_name",
    "second_match_score",
    "match_label",
    "review_reason",
    "recommended_action",
]

SOURCE_INTEGRATION_REPORT_COLUMNS = [
    "severity",
    "category",
    "item",
    "count",
    "message",
    "next_action",
]

COST_AND_DEBT_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "tuition_year",
    "academic_year",
    "in_state_tuition_fees_insurance",
    "out_state_tuition_fees_insurance",
    "estimated_coa_in_state",
    "estimated_coa_out_state",
    "expected_scholarship",
    "application_fee",
    "secondary_fee",
    "deposit_amount",
    "average_grad_indebtedness",
    "residency_assumption",
    "debt_burden_score",
    "attendance_cost_score",
    "source_name",
    "source_url",
    "source_snapshot_path",
    "source_publication_date",
    "source_last_checked",
    "data_confidence",
    "source_table",
    "source_row_number",
    "match_score",
    "match_label",
    "notes",
]

ADMISSIONS_POLICIES_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "policy_category",
    "policy_field",
    "policy_value",
    "policy_value_type",
    "source_name",
    "source_url",
    "source_snapshot_path",
    "source_publication_date",
    "source_last_checked",
    "data_confidence",
    "source_table",
    "source_row_number",
    "match_score",
    "match_label",
    "notes",
]

LETTER_REQUIREMENTS_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "requirement_type",
    "requirement_url",
    "source_name",
    "source_url",
    "source_last_checked",
    "data_confidence",
    "source_table",
    "source_row_number",
    "match_score",
    "match_label",
    "notes",
]

ADMISSIONS_STATS_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "stats_cohort_year",
    "metric_population",
    "metric_type",
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
    "source_name",
    "source_url",
    "source_snapshot_path",
    "source_publication_date",
    "source_last_checked",
    "data_confidence",
    "notes",
]

ADMISSIONS_STATS_CANDIDATES_COLUMNS = [
    "candidate_id",
    "school_id",
    "school_name",
    "degree_type",
    "source_key",
    "source_name",
    "source_url",
    "value_url",
    "source_row_number",
    "source_school_name",
    "metric_context",
    "gpa",
    "mcat",
    "agreement_label",
    "data_confidence",
    "match_score",
    "match_label",
    "notes",
]

ADMISSIONS_STATS_CONFLICTS_COLUMNS = [
    "cluster_id",
    "canonical_school_name",
    "school_id",
    "sources_present",
    "source_count",
    "agreement_label",
    "gpa_values",
    "gpa_range",
    "gpa_spread",
    "mcat_values",
    "mcat_range",
    "mcat_spread",
    "metric_definition_note",
    "recommended_action",
]

COST_AND_DEBT_CANDIDATES_COLUMNS = [
    "school_id",
    "school_name",
    "state_abbrev",
    "in_state_tuition_fees_insurance",
    "out_state_tuition_fees_insurance",
    "estimated_coa_in_state",
    "estimated_coa_out_state",
    "tuition_source_url",
    "tuition_source_name",
    "aamc_source_row_number",
    "aamc_school_name",
    "match_score",
    "match_label",
    "second_match_score",
    "safety_label",
    "notes",
]

COST_AND_DEBT_REVIEW_COLUMNS = [
    "source_table",
    "source_row_number",
    "source_school_name",
    "source_state",
    "school_id",
    "school_name",
    "match_score",
    "second_match_score",
    "review_reason",
    "recommended_action",
    "notes",
]

SOURCE_COLUMNS = [
    "source_name",
    "url",
    "used_for",
    "source_page_updated_or_info_as_of",
    "source_last_checked",
    "notes",
]

US_STATE_NAMES_TO_ABBREV = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "district of columbia": "DC",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
}

US_STATE_ABBREVS = set(US_STATE_NAMES_TO_ABBREV.values())


@dataclass(frozen=True)
class SchoolRecord:
    school_id: str
    school_name: str
    degree_type: str
    state_abbrev: str
    active: bool
    row: dict[str, str]


@dataclass(frozen=True)
class MatchResult:
    school: SchoolRecord | None
    score: float
    label: str
    second_school: SchoolRecord | None
    second_score: float
    review_reason: str
    ignored: bool = False

    @property
    def is_safe(self) -> bool:
        return self.school is not None and self.label in SAFE_MATCH_LABELS


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def clean(value: object) -> str:
    return str(value or "").strip()


def is_truthy(value: object) -> bool:
    return clean(value).lower() in {"1", "true", "t", "yes", "y"}


def parse_float(value: object) -> float | None:
    text = clean(value).replace("$", "").replace(",", "").replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def fmt_decimal(value: float | None, digits: int = 3) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def fmt_currency(value: object) -> str:
    number = parse_float(value)
    if number is None:
        return ""
    return str(int(number))


def state_abbrev(value: object) -> str:
    text = clean(value)
    upper = text.upper()
    if upper in US_STATE_ABBREVS or re.fullmatch(r"[A-Z]{2}", upper):
        return upper
    return US_STATE_NAMES_TO_ABBREV.get(text.lower(), "")


@lru_cache(maxsize=10000)
def normalize_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"\b(u\.s\.|us)\b", " united states ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\b(the|of|at|and|for)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def ratio(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def token_set_ratio(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return 0.0
    if left == right:
        return 1.0
    intersection = sorted(left_tokens & right_tokens)
    union = left_tokens | right_tokens
    jaccard = len(intersection) / len(union)
    return max(
        ratio(left, right),
        ratio(" ".join(sorted(left_tokens)), " ".join(sorted(right_tokens))),
        jaccard,
    )


@lru_cache(maxsize=50000)
def school_match_score(source_name: str, school_name: str) -> float:
    return token_set_ratio(normalize_name(source_name), normalize_name(school_name))


def load_school_master() -> dict[str, SchoolRecord]:
    schools: dict[str, SchoolRecord] = {}
    for row in read_csv(MASTER_CSV):
        school_id = clean(row.get("school_id"))
        if not school_id:
            continue
        schools[school_id] = SchoolRecord(
            school_id=school_id,
            school_name=clean(row.get("school_name")),
            degree_type=clean(row.get("degree_type")),
            state_abbrev=state_abbrev(row.get("state_abbrev") or row.get("state")),
            active=is_truthy(row.get("active_in_universe")),
            row=row,
        )
    return schools


def load_overrides() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(SOURCE_MATCH_OVERRIDES_CSV):
        action = clean(row.get("override_action"))
        if not action:
            continue
        rows.append(row)
    return rows


def find_override(
    overrides: list[dict[str, str]],
    source_table: str,
    source_row_number: str,
    source_school_name: str,
) -> dict[str, str] | None:
    source_name_norm = normalize_name(source_school_name)
    candidates = [
        row
        for row in overrides
        if clean(row.get("source_table")) == source_table
        and clean(row.get("source_row_number")) == clean(source_row_number)
    ]
    if not candidates:
        return None
    for row in candidates:
        override_name = clean(row.get("source_school_name"))
        if not override_name or normalize_name(override_name) == source_name_norm:
            return row
    return candidates[0]


def match_school(
    source_table: str,
    source_row_number: str,
    source_school_name: str,
    source_state: str,
    source_degree_type: str,
    schools_by_id: dict[str, SchoolRecord],
    overrides: list[dict[str, str]],
) -> MatchResult:
    override = find_override(overrides, source_table, source_row_number, source_school_name)
    if override:
        action = clean(override.get("override_action"))
        if action == "ignore_source_row":
            return MatchResult(None, 0.0, "ignored", None, 0.0, "manual_ignore", ignored=True)
        if action == "force_no_match":
            return MatchResult(None, 0.0, "no_match", None, 0.0, "manual_force_no_match")
        if action == "accept_match":
            school = schools_by_id.get(clean(override.get("school_id")))
            if school:
                return MatchResult(school, 1.0, "override_accept", None, 0.0, "manual_accept")
            return MatchResult(None, 0.0, "review", None, 0.0, "manual_accept_missing_school_id")

    wanted_state = state_abbrev(source_state)
    wanted_degree = clean(source_degree_type).upper()
    cache_key = (normalize_name(source_school_name), wanted_state, wanted_degree)
    if not override and cache_key in MATCH_CACHE:
        return MATCH_CACHE[cache_key]

    candidates = [
        school
        for school in schools_by_id.values()
        if school.active
        and (not wanted_state or school.state_abbrev == wanted_state)
        and (not wanted_degree or school.degree_type.upper() == wanted_degree)
    ]
    if not candidates:
        result = MatchResult(None, 0.0, "no_match", None, 0.0, "no_compatible_active_school")
        if not override:
            MATCH_CACHE[cache_key] = result
        return result

    scored = sorted(
        ((school_match_score(source_school_name, school.school_name), school) for school in candidates),
        key=lambda item: (-item[0], item[1].school_id),
    )
    top_score, top_school = scored[0]
    second_score, second_school = scored[1] if len(scored) > 1 else (0.0, None)
    exact_name = normalize_name(source_school_name) == normalize_name(top_school.school_name)
    gap = top_score - second_score

    if exact_name and second_score < 1.0:
        label = "exact"
        review_reason = ""
    elif top_score >= 0.92 and gap >= 0.03:
        label = "high_confidence"
        review_reason = ""
    elif top_score < 0.75:
        label = "no_match"
        review_reason = "low_match_score"
    else:
        label = "review"
        review_reason = "ambiguous_match_gap" if gap < 0.03 else "below_safe_threshold"

    if override and clean(override.get("override_action")) == "reject_match":
        label = "review"
        review_reason = "manual_reject_match"

    result = MatchResult(top_school, top_score, label, second_school, second_score, review_reason)
    if not override:
        MATCH_CACHE[cache_key] = result
    return result


def match_review_row(
    source_table: str,
    source_row_number: str,
    source_school_name: str,
    source_state: str,
    source_degree_type: str,
    match: MatchResult,
    recommended_action: str,
) -> dict[str, str]:
    return {
        "source_table": source_table,
        "source_row_number": source_row_number,
        "source_school_name": source_school_name,
        "source_state": source_state,
        "source_degree_type": source_degree_type,
        "best_school_id": match.school.school_id if match.school else "",
        "best_school_name": match.school.school_name if match.school else "",
        "best_match_score": fmt_decimal(match.score),
        "second_school_id": match.second_school.school_id if match.second_school else "",
        "second_school_name": match.second_school.school_name if match.second_school else "",
        "second_match_score": fmt_decimal(match.second_score),
        "match_label": match.label,
        "review_reason": match.review_reason,
        "recommended_action": recommended_action,
    }


def review_queue_row(
    source_table: str,
    source_row_number: str,
    source_school_name: str,
    source_state: str,
    source_degree_type: str,
    match: MatchResult,
    review_reason: str,
    recommended_action: str,
) -> dict[str, str]:
    review_id = re.sub(
        r"[^a-z0-9_]+",
        "_",
        f"{source_table}_{source_row_number}_{source_school_name}_{review_reason}".lower(),
    ).strip("_")[:180]
    return {
        "review_id": review_id,
        "review_status": "open",
        "review_reason": review_reason,
        "source_table": source_table,
        "source_row_number": source_row_number,
        "source_school_name": source_school_name,
        "source_state": source_state,
        "source_degree_type": source_degree_type,
        "school_id": match.school.school_id if match.school else "",
        "school_name": match.school.school_name if match.school else "",
        "match_score": fmt_decimal(match.score),
        "second_match_score": fmt_decimal(match.second_score),
        "recommended_action": recommended_action,
        "created_date": SOURCE_LAST_CHECKED_DEFAULT,
        "resolved_date": "",
        "resolution_notes": "",
    }


def preserve_review_queue(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = {row.get("review_id", ""): row for row in read_csv(SOURCE_REVIEW_QUEUE_CSV)}
    output: list[dict[str, str]] = []
    generated_ids = set()
    for row in rows:
        review_id = row["review_id"]
        prior = existing.get(review_id, {})
        merged = dict(row)
        for field in ["review_status", "resolved_date", "resolution_notes"]:
            if clean(prior.get(field)):
                merged[field] = prior[field]
        output.append(merged)
        generated_ids.add(review_id)

    for review_id, prior in existing.items():
        if review_id and review_id not in generated_ids and clean(prior.get("review_status")) in {"resolved", "closed"}:
            output.append(prior)

    return sorted(output, key=lambda row: (row.get("review_status", ""), row.get("review_id", "")))


def source_last_checked(row: dict[str, str]) -> str:
    return clean(row.get("source_last_checked")) or SOURCE_LAST_CHECKED_DEFAULT


def value_type(value: str) -> str:
    text = clean(value)
    if not text:
        return ""
    if text.startswith(("http://", "https://")):
        return "url"
    if text.startswith("$") or re.fullmatch(r"\$?[0-9][0-9,]*(\.[0-9]+)?", text):
        return "number"
    if text.upper() in {"TRUE", "FALSE", "YES", "NO", "N/A"}:
        return "text"
    return "text"


def split_values(value: str) -> list[float]:
    values = []
    for part in re.split(r"[;|]", clean(value)):
        number = parse_float(part)
        if number is not None:
            values.append(number)
    return values


def merge_source_registry() -> Path:
    source_path = DATA / "sources.csv"
    rows = read_csv(source_path)
    seen = {(clean(row.get("source_name")), clean(row.get("url"))) for row in rows}
    for additions_path in [
        SOURCE_TABLE_DIR / "source_universe_aamc_msar_reports.csv",
        SOURCE_TABLE_DIR / "source_universe_additions.csv",
    ]:
        for row in read_csv(additions_path):
            normalized = {
                "source_name": clean(row.get("source_name")),
                "url": clean(row.get("url")),
                "used_for": clean(row.get("used_for")),
                "source_page_updated_or_info_as_of": clean(row.get("source_page_updated_or_info_as_of")),
                "source_last_checked": source_last_checked(row),
                "notes": clean(row.get("notes")),
            }
            key = (normalized["source_name"], normalized["url"])
            if normalized["source_name"] and normalized["url"] and key not in seen:
                rows.append(normalized)
                seen.add(key)

    write_csv(source_path, SOURCE_COLUMNS, rows)
    return source_path


def has_nonzero_cost(row: dict[str, str]) -> bool:
    return any(
        (parse_float(row.get(field)) or 0) > 0
        for field in [
            "in_state_tuition_fees_insurance",
            "out_state_tuition_fees_insurance",
            "estimated_coa_in_state",
            "estimated_coa_out_state",
        ]
    )


def build_cost_outputs(
    schools_by_id: dict[str, SchoolRecord],
) -> tuple[list[Path], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    join_rows = read_csv(SOURCE_TABLE_DIR / "aamc_msar_tuition_school_master_join_candidates.csv")
    patch_rows = read_csv(SOURCE_TABLE_DIR / "aamc_msar_tuition_school_master_patch_candidates.csv")
    raw_rows = read_csv(SOURCE_TABLE_DIR / "aamc_msar_tuition_fees_insurance.csv")
    join_by_source_row = {clean(row.get("aamc_source_row_number")): row for row in join_rows}
    raw_by_source_row = {clean(row.get("source_row_number")): row for row in raw_rows}

    normalized: list[dict[str, str]] = []
    candidates: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []
    queue_rows: list[dict[str, str]] = []

    safe_school_ids: set[str] = set()
    patch_source_rows = {clean(row.get("aamc_source_row_number")) for row in patch_rows}
    for row in patch_rows:
        source_row_number = clean(row.get("aamc_source_row_number"))
        join_row = join_by_source_row.get(source_row_number, {})
        raw_row = raw_by_source_row.get(source_row_number, {})
        school_id = clean(row.get("school_id"))
        school = schools_by_id.get(school_id)
        match_score = parse_float(join_row.get("match_score") or row.get("match_score")) or 0.0
        second_score = parse_float(join_row.get("second_match_score")) or 0.0
        gap = match_score - second_score
        match_label = clean(join_row.get("match_label") or row.get("match_label"))
        has_cost = has_nonzero_cost(row)
        is_active_md = bool(school and school.active and school.degree_type == "MD")
        is_safe = has_cost and is_active_md and (match_label == "exact" or (match_label == "high_confidence" and gap >= 0.03))
        safety_label = "safe" if is_safe else "review"
        notes = clean(row.get("notes") or join_row.get("notes"))
        if not has_cost:
            notes = "; ".join(part for part in [notes, "all reported cost fields are zero"] if part)
        if match_label == "high_confidence" and gap < 0.03:
            notes = "; ".join(part for part in [notes, "ambiguous high-confidence match"] if part)
        if not is_active_md:
            notes = "; ".join(part for part in [notes, "matched school is not an active MD row"] if part)

        candidates.append(
            {
                "school_id": school_id,
                "school_name": clean(row.get("school_name")),
                "state_abbrev": clean(row.get("state_abbrev")),
                "in_state_tuition_fees_insurance": fmt_currency(row.get("in_state_tuition_fees_insurance")),
                "out_state_tuition_fees_insurance": fmt_currency(row.get("out_state_tuition_fees_insurance")),
                "estimated_coa_in_state": fmt_currency(row.get("estimated_coa_in_state")),
                "estimated_coa_out_state": fmt_currency(row.get("estimated_coa_out_state")),
                "tuition_source_url": clean(row.get("tuition_source_url")),
                "tuition_source_name": clean(row.get("tuition_source_name")),
                "aamc_source_row_number": source_row_number,
                "aamc_school_name": clean(row.get("aamc_school_name")),
                "match_score": fmt_decimal(match_score),
                "match_label": match_label,
                "second_match_score": fmt_decimal(second_score),
                "safety_label": safety_label,
                "notes": notes,
            }
        )

        if is_safe and school:
            safe_school_ids.add(school_id)
            normalized.append(
                {
                    "school_id": school.school_id,
                    "school_name": school.school_name,
                    "degree_type": school.degree_type,
                    "tuition_year": clean(raw_row.get("report_year")),
                    "academic_year": clean(raw_row.get("academic_year")),
                    "in_state_tuition_fees_insurance": fmt_currency(row.get("in_state_tuition_fees_insurance")),
                    "out_state_tuition_fees_insurance": fmt_currency(row.get("out_state_tuition_fees_insurance")),
                    "estimated_coa_in_state": fmt_currency(row.get("estimated_coa_in_state")),
                    "estimated_coa_out_state": fmt_currency(row.get("estimated_coa_out_state")),
                    "expected_scholarship": "",
                    "application_fee": "",
                    "secondary_fee": "",
                    "deposit_amount": "",
                    "average_grad_indebtedness": "",
                    "residency_assumption": "AAMC in-state and out-of-state cost rows preserved separately.",
                    "debt_burden_score": "",
                    "attendance_cost_score": "",
                    "source_name": clean(raw_row.get("source_name") or row.get("tuition_source_name")),
                    "source_url": clean(raw_row.get("source_url") or row.get("tuition_source_url")),
                    "source_snapshot_path": clean(raw_row.get("pdf_file")),
                    "source_publication_date": clean(raw_row.get("report_year")),
                    "source_last_checked": source_last_checked(raw_row),
                    "data_confidence": "aamc_public_report_safe_match",
                    "source_table": "aamc_msar_tuition_fees_insurance.csv",
                    "source_row_number": source_row_number,
                    "match_score": fmt_decimal(match_score),
                    "match_label": match_label,
                    "notes": "Canonical only because match is active US MD, nonzero cost, and passes second-match gap review.",
                }
            )
        else:
            reason = "unsafe_cost_match"
            if not has_cost:
                reason = "all_zero_cost_row"
            elif match_label == "high_confidence" and gap < 0.03:
                reason = "ambiguous_high_confidence_cost_match"
            elif not is_active_md:
                reason = "not_active_md_cost_row"
            review_rows.append(
                {
                    "source_table": "aamc_msar_tuition_school_master_patch_candidates.csv",
                    "source_row_number": source_row_number,
                    "source_school_name": clean(row.get("aamc_school_name")),
                    "source_state": clean(join_row.get("aamc_state") or row.get("state_abbrev")),
                    "school_id": school_id,
                    "school_name": clean(row.get("school_name")),
                    "match_score": fmt_decimal(match_score),
                    "second_match_score": fmt_decimal(second_score),
                    "review_reason": reason,
                    "recommended_action": "review source row and add source_match_override if safe",
                    "notes": notes,
                }
            )
            queue_rows.append(
                review_queue_row(
                    "aamc_msar_tuition_school_master_patch_candidates.csv",
                    source_row_number,
                    clean(row.get("aamc_school_name")),
                    clean(join_row.get("aamc_state") or row.get("state_abbrev")),
                    "MD",
                    MatchResult(school, match_score, match_label, None, second_score, reason) if school else MatchResult(None, match_score, match_label, None, second_score, reason),
                    reason,
                    "review cost match",
                )
            )

    for row in join_rows:
        source_row_number = clean(row.get("aamc_source_row_number"))
        if source_row_number in patch_source_rows:
            continue
        reason = clean(row.get("notes")) or clean(row.get("match_label")) or "not_in_patch_candidates"
        review_rows.append(
            {
                "source_table": "aamc_msar_tuition_school_master_join_candidates.csv",
                "source_row_number": source_row_number,
                "source_school_name": clean(row.get("aamc_school_name")),
                "source_state": clean(row.get("aamc_state")),
                "school_id": clean(row.get("master_school_id")),
                "school_name": clean(row.get("master_school_name")),
                "match_score": fmt_decimal(parse_float(row.get("match_score"))),
                "second_match_score": fmt_decimal(parse_float(row.get("second_match_score"))),
                "review_reason": "join_row_not_safe_for_patch",
                "recommended_action": "review if school should enter canonical cost table",
                "notes": reason,
            }
        )

    for school in schools_by_id.values():
        if not school.active:
            continue
        if school.school_id in safe_school_ids:
            continue
        if school.degree_type not in {"MD", "DO"}:
            continue
        review_rows.append(
            {
                "source_table": "school_master.csv",
                "source_row_number": "",
                "source_school_name": "",
                "source_state": school.state_abbrev,
                "school_id": school.school_id,
                "school_name": school.school_name,
                "match_score": "",
                "second_match_score": "",
                "review_reason": f"{school.degree_type.lower()}_missing_safe_cost_row",
                "recommended_action": "find or confirm cost source",
                "notes": "No canonical AAMC cost row is currently safe for this active school.",
            }
        )

    normalized.sort(key=lambda row: (row["school_name"], row["school_id"]))
    candidates.sort(key=lambda row: (row["safety_label"], row["aamc_source_row_number"], row["school_name"]))
    review_rows.sort(key=lambda row: (row["review_reason"], row["school_name"], row["source_row_number"]))
    write_csv(COST_AND_DEBT_CSV, COST_AND_DEBT_COLUMNS, normalized)
    write_csv(COST_AND_DEBT_CANDIDATES_CSV, COST_AND_DEBT_CANDIDATES_COLUMNS, candidates)
    write_csv(COST_AND_DEBT_REVIEW_CSV, COST_AND_DEBT_REVIEW_COLUMNS, review_rows)
    return [COST_AND_DEBT_CSV, COST_AND_DEBT_CANDIDATES_CSV, COST_AND_DEBT_REVIEW_CSV], review_rows, queue_rows, candidates


def source_value_fields(row: dict[str, str]) -> list[str]:
    metadata = {
        "source_key",
        "source_name",
        "source_url",
        "pdf_file",
        "source_row_number",
        "stream_index",
        "row_y",
        "state",
        "school_name_raw",
        "school_name_clean",
        "notes",
    }
    return [field for field in row if field not in metadata and clean(row.get(field))]


def build_policy_outputs(
    schools_by_id: dict[str, SchoolRecord],
    overrides: list[dict[str, str]],
) -> tuple[list[Path], list[dict[str, str]], list[dict[str, str]]]:
    policy_tables = [
        "aamc_msar_admission_policies.csv",
        "aamc_msar_applications_accepted.csv",
        "aamc_msar_community_college_coursework.csv",
        "aamc_msar_daca_policies.csv",
        "aamc_msar_deposit_information.csv",
        "aamc_msar_gender_sexual_minority_support.csv",
        "aamc_msar_interview_policies.csv",
        "aamc_msar_mcat_dates.csv",
        "aamc_msar_mission_statements.csv",
        "aamc_msar_premed_course_requirements.csv",
        "aamc_msar_preview_policies.csv",
        "aamc_msar_secondary_application.csv",
        "aamc_msar_transfer_policies.csv",
        "aamc_msar_waitlist_procedures.csv",
    ]
    rows_out: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []
    match_review_rows: list[dict[str, str]] = []

    for table_name in policy_tables:
        source_table = SOURCE_TABLE_DIR / table_name
        for row in read_csv(source_table):
            source_row_number = clean(row.get("source_row_number"))
            source_school_name = clean(row.get("school_name_clean") or row.get("school_name_raw"))
            source_state = clean(row.get("state"))
            match = match_school(table_name, source_row_number, source_school_name, source_state, "MD", schools_by_id, overrides)
            if match.ignored:
                continue
            fields = source_value_fields(row)
            if not fields:
                continue
            if not match.is_safe:
                match_review_rows.append(
                    match_review_row(table_name, source_row_number, source_school_name, source_state, "MD", match, "review source match")
                )
                review_rows.append(
                    review_queue_row(
                        table_name,
                        source_row_number,
                        source_school_name,
                        source_state,
                        "MD",
                        match,
                        match.review_reason or "unsafe_policy_match",
                        "review source match",
                    )
                )
                continue

            assert match.school is not None
            for field in fields:
                rows_out.append(
                    {
                        "school_id": match.school.school_id,
                        "school_name": match.school.school_name,
                        "degree_type": match.school.degree_type,
                        "policy_category": table_name.removeprefix("aamc_msar_").removesuffix(".csv"),
                        "policy_field": field,
                        "policy_value": clean(row.get(field)),
                        "policy_value_type": value_type(clean(row.get(field))),
                        "source_name": clean(row.get("source_name")),
                        "source_url": clean(row.get("source_url")),
                        "source_snapshot_path": clean(row.get("pdf_file")),
                        "source_publication_date": "2027 Entering Class",
                        "source_last_checked": source_last_checked(row),
                        "data_confidence": "aamc_public_report_safe_match",
                        "source_table": table_name,
                        "source_row_number": source_row_number,
                        "match_score": fmt_decimal(match.score),
                        "match_label": match.label,
                        "notes": clean(row.get("notes")),
                    }
                )

    rows_out.sort(key=lambda row: (row["school_name"], row["policy_category"], row["policy_field"], row["source_row_number"]))
    write_csv(ADMISSIONS_POLICIES_CSV, ADMISSIONS_POLICIES_COLUMNS, rows_out)
    return [ADMISSIONS_POLICIES_CSV], review_rows, match_review_rows


def requirement_degree(requirement_type: str) -> str:
    text = requirement_type.upper()
    if text.startswith("DO"):
        return "DO"
    if text.startswith("MD"):
        return "MD"
    return ""


def build_letter_requirement_outputs(
    schools_by_id: dict[str, SchoolRecord],
    overrides: list[dict[str, str]],
) -> tuple[list[Path], list[dict[str, str]], list[dict[str, str]]]:
    rows_out: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []
    match_review_rows: list[dict[str, str]] = []
    table_name = "cycletrack_lor_links.csv"

    for physical_row_number, row in enumerate(read_csv(SOURCE_TABLE_DIR / table_name), start=1):
        if is_truthy(row.get("is_missing_placeholder")) or not clean(row.get("requirement_url")):
            continue
        degree = requirement_degree(clean(row.get("requirement_type")))
        source_row_number = str(physical_row_number)
        source_school_name = clean(row.get("school_name_clean") or row.get("school_name_raw"))
        match = match_school(table_name, source_row_number, source_school_name, "", degree, schools_by_id, overrides)
        if match.ignored:
            continue
        if not match.is_safe:
            match_review_rows.append(
                match_review_row(table_name, source_row_number, source_school_name, "", degree, match, "review LOR link match")
            )
            review_rows.append(
                review_queue_row(
                    table_name,
                    source_row_number,
                    source_school_name,
                    "",
                    degree,
                    match,
                    match.review_reason or "unsafe_lor_match",
                    "review LOR link match",
                )
            )
            continue
        assert match.school is not None
        rows_out.append(
            {
                "school_id": match.school.school_id,
                "school_name": match.school.school_name,
                "degree_type": match.school.degree_type,
                "requirement_type": clean(row.get("requirement_type")),
                "requirement_url": clean(row.get("requirement_url")),
                "source_name": clean(row.get("source_name")),
                "source_url": clean(row.get("source_url")),
                "source_last_checked": source_last_checked(row),
                "data_confidence": "cycletrack_requirement_link_safe_match",
                "source_table": table_name,
                "source_row_number": source_row_number,
                "match_score": fmt_decimal(match.score),
                "match_label": match.label,
                "notes": clean(row.get("notes")),
            }
        )

    rows_out.sort(key=lambda row: (row["school_name"], row["requirement_type"]))
    write_csv(LETTER_REQUIREMENTS_CSV, LETTER_REQUIREMENTS_COLUMNS, rows_out)
    return [LETTER_REQUIREMENTS_CSV], review_rows, match_review_rows


def cluster_lookup(comparison_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in comparison_rows:
        names = [clean(row.get("canonical_school_name"))]
        for source_key in ALL_STATS_SOURCE_KEYS:
            names.extend(part.strip() for part in clean(row.get(f"{source_key}_school_name")).split(";") if part.strip())
        for name in names:
            normalized = normalize_name(name)
            if normalized and normalized not in lookup:
                lookup[normalized] = row
    return lookup


def published_values(row: dict[str, str], metric: str) -> tuple[list[float], list[str], list[str]]:
    values: list[float] = []
    names: list[str] = []
    urls: list[str] = []
    for source_key in PUBLISHED_STATS_SOURCE_KEYS:
        source_values = split_values(clean(row.get(f"{source_key}_{metric}")))
        if source_values:
            values.extend(source_values)
            source_name, source_url = PUBLISHED_SOURCE_INFO[source_key]
            names.append(source_name)
            url = clean(row.get(f"{source_key}_value_url")) or source_url
            if url:
                urls.append(url)
    return values, names, urls


def build_admissions_stats_outputs(
    schools_by_id: dict[str, SchoolRecord],
    overrides: list[dict[str, str]],
) -> tuple[list[Path], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    comparison_rows = read_csv(SOURCE_DIFFS_DIR / "mcat_gpa_source_comparison.csv")
    conflict_rows = read_csv(SOURCE_DIFFS_DIR / "mcat_gpa_conflicts.csv")
    comparable_rows = read_csv(SOURCE_TABLE_DIR / "all_comparable_mcat_gpa_sources.csv")
    clusters = cluster_lookup(comparison_rows)

    normalized_stats: list[dict[str, str]] = []
    candidates: list[dict[str, str]] = []
    conflicts_out: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []
    match_review_rows: list[dict[str, str]] = []

    cluster_matches: dict[str, MatchResult] = {}
    for row in comparison_rows:
        cluster_id = clean(row.get("cluster_id"))
        source_school_name = clean(row.get("canonical_school_name"))
        match = match_school("mcat_gpa_source_comparison.csv", cluster_id, source_school_name, "", "", schools_by_id, overrides)
        cluster_matches[cluster_id] = match
        agreement = clean(row.get("agreement_label"))
        has_published = any(clean(row.get(f"{source_key}_school_name")) for source_key in PUBLISHED_STATS_SOURCE_KEYS)
        if agreement not in {"close_agreement", "single_source"}:
            continue
        if not has_published:
            review_rows.append(
                review_queue_row(
                    "mcat_gpa_source_comparison.csv",
                    cluster_id,
                    source_school_name,
                    "",
                    "",
                    match,
                    "cycletrack_only_context",
                    "do not promote to canonical stats without a published source",
                )
            )
            continue
        if not match.is_safe:
            match_review_rows.append(
                match_review_row("mcat_gpa_source_comparison.csv", cluster_id, source_school_name, "", "", match, "review stats match")
            )
            review_rows.append(
                review_queue_row(
                    "mcat_gpa_source_comparison.csv",
                    cluster_id,
                    source_school_name,
                    "",
                    "",
                    match,
                    match.review_reason or "unsafe_stats_match",
                    "review stats match",
                )
            )
            continue

        gpa_values, source_names, urls = published_values(row, "gpa")
        mcat_values, mcat_source_names, mcat_urls = published_values(row, "mcat")
        source_names = sorted(set(source_names + mcat_source_names))
        urls = sorted(set(urls + mcat_urls))
        if not gpa_values and not mcat_values:
            continue
        assert match.school is not None
        confidence = "third_party_close_agreement" if agreement == "close_agreement" else "third_party_single_source"
        normalized_stats.append(
            {
                "school_id": match.school.school_id,
                "school_name": match.school.school_name,
                "degree_type": match.school.degree_type,
                "stats_cohort_year": "",
                "metric_population": "published school average",
                "metric_type": "provisional_third_party_median",
                "mcat_median_accepted": "",
                "mcat_median_matriculated": "",
                "mcat_mean_enrolled": fmt_decimal(median(mcat_values), 1) if mcat_values else "",
                "mcat_10th_percentile": "",
                "mcat_25th_percentile": "",
                "mcat_75th_percentile": "",
                "mcat_90th_percentile": "",
                "overall_gpa_median_accepted": "",
                "overall_gpa_median_matriculated": "",
                "overall_gpa_mean_enrolled": fmt_decimal(median(gpa_values), 2) if gpa_values else "",
                "science_gpa_mean_enrolled": "",
                "source_name": "; ".join(source_names),
                "source_url": "; ".join(urls),
                "source_snapshot_path": "",
                "source_publication_date": "",
                "source_last_checked": SOURCE_LAST_CHECKED_DEFAULT,
                "data_confidence": confidence,
                "notes": (
                    "Provisional median of comparable published third-party GPA/MCAT rows; "
                    "not official MSAR entering-class data."
                ),
            }
        )

    for physical_row_number, row in enumerate(comparable_rows, start=1):
        source_school_name = clean(row.get("school_name_clean") or row.get("school_name_raw"))
        cluster = clusters.get(normalize_name(source_school_name), {})
        source_key = clean(row.get("source_key"))
        match = match_school(
            "all_comparable_mcat_gpa_sources.csv",
            str(physical_row_number),
            source_school_name,
            "",
            "",
            schools_by_id,
            overrides,
        )
        data_confidence = "cycletrack_context_only" if source_key == "cycletrack_acceptance_median" else "third_party_candidate"
        if clean(cluster.get("agreement_label")):
            data_confidence = f"{data_confidence}_{clean(cluster.get('agreement_label'))}"
        candidates.append(
            {
                "candidate_id": f"{source_key}:{physical_row_number}",
                "school_id": match.school.school_id if match.school else "",
                "school_name": match.school.school_name if match.school else "",
                "degree_type": match.school.degree_type if match.school else "",
                "source_key": source_key,
                "source_name": clean(row.get("source_name")),
                "source_url": clean(row.get("source_url")),
                "value_url": clean(row.get("value_url")),
                "source_row_number": str(physical_row_number),
                "source_school_name": source_school_name,
                "metric_context": clean(row.get("metric_context")),
                "gpa": clean(row.get("gpa")),
                "mcat": clean(row.get("mcat")),
                "agreement_label": clean(cluster.get("agreement_label")),
                "data_confidence": data_confidence,
                "match_score": fmt_decimal(match.score),
                "match_label": match.label,
                "notes": clean(row.get("notes")),
            }
        )
        if not match.is_safe and not match.ignored:
            match_review_rows.append(
                match_review_row(
                    "all_comparable_mcat_gpa_sources.csv",
                    str(physical_row_number),
                    source_school_name,
                    "",
                    "",
                    match,
                    "review candidate stats match",
                )
            )

    for row in conflict_rows:
        cluster_id = clean(row.get("cluster_id"))
        match = cluster_matches.get(cluster_id) or match_school(
            "mcat_gpa_conflicts.csv",
            cluster_id,
            clean(row.get("canonical_school_name")),
            "",
            "",
            schools_by_id,
            overrides,
        )
        conflicts_out.append(
            {
                "cluster_id": cluster_id,
                "canonical_school_name": clean(row.get("canonical_school_name")),
                "school_id": match.school.school_id if match.school and match.is_safe else "",
                "sources_present": clean(row.get("sources_present")),
                "source_count": clean(row.get("source_count")),
                "agreement_label": clean(row.get("agreement_label")),
                "gpa_values": clean(row.get("gpa_values")),
                "gpa_range": clean(row.get("gpa_range")),
                "gpa_spread": clean(row.get("gpa_spread")),
                "mcat_values": clean(row.get("mcat_values")),
                "mcat_range": clean(row.get("mcat_range")),
                "mcat_spread": clean(row.get("mcat_spread")),
                "metric_definition_note": clean(row.get("metric_definition_note")),
                "recommended_action": "manual review before promoting to canonical admissions_stats",
            }
        )
        review_rows.append(
            review_queue_row(
                "mcat_gpa_conflicts.csv",
                cluster_id,
                clean(row.get("canonical_school_name")),
                "",
                match.school.degree_type if match.school else "",
                match,
                clean(row.get("agreement_label")) or "mcat_gpa_conflict",
                "resolve GPA/MCAT source conflict",
            )
        )

    normalized_stats.sort(key=lambda row: (row["school_name"], row["school_id"]))
    candidates.sort(key=lambda row: (row["source_key"], row["source_row_number"]))
    conflicts_out.sort(key=lambda row: int(row["cluster_id"]) if row["cluster_id"].isdigit() else 999999)
    write_csv(ADMISSIONS_STATS_CSV, ADMISSIONS_STATS_COLUMNS, normalized_stats)
    write_csv(ADMISSIONS_STATS_CANDIDATES_CSV, ADMISSIONS_STATS_CANDIDATES_COLUMNS, candidates)
    write_csv(ADMISSIONS_STATS_CONFLICTS_CSV, ADMISSIONS_STATS_CONFLICTS_COLUMNS, conflicts_out)
    return [ADMISSIONS_STATS_CSV, ADMISSIONS_STATS_CANDIDATES_CSV, ADMISSIONS_STATS_CONFLICTS_CSV], review_rows, match_review_rows, candidates


def report_row(severity: str, category: str, item: str, count: int, message: str, next_action: str) -> dict[str, str]:
    return {
        "severity": severity,
        "category": category,
        "item": item,
        "count": str(count),
        "message": message,
        "next_action": next_action,
    }


def build_report(
    cost_candidates: list[dict[str, str]],
    stats_candidates: list[dict[str, str]],
    review_queue_rows: list[dict[str, str]],
) -> Path:
    cost_safety = Counter(row.get("safety_label", "") or "unknown" for row in cost_candidates)
    review_reasons = Counter(row.get("review_reason", "") or "unknown" for row in review_queue_rows)
    rows = [
        report_row(
            "info",
            "cost",
            "canonical_rows",
            len(read_csv(COST_AND_DEBT_CSV)),
            "AAMC tuition rows promoted to canonical cost_and_debt.csv.",
            "Use these for cost awareness; do not infer scholarships or debt without later sources.",
        ),
        report_row(
            "warning",
            "cost",
            "review_candidates",
            cost_safety.get("review", 0),
            "AAMC tuition candidates held for match or zero-cost review.",
            "Resolve in Source Review Queue or source_match_overrides.csv.",
        ),
        report_row(
            "info",
            "admissions_stats",
            "canonical_rows",
            len(read_csv(ADMISSIONS_STATS_CSV)),
            "Third-party GPA/MCAT rows promoted only when agreement policy allows it.",
            "Treat as provisional until official school/MSAR data is reviewed.",
        ),
        report_row(
            "warning",
            "admissions_stats",
            "conflicts",
            len(read_csv(ADMISSIONS_STATS_CONFLICTS_CSV)),
            "GPA/MCAT comparison clusters have source disagreement.",
            "Review outputs/admissions_stats_conflicts.csv before promoting values.",
        ),
        report_row(
            "info",
            "source_review",
            "open_review_rows",
            len(review_queue_rows),
            "Rows needing source matching, conflict, or coverage review.",
            "Work data/manual/source_review_queue.csv and keep notes transparent.",
        ),
    ]
    for reason, count in sorted(review_reasons.items()):
        rows.append(
            report_row(
                "info",
                "source_review_reason",
                reason,
                count,
                "Open review row count by reason.",
                "Prioritize high-value rows before relying on ranking outputs.",
            )
        )
    write_csv(SOURCE_INTEGRATION_REPORT_CSV, SOURCE_INTEGRATION_REPORT_COLUMNS, rows)
    return SOURCE_INTEGRATION_REPORT_CSV


def validate_source_inputs() -> None:
    required = [
        SOURCE_TABLE_DIR / "aamc_msar_tuition_school_master_join_candidates.csv",
        SOURCE_TABLE_DIR / "aamc_msar_tuition_school_master_patch_candidates.csv",
        SOURCE_TABLE_DIR / "aamc_msar_tuition_fees_insurance.csv",
        SOURCE_TABLE_DIR / "all_comparable_mcat_gpa_sources.csv",
        SOURCE_DIFFS_DIR / "mcat_gpa_source_comparison.csv",
        SOURCE_DIFFS_DIR / "mcat_gpa_conflicts.csv",
        SOURCE_TABLE_DIR / "cycletrack_lor_links.csv",
    ]
    missing = [relative(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing source input(s): " + ", ".join(missing))


def build_source_integration() -> list[Path]:
    validate_source_inputs()
    MATCH_CACHE.clear()
    OUT.mkdir(parents=True, exist_ok=True)
    MANUAL_DATA.mkdir(parents=True, exist_ok=True)
    schools_by_id = load_school_master()
    overrides = load_overrides()

    written: list[Path] = []
    written.append(merge_source_registry())

    cost_paths, cost_review_rows, cost_queue_rows, cost_candidates = build_cost_outputs(schools_by_id)
    written.extend(cost_paths)

    policy_paths, policy_queue_rows, policy_match_review = build_policy_outputs(schools_by_id, overrides)
    written.extend(policy_paths)

    letter_paths, letter_queue_rows, letter_match_review = build_letter_requirement_outputs(schools_by_id, overrides)
    written.extend(letter_paths)

    stats_paths, stats_queue_rows, stats_match_review, stats_candidates = build_admissions_stats_outputs(schools_by_id, overrides)
    written.extend(stats_paths)

    source_review_rows = preserve_review_queue(cost_queue_rows + policy_queue_rows + letter_queue_rows + stats_queue_rows)
    write_csv(SOURCE_REVIEW_QUEUE_CSV, SOURCE_REVIEW_QUEUE_COLUMNS, source_review_rows)
    written.append(SOURCE_REVIEW_QUEUE_CSV)

    match_review_rows = policy_match_review + letter_match_review + stats_match_review
    match_review_rows.sort(key=lambda row: (row["source_table"], row["source_row_number"], row["source_school_name"]))
    write_csv(SOURCE_MATCH_REVIEW_CSV, SOURCE_MATCH_REVIEW_COLUMNS, match_review_rows)
    written.append(SOURCE_MATCH_REVIEW_CSV)

    written.append(build_report(cost_candidates, stats_candidates, source_review_rows))
    return written


def main() -> None:
    written = build_source_integration()
    for path in written:
        print(f"Wrote {relative(path)}")
