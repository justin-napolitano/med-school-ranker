from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from med_school_ranker.paths import (
    MASTER_CSV,
    OUT,
    PREFERENCES_CSV,
    RANKINGS_CSV,
    ROOT,
    SCENARIO_WEIGHTS_CSV,
)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def parse_number(value: str | None) -> Optional[float]:
    if value is None:
        return None
    value = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_weights(path: Path, group_key: str) -> Dict[str, List[Tuple[str, float]]]:
    grouped: Dict[str, List[Tuple[str, float]]] = {}
    for row in read_csv(path):
        group = row[group_key].strip()
        column = row["column_name"].strip()
        weight = parse_number(row.get("weight")) or 0
        if group and column and weight > 0:
            grouped.setdefault(group, []).append((column, weight))
    return grouped


def weighted_score(values: Dict[str, str], weights: Iterable[Tuple[str, float]]) -> Tuple[Optional[float], float]:
    numerator = 0.0
    denominator = 0.0
    possible = 0.0
    for column, weight in weights:
        possible += weight
        value = parse_number(values.get(column))
        if value is None:
            continue
        numerator += value * weight
        denominator += weight
    if denominator == 0:
        return None, 0.0
    return numerator / denominator, denominator / possible if possible else 0.0


def fmt(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def rank_values(rows: List[Dict[str, str]], score_column: str, rank_column: str) -> None:
    scored = [
        (idx, parse_number(row.get(score_column)))
        for idx, row in enumerate(rows)
        if parse_number(row.get(score_column)) is not None
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    rank = 0
    previous_score: Optional[float] = None
    for position, (idx, score) in enumerate(scored, start=1):
        if previous_score is None or score != previous_score:
            rank = position
            previous_score = score
        rows[idx][rank_column] = str(rank)


def dynamic_tier(admissions_score: Optional[float], attendance_score: Optional[float]) -> str:
    if admissions_score is None or attendance_score is None:
        return "Unscored"
    if admissions_score < 3 and attendance_score >= 8:
        return "Dream"
    if admissions_score < 5:
        return "Reach"
    if admissions_score < 7:
        return "Target"
    return "Likely"


def research_funnel(rank: Optional[float]) -> str:
    if rank is None:
        return ""
    if rank <= 35:
        return "25-35 application pool"
    if rank <= 40:
        return "40 researched schools"
    if rank <= 75:
        return "75 serious candidates"
    return "full universe"


def build_rankings() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    master_rows = read_csv(MASTER_CSV)
    preference_weights = load_weights(PREFERENCES_CSV, "score_group")
    scenario_weights = load_weights(SCENARIO_WEIGHTS_CSV, "scenario")

    scoring_columns = {
        column
        for weights in preference_weights.values()
        for column, _ in weights
        if not column.endswith("_score") or column not in {"admissions_score", "attendance_score"}
    }
    scoring_columns.update(
        column
        for weights in scenario_weights.values()
        for column, _ in weights
        if column not in {"admissions_score", "attendance_score", "overall_school_value", "data_completeness_score"}
    )

    output_rows: List[Dict[str, str]] = []
    for row in master_rows:
        values = dict(row)

        admissions_score, admissions_coverage = weighted_score(values, preference_weights.get("Admissions Score", []))
        attendance_score, attendance_coverage = weighted_score(values, preference_weights.get("Attendance Score", []))
        values["admissions_score"] = fmt(admissions_score)
        values["attendance_score"] = fmt(attendance_score)
        values["admissions_data_coverage"] = fmt(admissions_coverage * 100, 0)
        values["attendance_data_coverage"] = fmt(attendance_coverage * 100, 0)

        overall_score, overall_coverage = weighted_score(values, preference_weights.get("Overall School Value", []))
        values["overall_school_value"] = fmt(overall_score)
        values["overall_data_coverage"] = fmt(overall_coverage * 100, 0)

        populated = sum(1 for column in scoring_columns if parse_number(values.get(column)) is not None)
        completeness = (populated / len(scoring_columns) * 10) if scoring_columns else None
        values["data_completeness_score"] = fmt(completeness)
        values["dynamic_tier"] = dynamic_tier(admissions_score, attendance_score)

        for scenario, weights in scenario_weights.items():
            scenario_score, scenario_coverage = weighted_score(values, weights)
            key = scenario.lower().replace(" ", "_")
            values[f"{key}_score"] = fmt(scenario_score)
            values[f"{key}_coverage"] = fmt(scenario_coverage * 100, 0)

        output_rows.append(values)

    rank_values(output_rows, "overall_school_value", "overall_rank")
    for scenario in scenario_weights:
        key = scenario.lower().replace(" ", "_")
        rank_values(output_rows, f"{key}_score", f"{key}_rank")

    for row in output_rows:
        row["suggested_funnel_bucket"] = research_funnel(parse_number(row.get("overall_rank")))

    output_rows.sort(
        key=lambda row: (
            parse_number(row.get("overall_rank")) is None,
            parse_number(row.get("overall_rank")) or 999999,
            row.get("school_name", ""),
        )
    )

    computed_headers = [
        "overall_rank",
        "school_id",
        "school_name",
        "degree_type",
        "city",
        "state",
        "dynamic_tier",
        "suggested_funnel_bucket",
        "overall_school_value",
        "admissions_score",
        "attendance_score",
        "regret_index_score",
        "data_completeness_score",
        "admissions_data_coverage",
        "attendance_data_coverage",
        "overall_data_coverage",
    ]
    scenario_headers: List[str] = []
    for scenario in scenario_weights:
        key = scenario.lower().replace(" ", "_")
        scenario_headers.extend([f"{key}_rank", f"{key}_score", f"{key}_coverage"])

    passthrough_headers = [
        "application_unit_type",
        "parent_school_name",
        "campus_name",
        "accreditation_status",
        "manual_exclusion_flag",
        "exclusion_reason",
        "research_stage",
        "data_confidence",
        "source_name",
        "source_url",
        "last_verified_date",
        "notes",
    ]
    headers = computed_headers + scenario_headers + passthrough_headers

    with RANKINGS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    return RANKINGS_CSV


def main() -> None:
    output = build_rankings()
    print(f"Wrote {output.relative_to(ROOT)} with {len(read_csv(output))} rows")
