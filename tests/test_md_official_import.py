from __future__ import annotations

from pathlib import Path

from med_school_ranker import md_official_apply, md_official_discovery
from med_school_ranker.md_official_rules import (
    MD_DATA_CONFIDENCE,
    MD_OFFICIAL_COVERAGE_COLUMNS,
    MD_OFFICIAL_EXTRACTED_STATS_COLUMNS,
    MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    read_csv,
    write_csv,
)
from med_school_ranker.md_official_extraction import md_extracted_row
from med_school_ranker.validation import ADMISSIONS_STATS_COLUMNS


def test_md_sitemap_discovery_keeps_only_stats_like_urls(monkeypatch) -> None:
    school = {
        "school_id": "md_uf",
        "school_name": "University of Florida College of Medicine",
        "degree_type": "MD",
        "state_abbrev": "FL",
    }
    sitemap = """
    <urlset>
      <url><loc>https://med.ufl.edu/admissions/class-profile/</loc></url>
      <url><loc>https://med.ufl.edu/admissions/tuition/</loc></url>
      <url><loc>https://med.ufl.edu/about/facts-and-figures/</loc></url>
      <url><loc>https://www.ufl.edu/law/admissions/class-profile/</loc></url>
    </urlset>
    """

    monkeypatch.setattr(md_official_discovery, "sitemap_urls_from_robots", lambda origin, timeout: [])
    monkeypatch.setattr(md_official_discovery, "fetch_raw_url", lambda url, timeout: (sitemap, "application/xml"))

    rows = md_official_discovery.discover_sitemap_candidates(
        school,
        "https://med.ufl.edu/admissions/",
        timeout_seconds=1,
        max_sitemap_urls=20,
    )

    urls = {row["candidate_source_url"] for row in rows}
    assert "https://med.ufl.edu/admissions/class-profile/" in urls
    assert "https://med.ufl.edu/about/facts-and-figures/" in urls
    assert "https://med.ufl.edu/admissions/tuition/" not in urls
    assert "https://www.ufl.edu/law/admissions/class-profile/" not in urls
    assert all(row["review_status"] == "accepted_for_fetch" for row in rows)


def test_md_extractor_accepts_class_profile_values() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/class-profile/",
        "candidate_source_title": "Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class Profile for the entering class of 2028. Matriculants had a median MCAT score of 514 and median GPA of 3.82."

    row = md_extracted_row(candidate, text, "Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["data_confidence"] == MD_DATA_CONFIDENCE
    assert row["degree_type"] == "MD"
    assert row["mcat_value"] == "514"
    assert row["gpa_value"] == "3.82"
    assert row["evidence_text"]


def test_md_extractor_prefers_cumulative_gpa_over_science_gpa() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/class-profile/",
        "candidate_source_title": "Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = """
    2025 Entering Class Class Size 203.
    GPA - Cumulative 3.69 GPA - Science 3.59 Entrance Exam (MCAT) 508.
    """

    row = md_extracted_row(candidate, text, "Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "508"
    assert row["gpa_value"] == "3.69"


def test_md_extractor_prefers_total_gpa_over_science_and_graduate_gpa() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/class-profile/",
        "candidate_source_title": "Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = """
    Academic Performance Average Total GPA: 3.78 Average Total Science GPA: 3.71
    Average Total Graduate GPA: 3.65 MCAT Results Average Total MCAT: 510.
    """

    row = md_extracted_row(candidate, text, "Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "510"
    assert row["gpa_value"] == "3.78"


def test_md_extractor_does_not_accept_bcpm_as_overall_gpa() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/class-profile/",
        "candidate_source_title": "Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class Profile Metrics Average BCPM GPA: 3.80 Average MCAT Total: 511."

    row = md_extracted_row(candidate, text, "Class Profile")

    assert row["extraction_status"] == "needs_review_partial_stats"
    assert row["mcat_value"] == "511"
    assert row["gpa_value"] == ""


def test_md_extractor_rejects_minimum_requirement_values() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/requirements/",
        "candidate_source_title": "Requirements",
        "candidate_source_type": "admissions_page",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Applicants must meet a minimum MCAT score of 500 and a minimum cumulative GPA of 3.0."

    row = md_extracted_row(candidate, text, "Requirements")

    assert row["extraction_status"] == "rejected_minimum_requirement"
    assert row["data_confidence"] == ""
    assert row["mcat_value"] == ""
    assert row["gpa_value"] == ""


def test_md_apply_promotes_only_accepted_md_official_row(tmp_path: Path, monkeypatch) -> None:
    master_csv = tmp_path / "data/school_master.csv"
    stats_csv = tmp_path / "data/normalized/admissions_stats.csv"
    extracted_csv = tmp_path / "data/source_tables/md_official_extracted_stats.csv"
    candidates_csv = tmp_path / "data/source_tables/md_official_source_candidates.csv"
    conflicts_csv = tmp_path / "outputs/md_official_conflicts.csv"
    coverage_csv = tmp_path / "outputs/md_official_coverage.csv"

    monkeypatch.setattr(md_official_apply, "MASTER_CSV", master_csv)
    monkeypatch.setattr(md_official_apply, "ADMISSIONS_STATS_CSV", stats_csv)
    monkeypatch.setattr(md_official_apply, "MD_OFFICIAL_EXTRACTED_STATS_CSV", extracted_csv)
    monkeypatch.setattr(md_official_apply, "MD_OFFICIAL_SOURCE_CANDIDATES_CSV", candidates_csv)
    monkeypatch.setattr(md_official_apply, "MD_OFFICIAL_CONFLICTS_CSV", conflicts_csv)
    monkeypatch.setattr(md_official_apply, "MD_OFFICIAL_COVERAGE_CSV", coverage_csv)

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
            },
            {
                "school_id": "do_test",
                "school_name": "Test College of Osteopathic Medicine",
                "degree_type": "DO",
                "active_in_universe": "TRUE",
                "manual_exclusion_flag": "FALSE",
            },
        ],
    )
    provisional_md = {column: "" for column in ADMISSIONS_STATS_COLUMNS}
    provisional_md.update(
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
    do_row = {column: "" for column in ADMISSIONS_STATS_COLUMNS}
    do_row.update(
        {
            "school_id": "do_test",
            "school_name": "Test College of Osteopathic Medicine",
            "degree_type": "DO",
            "published_mcat_average": "502",
            "published_gpa_average": "3.5",
            "source_name": "Existing DO source",
            "source_url": "https://example.edu/do",
            "data_confidence": "third_party_published_average_low_quality",
        }
    )
    write_csv(stats_csv, ADMISSIONS_STATS_COLUMNS, [provisional_md, do_row])
    write_csv(candidates_csv, MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS, [])
    write_csv(
        extracted_csv,
        MD_OFFICIAL_EXTRACTED_STATS_COLUMNS,
        [
            {
                "school_id": "md_test",
                "school_name": "Test College of Medicine",
                "degree_type": "MD",
                "candidate_source_url": "https://medicine.example.edu/admissions/class-profile",
                "candidate_source_title": "Class Profile",
                "candidate_source_type": "class_profile",
                "source_host": "medicine.example.edu",
                "official_domain_status": "official_school_domain",
                "official_domain_score": "1.00",
                "fetch_status": "fetched",
                "extraction_status": "accepted",
                "stats_cohort_year": "2028",
                "metric_population": "matriculated students",
                "metric_type": "official_published_median",
                "mcat_value": "512",
                "mcat_metric": "median",
                "gpa_value": "3.84",
                "gpa_metric": "median",
                "evidence_text": "Class profile median MCAT score of 512 and median GPA of 3.84.",
                "source_last_checked": "2026-06-08",
                "data_confidence": MD_DATA_CONFIDENCE,
                "review_status": "approved_official_extraction",
            }
        ],
    )

    count = md_official_apply.apply_md_official_stats()
    stats_rows = read_csv(stats_csv)
    conflict_rows = read_csv(conflicts_csv)
    coverage_rows = read_csv(coverage_csv)

    assert count == 1
    assert len(stats_rows) == 2
    assert stats_rows[0]["school_id"] == "md_test"
    assert stats_rows[0]["source_name"] == "Official MD school source"
    assert stats_rows[0]["data_confidence"] == MD_DATA_CONFIDENCE
    assert stats_rows[1]["school_id"] == "do_test"
    assert conflict_rows[0]["conflict_status"] == "large_delta_review"
    assert MD_OFFICIAL_COVERAGE_COLUMNS == list(coverage_rows[0].keys())
