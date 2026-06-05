from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

from med_school_ranker.paths import (
    FINAL_APPLICATION_LIST_CSV,
    MASTER_CSV,
    RANKINGS_CSV,
    SCHOOL_DOSSIERS_CSV,
    SCHOOL_VISIBILITY_CSV,
)


FINAL_APPLICATION_LIST_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "city",
    "state",
    "current_bucket",
    "status",
    "why_kept",
    "why_cut",
    "assigned_research_owner",
    "next_action",
    "priority",
    "application_service",
    "primary_deadline",
    "secondary_fee",
    "submitted_primary",
    "secondary_received",
    "secondary_submitted",
    "interview_invite",
    "decision",
    "notes",
]

INCLUDED_DECISION_STATUSES = {
    "considering",
    "applying",
    "applied",
    "interview",
    "accepted",
    "waitlisted",
}
EXCLUDED_DECISION_STATUSES = {"not_applying", "rejected", "withdrawn"}
PRESERVED_COLUMNS = {
    "why_kept",
    "why_cut",
    "assigned_research_owner",
    "primary_deadline",
    "secondary_fee",
    "submitted_primary",
    "secondary_received",
    "secondary_submitted",
    "interview_invite",
    "notes",
}


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


def normalized(value: str | None) -> str:
    return str(value or "").strip().lower()


def parse_rank(value: str | None) -> int:
    text = str(value or "").strip()
    try:
        return int(float(text))
    except ValueError:
        return 9999


def first_by_school(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_school: dict[str, dict[str, str]] = {}
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id and school_id not in by_school:
            by_school[school_id] = row
    return by_school


def rankings_by_school(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    sorted_rows = sorted(rows, key=lambda row: parse_rank(row.get("decision_rank") or row.get("overall_rank")))
    return first_by_school(sorted_rows)


def existing_rows_by_school(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    return first_by_school(rows)


def application_service(degree_type: str) -> str:
    degree = degree_type.strip().upper()
    if degree == "MD":
        return "AMCAS"
    if degree == "DO":
        return "AACOMAS"
    return ""


def next_action_for(status: str, research_status: str) -> str:
    status = normalized(status)
    if status == "accepted":
        return "compare offer and revisit final fit"
    if status == "waitlisted":
        return "track waitlist movement and update letters"
    if status == "interview":
        return "prepare for interview"
    if status == "applied":
        return "track secondary, interview, and decision updates"
    if status == "applying":
        return "submit primary and secondary materials"
    if normalized(research_status) in {"researched", "ready_to_decide"}:
        return "decide whether to submit application"
    return "research dossier and decide whether to apply"


def priority_for(status: str, ranking: dict[str, str]) -> str:
    normalized_status = normalized(status)
    rank = parse_rank(ranking.get("decision_rank") or ranking.get("overall_rank"))
    if normalized_status in {"accepted", "interview", "applied", "applying"}:
        return "highest" if rank <= 40 else "high"
    if rank <= 25:
        return "highest"
    if rank <= 40:
        return "high"
    if rank <= 75:
        return "medium"
    return "low"


def generated_why_kept(status: str, ranking: dict[str, str], dossier: dict[str, str]) -> str:
    parts = [f"Marked {status or 'considering'} in school dossier"]
    rank = ranking.get("decision_rank") or ranking.get("overall_rank")
    if rank:
        parts.append(f"Decision Rank {rank}")
    if ranking.get("rank_band"):
        parts.append(f"rank band {ranking['rank_band']}")
    tier = ranking.get("admissions_fit_tier") or ranking.get("dynamic_tier")
    if tier:
        parts.append(f"admissions tier {tier}")
    bucket = ranking.get("application_bucket") or ranking.get("suggested_funnel_bucket")
    if bucket:
        parts.append(f"bucket {bucket}")
    if dossier.get("interest_level"):
        parts.append(f"interest {dossier['interest_level']}")
    return "; ".join(parts) + "."


def include_dossier_row(dossier: dict[str, str], visibility: dict[str, str]) -> bool:
    if normalized(visibility.get("visibility_state")) == "hidden":
        return False
    status = normalized(dossier.get("application_decision_status"))
    if status in EXCLUDED_DECISION_STATUSES:
        return False
    return status in INCLUDED_DECISION_STATUSES


def build_row(
    school: dict[str, str],
    ranking: dict[str, str],
    dossier: dict[str, str],
    existing: dict[str, str],
) -> dict[str, str]:
    status = normalized(dossier.get("application_decision_status")) or "considering"
    bucket = ranking.get("application_bucket") or ranking.get("suggested_funnel_bucket") or ""
    row = {column: "" for column in FINAL_APPLICATION_LIST_COLUMNS}
    row.update(
        {
            "school_id": school.get("school_id", ""),
            "school_name": school.get("school_name", ""),
            "degree_type": school.get("degree_type", ""),
            "city": school.get("city", ""),
            "state": school.get("state", ""),
            "current_bucket": bucket,
            "status": status,
            "why_kept": generated_why_kept(status, ranking, dossier),
            "why_cut": "",
            "next_action": next_action_for(status, dossier.get("research_status", "")),
            "priority": priority_for(status, ranking),
            "application_service": application_service(school.get("degree_type", "")),
            "decision": status,
        }
    )
    for column in PRESERVED_COLUMNS:
        if existing.get(column, "").strip():
            row[column] = existing[column]
    return row


def build_final_application_rows(
    school_master: list[dict[str, str]],
    rankings: list[dict[str, str]],
    visibility_rows: list[dict[str, str]],
    dossier_rows: list[dict[str, str]],
    existing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    ranking_by_school = rankings_by_school(rankings)
    visibility_by_school = first_by_school(visibility_rows)
    dossier_by_school = first_by_school(dossier_rows)
    existing_by_school = existing_rows_by_school(existing_rows)
    rows = []
    for school in school_master:
        school_id = school.get("school_id", "").strip()
        if not school_id:
            continue
        dossier = dossier_by_school.get(school_id, {})
        visibility = visibility_by_school.get(school_id, {})
        if not include_dossier_row(dossier, visibility):
            continue
        ranking = ranking_by_school.get(school_id, {})
        rows.append(build_row(school, ranking, dossier, existing_by_school.get(school_id, {})))
    rows.sort(
        key=lambda row: (
            {"highest": 0, "high": 1, "medium": 2, "low": 3}.get(row.get("priority", ""), 9),
            parse_rank(ranking_by_school.get(row["school_id"], {}).get("decision_rank")),
            row.get("school_name", ""),
        )
    )
    return rows


def build_final_application_list(
    *,
    master_path: Path = MASTER_CSV,
    rankings_path: Path = RANKINGS_CSV,
    visibility_path: Path = SCHOOL_VISIBILITY_CSV,
    dossiers_path: Path = SCHOOL_DOSSIERS_CSV,
    output_path: Path = FINAL_APPLICATION_LIST_CSV,
) -> Path:
    rows = build_final_application_rows(
        school_master=read_csv(master_path),
        rankings=read_csv(rankings_path),
        visibility_rows=read_csv(visibility_path),
        dossier_rows=read_csv(dossiers_path),
        existing_rows=read_csv(output_path),
    )
    write_csv(output_path, FINAL_APPLICATION_LIST_COLUMNS, rows)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build data/final_application_list.csv from persisted reviewer state.")
    parser.add_argument("--master", type=Path, default=MASTER_CSV)
    parser.add_argument("--rankings", type=Path, default=RANKINGS_CSV)
    parser.add_argument("--visibility", type=Path, default=SCHOOL_VISIBILITY_CSV)
    parser.add_argument("--dossiers", type=Path, default=SCHOOL_DOSSIERS_CSV)
    parser.add_argument("--output", type=Path, default=FINAL_APPLICATION_LIST_CSV)
    args = parser.parse_args()
    output = build_final_application_list(
        master_path=args.master,
        rankings_path=args.rankings,
        visibility_path=args.visibility,
        dossiers_path=args.dossiers,
        output_path=args.output,
    )
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
