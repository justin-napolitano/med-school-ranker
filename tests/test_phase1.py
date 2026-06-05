from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import load_workbook

from med_school_ranker import rankings, validation, workbook
from med_school_ranker.paths import ROOT


SCHOOL_MASTER_FIELDS = [
    "school_id",
    "school_name",
    "degree_type",
    "city",
    "state",
    "active_in_universe",
    "manual_exclusion_flag",
    "exclusion_reason",
    "admissions_mcat_fit_score",
    "attendance_prestige_score",
    "regret_index_score",
]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def default_school_rows() -> list[dict[str, str]]:
    return [
        {
            "school_id": "school_one",
            "school_name": "School One",
            "degree_type": "MD",
            "city": "Boston",
            "state": "Massachusetts",
            "active_in_universe": "TRUE",
            "manual_exclusion_flag": "FALSE",
            "exclusion_reason": "",
            "admissions_mcat_fit_score": "8",
            "attendance_prestige_score": "9",
            "regret_index_score": "7",
        },
        {
            "school_id": "school_two",
            "school_name": "School Two",
            "degree_type": "DO",
            "city": "Chicago",
            "state": "Illinois",
            "active_in_universe": "TRUE",
            "manual_exclusion_flag": "FALSE",
            "exclusion_reason": "",
            "admissions_mcat_fit_score": "4",
            "attendance_prestige_score": "5",
            "regret_index_score": "3",
        },
    ]


def write_minimal_project(
    root: Path,
    school_rows: list[dict[str, str]] | None = None,
    partner_rows: list[dict[str, str]] | None = None,
) -> None:
    rows = school_rows or default_school_rows()
    write_csv(root / "data/school_master.csv", SCHOOL_MASTER_FIELDS, rows)
    write_csv(
        root / "data/user_preferences.csv",
        ["score_group", "column_name", "weight", "notes"],
        [
            {"score_group": "Admissions Score", "column_name": "admissions_mcat_fit_score", "weight": "1", "notes": ""},
            {"score_group": "Attendance Score", "column_name": "attendance_prestige_score", "weight": "1", "notes": ""},
            {"score_group": "Overall School Value", "column_name": "admissions_score", "weight": "1", "notes": ""},
            {"score_group": "Overall School Value", "column_name": "attendance_score", "weight": "1", "notes": ""},
            {"score_group": "Overall School Value", "column_name": "regret_index_score", "weight": "1", "notes": ""},
        ],
    )
    write_csv(
        root / "data/scenario_weights.csv",
        ["scenario", "column_name", "weight", "notes"],
        [{"scenario": "Balanced", "column_name": "overall_school_value", "weight": "1", "notes": ""}],
    )
    write_csv(
        root / "data/applicant_profiles.csv",
        validation.APPLICANT_PROFILE_COLUMNS,
        [
            {
                "applicant_profile_id": "template_profile",
                "profile_name": "Template Profile",
                "is_default_profile": "TRUE",
                "mcat_total": "",
                "overall_gpa": "",
                "science_gpa": "",
                "state_of_residence": "",
                "preferred_setting": "urban",
                "urban_preference_score": "8",
                "rural_tolerance_score": "5",
                "specialty_interest": "emergency medicine",
                "target_application_count": "25",
                "cost_weight_level": "low",
                "hidden_curriculum_weight_level": "low",
                "specialty_weight_level": "low",
                "notes": "Template only.",
            }
        ],
    )
    write_csv(root / "data/normalized/admissions_stats.csv", validation.ADMISSIONS_STATS_COLUMNS, [])
    write_csv(
        root / "data/manual/admissions_source_queue.csv",
        validation.ADMISSIONS_SOURCE_QUEUE_COLUMNS,
        [
            {
                "school_id": row["school_id"],
                "school_name": row["school_name"],
                "degree_type": row["degree_type"],
                "candidate_source_url": "",
                "source_status": "",
                "extraction_status": "",
                "review_status": "",
                "last_checked": "",
                "notes": "",
            }
            for row in rows
        ],
    )
    write_csv(
        root / "data/manual/partner_inputs.csv",
        validation.PARTNER_INPUT_COLUMNS,
        partner_rows
        or [
            {
                "applicant_profile_id": "template_profile",
                "school_id": row["school_id"],
                "school_name": row["school_name"],
                "could_live_here_4_years_score": "",
                "location_fit_score": "",
                "culture_fit_score": "",
                "regret_index_score": "",
                "hard_no_flag": "",
                "hard_no_reason": "",
                "partner_notes": "",
            }
            for row in rows
        ],
    )
    write_csv(root / "data/final_application_list.csv", ["school_id", "school_name", "why_kept", "why_cut"], [])


def test_ranking_generation_runs(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    out = tmp_path / "outputs"

    monkeypatch.setattr(rankings, "ROOT", tmp_path)
    monkeypatch.setattr(rankings, "OUT", out)
    monkeypatch.setattr(rankings, "MASTER_CSV", tmp_path / "data/school_master.csv")
    monkeypatch.setattr(rankings, "PREFERENCES_CSV", tmp_path / "data/user_preferences.csv")
    monkeypatch.setattr(rankings, "SCENARIO_WEIGHTS_CSV", tmp_path / "data/scenario_weights.csv")
    monkeypatch.setattr(rankings, "RANKINGS_CSV", out / "calculated_rankings.csv")

    output = rankings.build_rankings()

    with output.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["school_id"] == "school_one"
    assert rows[0]["overall_rank"] == "1"


def test_workbook_has_required_tabs(tmp_path, monkeypatch):
    required_tabs = {
        "Instructions",
        "Project Subplans",
        "School Master",
        "Applicant Profiles",
        "User Preferences",
        "Scenario Weights",
        "Admissions Stats",
        "Admissions Source Queue",
        "Partner Inputs",
        "Calculated Rankings",
        "Final Application List",
        "Data Quality",
        "Sources",
        "Field Definitions",
    }
    assert required_tabs.issubset({title for title, _ in workbook.SHEETS})

    temp_sheets = []
    for title, path in workbook.SHEETS:
        if path is None:
            temp_sheets.append((title, None))
            continue
        temp_path = tmp_path / path.relative_to(ROOT)
        write_csv(temp_path, ["id"], [{"id": title}])
        temp_sheets.append((title, temp_path))

    monkeypatch.setattr(workbook, "ROOT", tmp_path)
    monkeypatch.setattr(workbook, "OUT", tmp_path / "outputs")
    monkeypatch.setattr(workbook, "WORKBOOK_XLSX", tmp_path / "outputs/med_school_ranker.xlsx")
    monkeypatch.setattr(workbook, "SHEETS", temp_sheets)

    output = workbook.build_workbook()
    wb = load_workbook(output, read_only=True)
    assert required_tabs.issubset(set(wb.sheetnames))


def test_validation_catches_duplicate_school_id(tmp_path):
    rows = default_school_rows()
    rows[1]["school_id"] = rows[0]["school_id"]
    write_minimal_project(tmp_path, school_rows=rows)

    issues = validation.validate_project(tmp_path)

    assert any(issue.severity == "error" and issue.field == "school_id" for issue in issues)


def test_validation_catches_invalid_score(tmp_path):
    rows = default_school_rows()
    rows[0]["admissions_mcat_fit_score"] = "11"
    write_minimal_project(tmp_path, school_rows=rows)

    issues = validation.validate_project(tmp_path)

    assert any(issue.severity == "error" and issue.field == "admissions_mcat_fit_score" for issue in issues)


def test_validation_catches_exclusion_without_reason(tmp_path):
    rows = default_school_rows()
    rows[0]["manual_exclusion_flag"] = "TRUE"
    rows[0]["exclusion_reason"] = ""
    write_minimal_project(tmp_path, school_rows=rows)

    issues = validation.validate_project(tmp_path)

    assert any(issue.severity == "error" and issue.field == "exclusion_reason" for issue in issues)
