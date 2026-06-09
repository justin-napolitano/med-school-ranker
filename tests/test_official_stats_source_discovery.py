from __future__ import annotations

from pathlib import Path

from med_school_ranker import official_stats_apply
from med_school_ranker.official_source_rules import (
    OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    OFFICIAL_STATS_CONFLICT_COLUMNS,
    OFFICIAL_STATS_COVERAGE_COLUMNS,
    OFFICIAL_STATS_EXTRACTED_COLUMNS,
    classify_official_source,
    read_csv,
    write_csv,
)
from med_school_ranker.official_stats_extraction import extract_stats_from_text
from med_school_ranker.validation import ADMISSIONS_STATS_COLUMNS


def test_official_source_classifier_accepts_school_domain() -> None:
    school = {
        "school_name": "University of Florida College of Medicine",
        "website": "https://med.ufl.edu/",
    }

    result = classify_official_source(school, "https://med.ufl.edu/admissions/class-profile/")

    assert result.status == "official_school_domain"
    assert result.accepted_for_auto_extraction


def test_official_source_classifier_rejects_search_and_third_party_urls() -> None:
    school = {
        "school_name": "University of Florida College of Medicine",
        "website": "https://med.ufl.edu/",
    }

    search_result = classify_official_source(school, "https://www.google.com/search?q=uf+medicine+mcat+gpa")
    advising_result = classify_official_source(
        school,
        "https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school",
    )

    assert search_result.status == "rejected_non_official_or_search"
    assert advising_result.status == "rejected_non_official_or_search"


def test_official_source_classifier_does_not_accept_unrelated_edu_without_signal() -> None:
    school = {
        "school_name": "University of Florida College of Medicine",
        "website": "",
    }

    result = classify_official_source(school, "https://medicine.yale.edu/md-program/admissions/")

    assert result.status == "needs_review_edu_domain"
    assert not result.accepted_for_auto_extraction


def test_extractor_accepts_class_profile_mcat_and_gpa_values() -> None:
    school = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
    }
    candidate = {
        "candidate_source_url": "https://medicine.example.edu/admissions/class-profile",
        "candidate_source_title": "Entering Class Profile",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = """
    Entering Class Profile, Class of 2028.
    Matriculants had a median MCAT score of 512 and an average overall GPA of 3.78.
    """

    row = extract_stats_from_text(school, candidate, text)

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "512"
    assert row["gpa_value"] == "3.78"
    assert row["stats_cohort_year"] == "2028"
    assert row["metric_population"] == "matriculated students"


def test_extractor_rejects_minimum_requirement_context() -> None:
    school = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
    }
    candidate = {
        "candidate_source_url": "https://medicine.example.edu/admissions/requirements",
        "candidate_source_title": "Admissions Requirements",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Applicants must meet a minimum MCAT score of 500 and a minimum cumulative GPA of 3.0."

    row = extract_stats_from_text(school, candidate, text)

    assert row["extraction_status"] == "rejected_minimum_requirement"
    assert row["mcat_value"] == ""
    assert row["gpa_value"] == ""


def test_apply_promotes_accepted_official_row(tmp_path: Path, monkeypatch) -> None:
    master_csv = tmp_path / "data/school_master.csv"
    stats_csv = tmp_path / "data/normalized/admissions_stats.csv"
    extracted_csv = tmp_path / "data/source_tables/official_mcat_gpa_extracted_values.csv"
    candidates_csv = tmp_path / "data/source_tables/official_mcat_gpa_source_candidates.csv"
    conflicts_csv = tmp_path / "outputs/official_mcat_gpa_conflicts.csv"
    coverage_csv = tmp_path / "outputs/official_mcat_gpa_coverage.csv"

    monkeypatch.setattr(official_stats_apply, "MASTER_CSV", master_csv)
    monkeypatch.setattr(official_stats_apply, "ADMISSIONS_STATS_CSV", stats_csv)
    monkeypatch.setattr(official_stats_apply, "OFFICIAL_STATS_EXTRACTED_VALUES_CSV", extracted_csv)
    monkeypatch.setattr(official_stats_apply, "OFFICIAL_STATS_SOURCE_CANDIDATES_CSV", candidates_csv)
    monkeypatch.setattr(official_stats_apply, "OFFICIAL_STATS_CONFLICTS_CSV", conflicts_csv)
    monkeypatch.setattr(official_stats_apply, "OFFICIAL_STATS_COVERAGE_CSV", coverage_csv)

    write_csv(
        master_csv,
        ["school_id", "school_name", "degree_type", "active_in_universe", "manual_exclusion_flag"],
        [
            {
                "school_id": "md_test",
                "school_name": "Test College of Medicine",
                "degree_type": "MD",
                "active_in_universe": "TRUE",
                "manual_exclusion_flag": "FALSE",
            }
        ],
    )
    provisional = {column: "" for column in ADMISSIONS_STATS_COLUMNS}
    provisional.update(
        {
            "school_id": "md_test",
            "school_name": "Test College of Medicine",
            "degree_type": "MD",
            "published_mcat_average": "509",
            "published_gpa_average": "3.7",
            "source_name": "Third-party source",
            "source_url": "https://example.com/third-party",
            "data_confidence": "third_party_published_average_low_quality",
        }
    )
    write_csv(stats_csv, ADMISSIONS_STATS_COLUMNS, [provisional])
    write_csv(candidates_csv, OFFICIAL_SOURCE_CANDIDATE_COLUMNS, [])
    write_csv(
        extracted_csv,
        OFFICIAL_STATS_EXTRACTED_COLUMNS,
        [
            {
                "school_id": "md_test",
                "school_name": "Test College of Medicine",
                "degree_type": "MD",
                "candidate_source_url": "https://medicine.example.edu/admissions/class-profile",
                "candidate_source_title": "Class Profile",
                "candidate_source_type": "class_profile",
                "official_domain_status": "official_school_domain",
                "official_domain_score": "1.00",
                "fetch_status": "fetched",
                "extraction_status": "accepted",
                "review_status": "approved_official_extraction",
                "stats_cohort_year": "2028",
                "metric_population": "matriculated students",
                "metric_type": "official_published_median",
                "mcat_value": "512",
                "mcat_metric": "median",
                "gpa_value": "3.84",
                "gpa_metric": "median",
                "source_last_checked": "2026-06-08",
            }
        ],
    )

    count = official_stats_apply.apply_official_stats()
    stats_rows = read_csv(stats_csv)
    conflict_rows = read_csv(conflicts_csv)
    coverage_rows = read_csv(coverage_csv)

    assert count == 1
    assert len(stats_rows) == 1
    assert stats_rows[0]["source_name"] == "Official school source"
    assert stats_rows[0]["published_mcat_average"] == "512"
    assert stats_rows[0]["published_gpa_average"] == "3.84"
    assert conflict_rows[0]["conflict_status"] == "large_delta_review"
    assert coverage_rows[0]["coverage_status"] == "official_stats_applied"
    assert OFFICIAL_STATS_CONFLICT_COLUMNS == list(conflict_rows[0].keys())
    assert OFFICIAL_STATS_COVERAGE_COLUMNS == list(coverage_rows[0].keys())
