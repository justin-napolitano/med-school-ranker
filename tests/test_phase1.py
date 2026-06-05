from __future__ import annotations

import csv
import json
import re
import zipfile
from html import unescape
from pathlib import Path

from openpyxl import load_workbook

from med_school_ranker import bundle, rankings, site as site_builder, validation, workbook
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
    write_csv(root / "data/reference/aamc_mcat_gpa_acceptance_grid.csv", validation.AAMC_MCAT_GPA_GRID_COLUMNS, [])
    write_csv(root / "data/normalized/admissions_stats.csv", validation.ADMISSIONS_STATS_COLUMNS, [])
    write_csv(root / "data/normalized/cost_and_debt.csv", validation.COST_AND_DEBT_COLUMNS, [])
    write_csv(root / "data/normalized/admissions_policies.csv", validation.ADMISSIONS_POLICIES_COLUMNS, [])
    write_csv(root / "data/normalized/letter_requirements.csv", validation.LETTER_REQUIREMENTS_COLUMNS, [])
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
    write_csv(root / "data/manual/source_review_queue.csv", validation.SOURCE_REVIEW_QUEUE_COLUMNS, [])
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
    write_csv(
        root / "data/manual/source_match_overrides.csv",
        [
            "override_id",
            "source_table",
            "source_row_number",
            "source_school_name",
            "source_state",
            "source_degree_type",
            "override_action",
            "school_id",
            "school_name",
            "match_status",
            "reviewed_by",
            "reviewed_date",
            "review_notes",
        ],
        [],
    )
    write_csv(
        root / "data/project_subplans.csv",
        [
            "plan_name",
            "status",
            "priority",
            "phase",
            "current_decision_summary",
            "next_action",
            "doc_path",
        ],
        [
            {
                "plan_name": "Test Plan",
                "status": "active",
                "priority": "1",
                "phase": "test",
                "current_decision_summary": "Fixture row.",
                "next_action": "Run tests.",
                "doc_path": "docs/test.md",
            }
        ],
    )


def patch_ranking_paths(monkeypatch, root: Path) -> Path:
    out = root / "outputs"
    monkeypatch.setattr(rankings, "ROOT", root)
    monkeypatch.setattr(rankings, "OUT", out)
    monkeypatch.setattr(rankings, "MASTER_CSV", root / "data/school_master.csv")
    monkeypatch.setattr(rankings, "PREFERENCES_CSV", root / "data/user_preferences.csv")
    monkeypatch.setattr(rankings, "SCENARIO_WEIGHTS_CSV", root / "data/scenario_weights.csv")
    monkeypatch.setattr(rankings, "RANKINGS_CSV", out / "calculated_rankings.csv")
    return out


def patch_site_paths(monkeypatch, root: Path) -> Path:
    out = root / "outputs"
    site_dir = out / "site"
    monkeypatch.setattr(site_builder, "ROOT", root)
    monkeypatch.setattr(site_builder, "OUT", out)
    monkeypatch.setattr(site_builder, "MASTER_CSV", root / "data/school_master.csv")
    monkeypatch.setattr(site_builder, "RANKINGS_CSV", out / "calculated_rankings.csv")
    monkeypatch.setattr(site_builder, "APPLICANT_PROFILES_CSV", root / "data/applicant_profiles.csv")
    monkeypatch.setattr(site_builder, "AAMC_MCAT_GPA_GRID_CSV", root / "data/reference/aamc_mcat_gpa_acceptance_grid.csv")
    monkeypatch.setattr(site_builder, "ADMISSIONS_STATS_CSV", root / "data/normalized/admissions_stats.csv")
    monkeypatch.setattr(site_builder, "PARTNER_INPUTS_CSV", root / "data/manual/partner_inputs.csv")
    monkeypatch.setattr(site_builder, "SOURCE_MATCH_OVERRIDES_CSV", root / "data/manual/source_match_overrides.csv")
    monkeypatch.setattr(site_builder, "ADMISSIONS_SOURCE_QUEUE_CSV", root / "data/manual/admissions_source_queue.csv")
    monkeypatch.setattr(site_builder, "DATA_QUALITY_REPORT_CSV", out / "data_quality_report.csv")
    monkeypatch.setattr(site_builder, "SITE_DIR", site_dir)
    monkeypatch.setattr(site_builder, "SITE_INDEX_HTML", site_dir / "index.html")
    monkeypatch.setattr(site_builder, "SOURCE_TABLE_DIR", root / "data/source_tables")
    monkeypatch.setattr(site_builder, "SOURCE_DIFFS_DIR", out / "source_diffs")
    monkeypatch.setattr(site_builder, "RAW_AAMC_MSAR_DIR", root / "data/raw/aamc/msar_reports")
    monkeypatch.setattr(
        site_builder,
        "JSON_OUTPUTS",
        {
            "school_master": root / "data/school_master.csv",
            "calculated_rankings": out / "calculated_rankings.csv",
            "applicant_profiles": root / "data/applicant_profiles.csv",
            "aamc_mcat_gpa_grid": root / "data/reference/aamc_mcat_gpa_acceptance_grid.csv",
            "admissions_stats": root / "data/normalized/admissions_stats.csv",
            "cost_and_debt": root / "data/normalized/cost_and_debt.csv",
            "admissions_policies": root / "data/normalized/admissions_policies.csv",
            "letter_requirements": root / "data/normalized/letter_requirements.csv",
            "partner_inputs": root / "data/manual/partner_inputs.csv",
            "source_match_overrides": root / "data/manual/source_match_overrides.csv",
            "source_review_queue": root / "data/manual/source_review_queue.csv",
            "admissions_source_queue": root / "data/manual/admissions_source_queue.csv",
            "data_quality_report": out / "data_quality_report.csv",
            "source_integration_report": out / "source_integration_report.csv",
            "source_match_review": out / "source_match_review.csv",
            "admissions_stats_candidates": out / "admissions_stats_candidates.csv",
            "admissions_stats_conflicts": out / "admissions_stats_conflicts.csv",
            "cost_and_debt_candidates": out / "cost_and_debt_candidates.csv",
            "cost_and_debt_review": out / "cost_and_debt_review.csv",
            "project_subplans": root / "data/project_subplans.csv",
        },
    )
    return site_dir


def test_ranking_generation_runs(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)

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
        "AAMC GPA MCAT Grid",
        "Admissions Stats",
        "Cost and Debt",
        "Admissions Policies",
        "Letter Requirements",
        "Admissions Source Queue",
        "Source Match Overrides",
        "Source Review Queue",
        "Partner Inputs",
        "Calculated Rankings",
        "Final Application List",
        "Data Quality",
        "Source Integration Report",
        "Source Match Review",
        "Admissions Stats Candidates",
        "Admissions Stats Conflicts",
        "Cost and Debt Candidates",
        "Cost and Debt Review",
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


def test_site_generation_writes_local_payload_and_json(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    validation.validate_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)
    rankings.build_rankings()
    site_dir = patch_site_paths(monkeypatch, tmp_path)

    output = site_builder.build_site()

    assert output == site_dir / "index.html"
    html_text = output.read_text()
    assert 'id="site-data"' in html_text

    embedded_match = re.search(
        r'<script type="application/json" id="site-data">(.*?)</script>',
        html_text,
        re.DOTALL,
    )
    assert embedded_match is not None
    embedded_payload = json.loads(unescape(embedded_match.group(1)))

    master_rows = site_builder.read_csv(tmp_path / "data/school_master.csv")
    assert embedded_payload["meta"]["active_school_count"] == len(master_rows)
    assert all(school["school"].get("state") != "Puerto Rico" for school in embedded_payload["schools"])

    required_json = [
        "school_master.json",
        "calculated_rankings.json",
        "applicant_profiles.json",
        "aamc_mcat_gpa_grid.json",
        "admissions_stats.json",
        "cost_and_debt.json",
        "admissions_policies.json",
        "letter_requirements.json",
        "partner_inputs.json",
        "source_match_overrides.json",
        "source_review_queue.json",
        "admissions_source_queue.json",
        "data_quality_report.json",
        "source_integration_report.json",
        "source_match_review.json",
        "admissions_stats_candidates.json",
        "admissions_stats_conflicts.json",
        "cost_and_debt_candidates.json",
        "cost_and_debt_review.json",
        "project_subplans.json",
        "source_status.json",
        "site_payload.json",
    ]
    for filename in required_json:
        json.loads((site_dir / "data" / filename).read_text())


def test_site_output_does_not_copy_private_data(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    private_file = tmp_path / "data/manual/private/secret.csv"
    private_file.parent.mkdir(parents=True)
    private_file.write_text("secret\nsuper_secret_value\n")
    validation.validate_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)
    rankings.build_rankings()
    site_dir = patch_site_paths(monkeypatch, tmp_path)

    site_builder.build_site()

    generated_files = [path for path in site_dir.rglob("*") if path.is_file()]
    assert all("private" not in path.relative_to(site_dir).parts for path in generated_files)
    assert all("super_secret_value" not in path.read_text(errors="ignore") for path in generated_files)


def test_upload_bundle_includes_site_and_excludes_private_data(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    out = tmp_path / "outputs"
    site_dir = out / "site"
    write_csv(out / "calculated_rankings.csv", ["school_id"], [{"school_id": "school_one"}])
    write_csv(out / "data_quality_report.csv", validation.REPORT_COLUMNS, [])
    site_dir.mkdir(parents=True)
    (site_dir / "index.html").write_text("<!doctype html>")
    (site_dir / "data").mkdir()
    (site_dir / "data/site_payload.json").write_text("{}")
    workbook_path = out / "med_school_ranker.xlsx"
    workbook_path.write_text("workbook placeholder")
    private_file = tmp_path / "data/private/secret.csv"
    private_file.parent.mkdir(parents=True)
    private_file.write_text("secret\nsuper_secret_value\n")

    monkeypatch.setattr(bundle, "ROOT", tmp_path)
    monkeypatch.setattr(bundle, "DATA", tmp_path / "data")
    monkeypatch.setattr(bundle, "OUT", out)
    monkeypatch.setattr(bundle, "SITE_DIR", site_dir)
    monkeypatch.setattr(bundle, "WORKBOOK_XLSX", workbook_path)
    monkeypatch.setattr(bundle, "UPLOAD_ZIP", tmp_path / "med-school-ranker-upload.zip")

    zip_path = bundle.build_upload_zip()

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "outputs/site/index.html" in names
    assert "outputs/site/data/site_payload.json" in names
    assert not any(name.startswith("data/private/") for name in names)
    assert not any(name.startswith("data/manual/private/") for name in names)
