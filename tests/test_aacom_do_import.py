from __future__ import annotations

from pathlib import Path

from med_school_ranker import aacom_do_apply
from med_school_ranker.aacom_do_extraction import extract_aacom_stats_from_text
from med_school_ranker.aacom_do_rules import (
    AACOM_CONFLICT_COLUMNS,
    AACOM_COVERAGE_COLUMNS,
    AACOM_DATA_CONFIDENCE,
    AACOM_EXTRACTED_STATS_COLUMNS,
    AACOM_PROFILE_CANDIDATE_COLUMNS,
    best_profile_match,
    parse_aacom_profile_cards,
    parse_aacom_profile_urls,
    read_csv,
    write_csv,
)
from med_school_ranker.validation import ADMISSIONS_STATS_COLUMNS


def test_parse_aacom_profile_urls_normalizes_absolute_and_relative_links() -> None:
    document = """
    <a href="/detail-pages/com/arizona-college-of-osteopathic-medicine">Arizona</a>
    <a href="https://www.aacom.org/detail-pages/com/kansas-city-university-college-of-osteopathic-medicine/">
    Kansas City
    </a>
    <a data-srch-target="aHR0cHM6Ly9hYWNvbS5vcmcvZGV0YWlsLXBhZ2VzL2NvbS9hbGFiYW1hLWNvbGxlZ2Utb2Ytb3N0ZW9wYXRoaWMtbWVkaWNpbmU=">Alabama</a>
    """

    urls = parse_aacom_profile_urls(document)

    assert urls == [
        "https://www.aacom.org/detail-pages/com/alabama-college-of-osteopathic-medicine",
        "https://www.aacom.org/detail-pages/com/arizona-college-of-osteopathic-medicine",
        "https://www.aacom.org/detail-pages/com/kansas-city-university-college-of-osteopathic-medicine",
    ]


def test_parse_aacom_profile_cards_keeps_location_metadata() -> None:
    document = """
    <a data-srch-target="aHR0cHM6Ly9hYWNvbS5vcmcvZGV0YWlsLXBhZ2VzL2NvbS9hbGFiYW1hLWNvbGxlZ2Utb2Ytb3N0ZW9wYXRoaWMtbWVkaWNpbmU=" class="item-list__link">
      <span class="item-list__title">Alabama College of Osteopathic Medicine</span>
      <div class="item-list__location"><i></i><span> Dothan, AL</span></div>
    </a>
    """

    cards = parse_aacom_profile_cards(document)

    assert len(cards) == 1
    assert cards[0].url == "https://www.aacom.org/detail-pages/com/alabama-college-of-osteopathic-medicine"
    assert cards[0].title == "Alabama College of Osteopathic Medicine"
    assert cards[0].city == "Dothan"
    assert cards[0].state_abbrev == "AL"


def test_best_profile_match_safely_matches_do_school_slug() -> None:
    schools = [
        {
            "school_id": "do_azcom",
            "school_name": "Arizona College of Osteopathic Medicine",
            "degree_type": "DO",
        }
    ]

    match = best_profile_match(
        "https://www.aacom.org/detail-pages/com/arizona-college-of-osteopathic-medicine",
        "",
        schools,
    )

    assert match.status == "safe_match"
    assert match.school and match.school["school_id"] == "do_azcom"


def test_best_profile_match_uses_city_for_same_state_campus_match() -> None:
    schools = [
        {
            "school_id": "do_atsu_soma",
            "school_name": "A.T. Still University, School of Osteopathic Medicine in Arizona",
            "degree_type": "DO",
            "city": "Mesa",
            "state_abbrev": "AZ",
        },
        {
            "school_id": "do_azcom",
            "school_name": "Midwestern University Arizona College of Osteopathic Medicine",
            "degree_type": "DO",
            "city": "Glendale",
            "state_abbrev": "AZ",
        },
    ]

    match = best_profile_match(
        "https://www.aacom.org/detail-pages/com/arizona-college-of-osteopathic-medicine",
        "Arizona College of Osteopathic Medicine",
        schools,
        city="Glendale",
        state_abbrev="AZ",
    )

    assert match.status == "safe_match"
    assert match.school and match.school["school_id"] == "do_azcom"


def test_aacom_extractor_accepts_mean_mcat_and_gpa_values() -> None:
    school = {
        "school_id": "do_test",
        "school_name": "Test College of Osteopathic Medicine",
        "degree_type": "DO",
    }
    candidate = {
        "aacom_profile_url": "https://www.aacom.org/detail-pages/com/test-college-of-osteopathic-medicine",
        "aacom_profile_title": "Test College of Osteopathic Medicine",
    }
    text = """
    Test College of Osteopathic Medicine 2024-2025
    MCAT/GPA Information Mean MCAT Score 510
    Avg. Cum. Undergrad GPA Score 3.65
    Oldest MCAT Considered 2022
    Latest MCAT Score Accepted 2025
    """

    row = extract_aacom_stats_from_text(school, candidate, text)

    assert row["extraction_status"] == "accepted"
    assert row["review_status"] == "approved_aacom_extraction"
    assert row["mcat_mean"] == "510"
    assert row["overall_gpa_mean"] == "3.65"
    assert row["data_confidence"] == AACOM_DATA_CONFIDENCE


def test_aacom_extractor_keeps_partial_values_in_review() -> None:
    school = {
        "school_id": "do_test",
        "school_name": "Test College of Osteopathic Medicine",
        "degree_type": "DO",
    }
    candidate = {
        "aacom_profile_url": "https://www.aacom.org/detail-pages/com/test-college-of-osteopathic-medicine",
        "aacom_profile_title": "Test College of Osteopathic Medicine",
    }
    text = "MCAT/GPA Information Mean MCAT Score 510"

    row = extract_aacom_stats_from_text(school, candidate, text)

    assert row["extraction_status"] == "needs_review_partial_aacom_stats"
    assert row["review_status"] == "needs_review"
    assert row["mcat_mean"] == "510"
    assert row["overall_gpa_mean"] == ""


def test_apply_promotes_aacom_row_and_preserves_provisional_row(tmp_path: Path, monkeypatch) -> None:
    master_csv = tmp_path / "data/school_master.csv"
    stats_csv = tmp_path / "data/normalized/admissions_stats.csv"
    extracted_csv = tmp_path / "data/source_tables/aacom_do_extracted_stats.csv"
    candidates_csv = tmp_path / "data/source_tables/aacom_do_profile_candidates.csv"
    conflicts_csv = tmp_path / "outputs/aacom_do_profile_conflicts.csv"
    coverage_csv = tmp_path / "outputs/aacom_do_profile_coverage.csv"

    monkeypatch.setattr(aacom_do_apply, "MASTER_CSV", master_csv)
    monkeypatch.setattr(aacom_do_apply, "ADMISSIONS_STATS_CSV", stats_csv)
    monkeypatch.setattr(aacom_do_apply, "AACOM_DO_EXTRACTED_STATS_CSV", extracted_csv)
    monkeypatch.setattr(aacom_do_apply, "AACOM_DO_PROFILE_CANDIDATES_CSV", candidates_csv)
    monkeypatch.setattr(aacom_do_apply, "AACOM_DO_PROFILE_CONFLICTS_CSV", conflicts_csv)
    monkeypatch.setattr(aacom_do_apply, "AACOM_DO_PROFILE_COVERAGE_CSV", coverage_csv)

    write_csv(
        master_csv,
        ["school_id", "school_name", "degree_type", "active_in_universe", "manual_exclusion_flag"],
        [
            {
                "school_id": "do_test",
                "school_name": "Test College of Osteopathic Medicine",
                "degree_type": "DO",
                "active_in_universe": "TRUE",
                "manual_exclusion_flag": "FALSE",
            }
        ],
    )
    provisional = {column: "" for column in ADMISSIONS_STATS_COLUMNS}
    provisional.update(
        {
            "school_id": "do_test",
            "school_name": "Test College of Osteopathic Medicine",
            "degree_type": "DO",
            "published_mcat_average": "506",
            "published_gpa_average": "3.45",
            "source_name": "Third-party source",
            "source_url": "https://example.com/do-provisional",
            "data_confidence": "third_party_published_average_low_quality",
        }
    )
    write_csv(stats_csv, ADMISSIONS_STATS_COLUMNS, [provisional])
    write_csv(candidates_csv, AACOM_PROFILE_CANDIDATE_COLUMNS, [])
    write_csv(
        extracted_csv,
        AACOM_EXTRACTED_STATS_COLUMNS,
        [
            {
                "school_id": "do_test",
                "school_name": "Test College of Osteopathic Medicine",
                "degree_type": "DO",
                "aacom_profile_url": "https://www.aacom.org/detail-pages/com/test-college-of-osteopathic-medicine",
                "aacom_profile_title": "Test College of Osteopathic Medicine",
                "fetch_status": "fetched",
                "extraction_status": "accepted",
                "stats_academic_year": "2024-25",
                "metric_population": "AACOM COM-submitted profile",
                "metric_type": "aacom_reported_mean",
                "mcat_mean": "510",
                "overall_gpa_mean": "3.65",
                "source_last_checked": "2026-06-08",
                "data_confidence": AACOM_DATA_CONFIDENCE,
                "review_status": "approved_aacom_extraction",
            }
        ],
    )

    count = aacom_do_apply.apply_aacom_do_stats()
    stats_rows = read_csv(stats_csv)
    conflict_rows = read_csv(conflicts_csv)
    coverage_rows = read_csv(coverage_csv)

    assert count == 1
    assert len(stats_rows) == 2
    assert stats_rows[0]["source_name"] == "AACOM Choose D.O. Explorer"
    assert stats_rows[0]["published_mcat_average"] == "510"
    assert stats_rows[0]["published_gpa_average"] == "3.65"
    assert stats_rows[1]["source_name"] == "Third-party source"
    assert conflict_rows[0]["conflict_status"] == "large_delta_review"
    assert coverage_rows[0]["coverage_status"] == "aacom_stats_applied"
    assert AACOM_CONFLICT_COLUMNS == list(conflict_rows[0].keys())
    assert AACOM_COVERAGE_COLUMNS == list(coverage_rows[0].keys())
