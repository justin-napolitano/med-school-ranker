from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from med_school_ranker.paths import MASTER_CSV, ROOT, SCHOOL_DOSSIERS_CSV, SCHOOL_VISIBILITY_CSV
from med_school_ranker.validation import SCHOOL_DOSSIER_COLUMNS, SCHOOL_VISIBILITY_COLUMNS


VISIBILITY_EXPORT_SCHEMA = "school_visibility_v1"
DOSSIER_EXPORT_SCHEMA = "school_dossier_edits_v1"


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def school_names(master_path: Path = MASTER_CSV) -> dict[str, str]:
    return {
        row.get("school_id", "").strip(): row.get("school_name", "").strip()
        for row in read_rows(master_path)
        if row.get("school_id", "").strip()
    }


def indexed_by_school(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed = {}
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id:
            indexed[school_id] = row
    return indexed


def validate_export_schema(row: dict[str, str], expected_schema: str, source_path: Path) -> None:
    schema = row.get("export_schema_version", "").strip()
    if schema and schema != expected_schema:
        raise ValueError(f"{source_path} has unsupported export_schema_version '{schema}'. Expected {expected_schema}.")


def import_visibility_export(
    export_path: Path,
    target_path: Path = SCHOOL_VISIBILITY_CSV,
    master_path: Path = MASTER_CSV,
) -> int:
    existing = indexed_by_school(read_rows(target_path))
    names = school_names(master_path)
    imported_at = now_iso()
    imported_count = 0

    for row in read_rows(export_path):
        validate_export_schema(row, VISIBILITY_EXPORT_SCHEMA, export_path)
        school_id = row.get("school_id", "").strip()
        if not school_id:
            continue
        visibility_state = row.get("visibility_state", "").strip() or "visible"
        if visibility_state == "visible" and school_id not in existing:
            continue
        existing[school_id] = {
            "school_id": school_id,
            "school_name": names.get(school_id) or row.get("school_name", "").strip(),
            "visibility_state": visibility_state,
            "visibility_reason": row.get("visibility_reason", "").strip(),
            "hidden_at": row.get("hidden_at", "").strip(),
            "updated_at": row.get("updated_at", "").strip() or row.get("exported_at", "").strip() or imported_at,
            "source": "browser_visibility_export",
            "notes": row.get("notes", "").strip(),
        }
        imported_count += 1

    write_rows(target_path, SCHOOL_VISIBILITY_COLUMNS, sorted(existing.values(), key=lambda item: item["school_name"]))
    return imported_count


def dossier_has_content(row: dict[str, str]) -> bool:
    return any(
        row.get(field, "").strip()
        for field in [
            "research_status",
            "interest_level",
            "four_year_happiness",
            "location_fit",
            "culture_fit",
            "regret_index",
            "hard_no_flag",
            "hard_no_reason",
            "application_decision_status",
            "notes",
        ]
    )


def import_dossier_export(
    export_path: Path,
    target_path: Path = SCHOOL_DOSSIERS_CSV,
    master_path: Path = MASTER_CSV,
) -> int:
    existing = indexed_by_school(read_rows(target_path))
    names = school_names(master_path)
    imported_at = now_iso()
    imported_count = 0

    for row in read_rows(export_path):
        validate_export_schema(row, DOSSIER_EXPORT_SCHEMA, export_path)
        school_id = row.get("school_id", "").strip()
        if not school_id or not dossier_has_content(row):
            continue
        existing[school_id] = {
            "school_id": school_id,
            "school_name": names.get(school_id) or row.get("school_name", "").strip(),
            "research_status": row.get("research_status", "").strip(),
            "interest_level": row.get("interest_level", "").strip(),
            "four_year_happiness": row.get("four_year_happiness", "").strip(),
            "location_fit": row.get("location_fit", "").strip(),
            "culture_fit": row.get("culture_fit", "").strip(),
            "regret_index": row.get("regret_index", "").strip(),
            "hard_no_flag": row.get("hard_no_flag", "").strip(),
            "hard_no_reason": row.get("hard_no_reason", "").strip(),
            "application_decision_status": row.get("application_decision_status", "").strip(),
            "notes": row.get("notes", "").strip(),
            "updated_at": row.get("exported_at", "").strip() or imported_at,
            "source": "browser_dossier_export",
        }
        imported_count += 1

    write_rows(target_path, SCHOOL_DOSSIER_COLUMNS, sorted(existing.values(), key=lambda item: item["school_name"]))
    return imported_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Import browser-exported reviewer state CSVs into durable manual tables.")
    parser.add_argument("--visibility-export", type=Path, help="Path to school_visibility_export.csv from the site.")
    parser.add_argument("--dossier-export", type=Path, help="Path to school_dossier_edits_export.csv from the site.")
    args = parser.parse_args()

    if not args.visibility_export and not args.dossier_export:
        parser.error("Provide --visibility-export, --dossier-export, or both.")

    if args.visibility_export:
        count = import_visibility_export(args.visibility_export)
        print(f"Imported {count} visibility row(s) into {SCHOOL_VISIBILITY_CSV.relative_to(ROOT)}")
    if args.dossier_export:
        count = import_dossier_export(args.dossier_export)
        print(f"Imported {count} dossier row(s) into {SCHOOL_DOSSIERS_CSV.relative_to(ROOT)}")
