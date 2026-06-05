from __future__ import annotations

import csv
from pathlib import Path

from med_school_ranker import rankings
from med_school_ranker import validation


SCHOOL_MASTER_FIELDS = [
    "school_id",
    "school_name",
    "degree_type",
    "city",
    "state",
    "state_abbrev",
    "active_in_universe",
    "manual_exclusion_flag",
    "exclusion_reason",
    "admissions_mcat_fit_score",
    "attendance_prestige_score",
    "regret_index_score",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_minimal_project(root: Path) -> None:
    school_rows = [
        {
            "school_id": "school_one",
            "school_name": "School One",
            "degree_type": "MD",
            "city": "Boston",
            "state": "Massachusetts",
            "state_abbrev": "MA",
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
            "state_abbrev": "IL",
            "active_in_universe": "TRUE",
            "manual_exclusion_flag": "FALSE",
            "exclusion_reason": "",
            "admissions_mcat_fit_score": "4",
            "attendance_prestige_score": "5",
            "regret_index_score": "3",
        },
    ]
    write_csv(root / "data/school_master.csv", SCHOOL_MASTER_FIELDS, school_rows)
    write_csv(
        root / "data/user_preferences.csv",
        ["score_group", "column_name", "weight", "notes"],
        [
            {"score_group": "Admissions Score", "column_name": "admissions_mcat_fit_score", "weight": "1", "notes": ""},
            {"score_group": "Admissions Score", "column_name": "admissions_gpa_fit_score", "weight": "1", "notes": ""},
            {"score_group": "Admissions Score", "column_name": "admissions_oos_friendliness_score", "weight": "1", "notes": ""},
            {"score_group": "Attendance Score", "column_name": "attendance_cost_score", "weight": "1", "notes": ""},
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
    write_csv(root / "data/reference/aamc_mcat_gpa_acceptance_grid.csv", validation.AAMC_MCAT_GPA_GRID_COLUMNS, [])
    write_csv(root / "data/normalized/admissions_stats.csv", validation.ADMISSIONS_STATS_COLUMNS, [])
    write_csv(root / "data/normalized/cost_and_debt.csv", validation.COST_AND_DEBT_COLUMNS, [])
    write_csv(root / "data/normalized/admissions_policies.csv", validation.ADMISSIONS_POLICIES_COLUMNS, [])
    write_csv(root / "data/manual/partner_inputs.csv", validation.PARTNER_INPUT_COLUMNS, [
        {
            "applicant_profile_id": "test_profile",
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
        for row in school_rows
    ])


def patch_ranking_paths(monkeypatch, root: Path) -> None:
    out = root / "outputs"
    monkeypatch.setattr(rankings, "ROOT", root)
    monkeypatch.setattr(rankings, "OUT", out)
    monkeypatch.setattr(rankings, "MASTER_CSV", root / "data/school_master.csv")
    monkeypatch.setattr(rankings, "APPLICANT_PROFILES_CSV", root / "data/applicant_profiles.csv")
    monkeypatch.setattr(rankings, "PRIVATE_APPLICANT_PROFILES_CSV", root / "data/manual/private/applicant_profiles.local.csv")
    monkeypatch.setattr(rankings, "PREFERENCES_CSV", root / "data/user_preferences.csv")
    monkeypatch.setattr(rankings, "SCENARIO_WEIGHTS_CSV", root / "data/scenario_weights.csv")
    monkeypatch.setattr(rankings, "AAMC_MCAT_GPA_GRID_CSV", root / "data/reference/aamc_mcat_gpa_acceptance_grid.csv")
    monkeypatch.setattr(rankings, "ADMISSIONS_STATS_CSV", root / "data/normalized/admissions_stats.csv")
    monkeypatch.setattr(rankings, "COST_AND_DEBT_CSV", root / "data/normalized/cost_and_debt.csv")
    monkeypatch.setattr(rankings, "ADMISSIONS_POLICIES_CSV", root / "data/normalized/admissions_policies.csv")
    monkeypatch.setattr(rankings, "PARTNER_INPUTS_CSV", root / "data/manual/partner_inputs.csv")
    monkeypatch.setattr(rankings, "RANKINGS_CSV", out / "calculated_rankings.csv")
    monkeypatch.setattr(rankings, "SCORING_METHODOLOGY_CSV", out / "scoring_methodology.csv")
    monkeypatch.setattr(rankings, "SCORE_CONTRIBUTIONS_CSV", out / "score_contributions.csv")
    monkeypatch.setattr(rankings, "PRIVATE_OUT", out / "private")
    monkeypatch.setattr(rankings, "PRIVATE_RANKINGS_CSV", out / "private/calculated_rankings.private.csv")
    monkeypatch.setattr(rankings, "PRIVATE_SCORE_CONTRIBUTIONS_CSV", out / "private/score_contributions.private.csv")


def test_fit_formulas_and_florida_normalization():
    assert rankings.mcat_fit_score(509, 505) == 9
    assert round(rankings.gpa_fit_score(3.85, 3.69), 1) == 9
    assert rankings.state_abbrev("Florida") == "FL"


def test_phase2b_projection_scores_and_excludes_hard_no(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)

    school_path = tmp_path / "data/school_master.csv"
    school_rows = read_rows(school_path)
    school_rows[0]["state"] = "Florida"
    school_rows[0]["state_abbrev"] = "FL"
    school_rows[1]["state"] = "New York"
    school_rows[1]["state_abbrev"] = "NY"
    write_csv(school_path, list(school_rows[0].keys()), school_rows)

    write_csv(
        tmp_path / "data/applicant_profiles.csv",
        validation.APPLICANT_PROFILE_COLUMNS,
        [
            {
                "applicant_profile_id": "test_profile",
                "profile_name": "Test Profile",
                "is_default_profile": "TRUE",
                "mcat_total": "509",
                "overall_gpa": "3.85",
                "science_gpa": "",
                "state_of_residence": "Florida",
                "preferred_setting": "urban",
                "urban_preference_score": "8",
                "rural_tolerance_score": "5",
                "specialty_interest": "emergency medicine",
                "target_application_count": "25",
                "cost_weight_level": "low",
                "hidden_curriculum_weight_level": "low",
                "specialty_weight_level": "low",
                "notes": "Synthetic test profile.",
            }
        ],
    )
    write_csv(
        tmp_path / "data/normalized/admissions_stats.csv",
        validation.ADMISSIONS_STATS_COLUMNS,
        [
            {
                "school_id": "school_one",
                "school_name": "School One",
                "degree_type": "MD",
                "stats_cohort_year": "",
                "metric_population": "published school average",
                "metric_type": "third_party_published_source_average",
                "mcat_mean_enrolled": "505",
                "overall_gpa_mean_enrolled": "3.69",
                "published_source_count": "2",
                "published_mcat_average": "505",
                "published_gpa_average": "3.69",
                "published_mcat_spread": "0",
                "published_gpa_spread": "0",
                "published_mcat_band": "502-505",
                "published_gpa_band": "3.60-3.79",
                "aamc_acceptance_rate": "32.0",
                "aamc_acceptance_rate_band": "25-39.9%",
                "data_quality_rank": "2",
                "data_quality_band": "medium",
                "source_name": "Test",
                "source_url": "https://example.com",
                "source_last_checked": "2026-06-05",
                "data_confidence": "test",
            },
            {
                "school_id": "school_two",
                "school_name": "School Two",
                "degree_type": "DO",
                "stats_cohort_year": "",
                "metric_population": "published school average",
                "metric_type": "third_party_published_source_average",
                "mcat_mean_enrolled": "512",
                "overall_gpa_mean_enrolled": "3.80",
                "published_source_count": "1",
                "published_mcat_average": "512",
                "published_gpa_average": "3.80",
                "data_quality_rank": "3",
                "data_quality_band": "low",
                "source_name": "Test",
                "source_url": "https://example.com",
                "source_last_checked": "2026-06-05",
                "data_confidence": "test",
            },
        ],
    )
    write_csv(
        tmp_path / "data/normalized/cost_and_debt.csv",
        validation.COST_AND_DEBT_COLUMNS,
        [
            {
                "school_id": "school_one",
                "school_name": "School One",
                "degree_type": "MD",
                "estimated_coa_in_state": "40000",
                "estimated_coa_out_state": "80000",
                "source_name": "Test",
                "source_url": "https://example.com",
                "source_last_checked": "2026-06-05",
                "data_confidence": "test",
            },
            {
                "school_id": "school_two",
                "school_name": "School Two",
                "degree_type": "DO",
                "estimated_coa_in_state": "60000",
                "estimated_coa_out_state": "100000",
                "source_name": "Test",
                "source_url": "https://example.com",
                "source_last_checked": "2026-06-05",
                "data_confidence": "test",
            },
        ],
    )
    partner_rows = read_rows(tmp_path / "data/manual/partner_inputs.csv")
    partner_rows[1]["applicant_profile_id"] = "test_profile"
    partner_rows[1]["hard_no_flag"] = "TRUE"
    partner_rows[1]["hard_no_reason"] = "Synthetic hard no."
    write_csv(tmp_path / "data/manual/partner_inputs.csv", validation.PARTNER_INPUT_COLUMNS, partner_rows)

    output = rankings.build_rankings()
    rows = {row["school_id"]: row for row in read_rows(output)}

    assert rows["school_one"]["applicant_state_abbrev"] == "FL"
    assert rows["school_one"]["admissions_mcat_fit_score"] == "9.0"
    assert rows["school_one"]["admissions_gpa_fit_score"] == "9.0"
    assert rows["school_one"]["admissions_oos_friendliness_score"] == "10.0"
    assert rows["school_one"]["attendance_cost_score"] == "10.0"
    assert rows["school_two"]["excluded_from_rank"] == "TRUE"
    assert rows["school_two"]["overall_rank"] == ""
    assert rows["school_one"]["decision_rank"] == rows["school_one"]["overall_rank"]
    assert rows["school_one"]["rank_confidence"]
    assert rows["school_one"]["rank_summary"]


def test_score_contributions_reconcile_to_group_score(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)
    write_csv(
        tmp_path / "data/applicant_profiles.csv",
        validation.APPLICANT_PROFILE_COLUMNS,
        [
            {
                "applicant_profile_id": "test_profile",
                "profile_name": "Test Profile",
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
                "notes": "Synthetic test profile.",
            }
        ],
    )

    output = rankings.build_rankings()
    ranking_row = next(row for row in read_rows(output) if row["school_id"] == "school_one")
    contribution_rows = [
        row
        for row in read_rows(tmp_path / "outputs/score_contributions.csv")
        if row["school_id"] == "school_one"
        and row["score_model"] == "Decision Rank"
        and row["score_group"] == "Overall School Value"
        and row["component_coverage_status"] != "missing"
    ]
    contribution_sum = sum(float(row["weighted_contribution"]) for row in contribution_rows)

    assert round(contribution_sum, 2) == round(float(ranking_row["overall_school_value"]), 2)
    assert {row["weight_basis"] for row in contribution_rows} == {"present_components_only"}
    missing_rows = [
        row
        for row in read_rows(tmp_path / "outputs/score_contributions.csv")
        if row["school_id"] == "school_one"
        and row["component_column"] == "admissions_gpa_fit_score"
    ]
    assert missing_rows
    assert missing_rows[0]["component_coverage_status"] == "missing"
    assert missing_rows[0]["weighted_contribution"] == ""


def test_scoring_methodology_is_public_banded_reference(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)

    rankings.build_rankings()
    rows = read_rows(tmp_path / "outputs/scoring_methodology.csv")

    assert rows
    assert "aamc_mcat_selector" in {row["methodology_area"] for row in rows}
    assert any(row["input_band_or_condition"] == "506-509" for row in rows)
    assert not any("private_profile" in str(row) for row in rows)


def test_private_rankings_write_only_to_private_output(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    patch_ranking_paths(monkeypatch, tmp_path)
    private_profile = tmp_path / "data/manual/private/applicant_profiles.local.csv"
    write_csv(
        private_profile,
        validation.APPLICANT_PROFILE_COLUMNS,
        [
            {
                "applicant_profile_id": "private_profile",
                "profile_name": "Private Profile",
                "is_default_profile": "TRUE",
                "mcat_total": "509",
                "overall_gpa": "3.85",
                "science_gpa": "",
                "state_of_residence": "Florida",
                "preferred_setting": "urban",
                "urban_preference_score": "8",
                "rural_tolerance_score": "5",
                "specialty_interest": "emergency medicine",
                "target_application_count": "25",
                "cost_weight_level": "low",
                "hidden_curriculum_weight_level": "low",
                "specialty_weight_level": "low",
                "notes": "Private test profile.",
            }
        ],
    )

    output = rankings.build_private_rankings()
    rows = read_rows(output)

    assert output == tmp_path / "outputs/private/calculated_rankings.private.csv"
    assert rows
    assert {row["profile_source"] for row in rows} == {"private_local"}
    private_contributions = tmp_path / "outputs/private/score_contributions.private.csv"
    assert private_contributions.exists()
    assert {row["profile_source"] for row in read_rows(private_contributions)} == {"private_local"}
    assert not (tmp_path / "outputs/score_contributions.private.csv").exists()
