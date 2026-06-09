from __future__ import annotations

from pathlib import Path

from med_school_ranker import (
    md_official_apply,
    md_official_discovery,
    md_official_extraction,
    md_official_source_hunt,
    official_stats_extraction,
)
from med_school_ranker.md_official_rules import (
    MD_DATA_CONFIDENCE,
    MD_OFFICIAL_ASSISTED_SEARCH_SEED_COLUMNS,
    MD_OFFICIAL_COVERAGE_COLUMNS,
    MD_OFFICIAL_EXTRACTED_STATS_COLUMNS,
    MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    is_fetch_ready_source_type,
    md_source_type_hint,
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


def test_md_known_path_probe_discovers_live_class_profile(monkeypatch) -> None:
    school = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "state_abbrev": "FL",
        "website": "https://medicine.example.edu/",
    }

    def fake_fetch(url: str, timeout: int) -> tuple[str, str]:
        if url == "https://medicine.example.edu/admissions/class-profile/":
            return (
                "<html><title>MD Class Profile</title><body>Entering class profile median MCAT 512 and median GPA 3.84.</body></html>",
                "text/html",
            )
        return "", ""

    monkeypatch.setattr(md_official_discovery, "fetch_raw_url", fake_fetch)

    rows = md_official_discovery.discover_known_path_candidates(
        school,
        "https://medicine.example.edu/admissions/",
        timeout_seconds=1,
        max_probe_urls=5,
    )

    assert [row["candidate_source_url"] for row in rows] == ["https://medicine.example.edu/admissions/class-profile/"]
    assert rows[0]["candidate_source_type"] == "class_profile"
    assert rows[0]["review_status"] == "accepted_for_fetch"
    assert rows[0]["discovery_method"] == "official_known_path_probe"


def test_md_discovery_imports_assisted_search_seed(tmp_path: Path, monkeypatch) -> None:
    seeds_csv = tmp_path / "data/source_tables/md_official_assisted_search_seeds.csv"
    monkeypatch.setattr(md_official_discovery, "MD_OFFICIAL_ASSISTED_SEARCH_SEEDS_CSV", seeds_csv)
    school = {
        "school_id": "md_nyu",
        "school_name": "NYU Grossman School of Medicine",
        "degree_type": "MD",
        "state_abbrev": "NY",
        "website": "https://med.nyu.edu/",
    }
    write_csv(
        seeds_csv,
        MD_OFFICIAL_ASSISTED_SEARCH_SEED_COLUMNS,
        [
            {
                "school_id": "md_nyu",
                "school_name": "NYU Grossman School of Medicine",
                "degree_type": "MD",
                "candidate_source_url": "https://med.nyu.edu/education/md-degree/md-admissions/by-the-numbers",
                "candidate_source_title": "MD Admissions By the Numbers",
                "search_query": "NYU Grossman School of Medicine median MCAT GPA official",
                "search_provider": "google",
                "result_rank": "1",
                "discovered_date": "2026-06-08",
                "review_status": "approved_for_discovery",
            }
        ],
    )

    rows = md_official_discovery.rows_from_assisted_search_seeds({"md_nyu": school})

    assert len(rows) == 1
    assert rows[0]["candidate_source_url"].endswith("/by-the-numbers")
    assert rows[0]["review_status"] == "accepted_for_fetch"
    assert rows[0]["discovery_method"] == "assisted_search_official_url_seed"


def test_md_discovery_marks_reviewed_assisted_generic_urls_fetch_ready(tmp_path: Path, monkeypatch) -> None:
    seeds_csv = tmp_path / "data/source_tables/md_official_assisted_search_seeds.csv"
    monkeypatch.setattr(md_official_discovery, "MD_OFFICIAL_ASSISTED_SEARCH_SEEDS_CSV", seeds_csv)
    school = {
        "school_id": "md_fiu",
        "school_name": "Florida International University Herbert Wertheim College of Medicine",
        "degree_type": "MD",
        "state_abbrev": "FL",
        "website": "https://medicine.fiu.edu/",
    }
    write_csv(
        seeds_csv,
        MD_OFFICIAL_ASSISTED_SEARCH_SEED_COLUMNS,
        [
            {
                "school_id": "md_fiu",
                "school_name": "Florida International University Herbert Wertheim College of Medicine",
                "degree_type": "MD",
                "candidate_source_url": "https://medicine.fiu.edu/academics/doctor-of-medicine/faqs/",
                "candidate_source_title": "Doctor of Medicine FAQs",
                "search_query": "Florida International Herbert Wertheim College of Medicine class profile MCAT GPA official",
                "search_provider": "google",
                "result_rank": "3",
                "discovered_date": "2026-06-08",
                "review_status": "approved_for_discovery",
            }
        ],
    )

    rows = md_official_discovery.rows_from_assisted_search_seeds({"md_fiu": school})

    assert len(rows) == 1
    assert rows[0]["candidate_source_type"] == "admissions_page"
    assert rows[0]["review_status"] == "accepted_for_fetch"
    assert rows[0]["fetch_status"] == "not_fetched"


def test_md_source_type_treats_fact_sheet_and_class_of_pages_as_fetch_ready() -> None:
    fact_sheet_type = md_source_type_hint(
        "https://enews.msm.edu/Admissions/doctor-of-medicine/fact-sheet.php",
        "Doctor of Medicine (M.D.) Degree Fact Sheet",
    )
    class_news_type = md_source_type_hint(
        "https://www.usf.edu/health/news/2024/mcom-welcomes-class-of-2028.aspx",
        "USF Health Morsani College of Medicine welcomes newest future doctors",
    )

    assert is_fetch_ready_source_type(fact_sheet_type)
    assert is_fetch_ready_source_type(class_news_type)


def test_md_source_hunt_queue_prioritizes_pending_before_missing(tmp_path: Path, monkeypatch) -> None:
    master_csv = tmp_path / "data/school_master.csv"
    coverage_csv = tmp_path / "outputs/md_official_coverage.csv"
    extracted_csv = tmp_path / "data/source_tables/md_official_extracted_stats.csv"
    candidates_csv = tmp_path / "data/source_tables/md_official_source_candidates.csv"
    review_csv = tmp_path / "outputs/md_official_review_queue.csv"
    monkeypatch.setattr(md_official_source_hunt, "MASTER_CSV", master_csv)
    monkeypatch.setattr(md_official_source_hunt, "MD_OFFICIAL_COVERAGE_CSV", coverage_csv)
    monkeypatch.setattr(md_official_source_hunt, "MD_OFFICIAL_EXTRACTED_STATS_CSV", extracted_csv)
    monkeypatch.setattr(md_official_source_hunt, "MD_OFFICIAL_SOURCE_CANDIDATES_CSV", candidates_csv)
    monkeypatch.setattr(md_official_source_hunt, "MD_OFFICIAL_REVIEW_QUEUE_CSV", review_csv)
    write_csv(
        master_csv,
        ["school_id", "school_name", "degree_type", "city", "state_abbrev", "website", "active_in_universe", "manual_exclusion_flag"],
        [
            {
                "school_id": "md_pending",
                "school_name": "Pending School of Medicine",
                "degree_type": "MD",
                "city": "Miami",
                "state_abbrev": "FL",
                "website": "https://medicine.example.edu/",
                "active_in_universe": "TRUE",
                "manual_exclusion_flag": "FALSE",
            },
            {
                "school_id": "md_missing",
                "school_name": "Missing School of Medicine",
                "degree_type": "MD",
                "city": "Boston",
                "state_abbrev": "MA",
                "website": "https://missing.example.edu/",
                "active_in_universe": "TRUE",
                "manual_exclusion_flag": "FALSE",
            },
        ],
    )
    write_csv(
        coverage_csv,
        MD_OFFICIAL_COVERAGE_COLUMNS,
        [
            {
                "school_id": "md_missing",
                "school_name": "Missing School of Medicine",
                "degree_type": "MD",
                "candidate_count": "0",
                "official_candidate_count": "0",
                "fetched_candidate_count": "0",
                "accepted_extraction_count": "0",
                "current_canonical_has_mcat": "no",
                "current_canonical_has_gpa": "no",
                "coverage_status": "missing_candidate",
                "next_action": "Find source.",
            },
            {
                "school_id": "md_pending",
                "school_name": "Pending School of Medicine",
                "degree_type": "MD",
                "candidate_count": "1",
                "official_candidate_count": "1",
                "fetched_candidate_count": "1",
                "accepted_extraction_count": "0",
                "current_canonical_has_mcat": "yes",
                "current_canonical_has_gpa": "yes",
                "coverage_status": "md_official_candidate_pending_extraction",
                "next_action": "Improve parser.",
            },
        ],
    )
    write_csv(extracted_csv, MD_OFFICIAL_EXTRACTED_STATS_COLUMNS, [])
    write_csv(
        candidates_csv,
        MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
        [
            {
                "school_id": "md_pending",
                "school_name": "Pending School of Medicine",
                "candidate_source_url": "https://medicine.example.edu/admissions/class-profile/",
                "candidate_source_type": "class_profile",
                "official_domain_score": "1.00",
                "review_status": "accepted_for_fetch",
            }
        ],
    )
    write_csv(review_csv, ["school_id", "extraction_status"], [{"school_id": "md_pending", "extraction_status": "no_relevant_stats_found"}])

    rows = md_official_source_hunt.build_source_hunt_queue()

    assert [row["school_id"] for row in rows] == ["md_pending", "md_missing"]
    assert rows[0]["hunt_bucket"] == "parser_or_extraction_pending"
    assert 'site:example.edu "Pending School of Medicine" "MCAT" "GPA"' == rows[0]["google_query_site_specific"]


def test_md_extraction_fetches_reviewed_assisted_url_with_generic_path() -> None:
    candidate = {
        "review_status": "accepted_for_fetch",
        "candidate_source_type": "admissions_page",
        "discovery_method": "assisted_search_official_url_seed",
        "official_domain_score": "1.00",
    }

    ready, skip_status, notes = md_official_extraction.should_fetch_candidate(candidate, fetch_domain_seeds=False)

    assert ready is True
    assert skip_status == ""
    assert "assisted-search" in notes


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


def test_md_extractor_accepts_undergraduate_gpa_as_overall_gpa() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/by-the-numbers",
        "candidate_source_title": "Admissions By the Numbers",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "The incoming class had a median MCAT score of 523. Their median undergraduate GPA was 3.98."

    row = md_extracted_row(candidate, text, "Admissions By the Numbers")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "523"
    assert row["gpa_value"] == "3.98"


def test_md_extractor_does_not_reject_overall_gpa_followed_by_bcpm_metric() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/entering-class-profile",
        "candidate_source_title": "Entering M.D. Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Entering M.D. Class Profile Applications 4,165 Mean MCAT 515 Mean GPA 3.85 Mean BCPM 3.82."

    row = md_extracted_row(candidate, text, "Entering M.D. Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "515"
    assert row["gpa_value"] == "3.85"


def test_md_extractor_accepts_mcat_composite_in_class_composition() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/entering-class-profile",
        "candidate_source_title": "2025 Entering Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "2025 Entering Class Profile Class Composition Class GPA: 3.83 Class Science GPA: 3.79 MCAT composite: 514"

    row = md_extracted_row(candidate, text, "2025 Entering Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "514"
    assert row["gpa_value"] == "3.83"


def test_md_extractor_uses_latest_shared_cohort_year_on_multi_year_pages() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/fact-sheet",
        "candidate_source_title": "Fact Sheet",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = """
    Entering Class of 2022 Total Applied 7,096 Matriculated 125
    Average GPA 3.53 Average Science GPA 3.42 Average MCAT 503.
    Entering Class of 2024 Total Applied 6,858 Matriculated 105
    Average GPA 3.45 Average Science GPA 3.38 Average MCAT 506.
    """

    row = md_extracted_row(candidate, text, "Fact Sheet")

    assert row["extraction_status"] == "accepted"
    assert row["stats_cohort_year"] == "2024"
    assert row["mcat_value"] == "506"
    assert row["gpa_value"] == "3.45"


def test_md_extractor_accepts_official_gpa_range_with_mcat_respectively() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/faq",
        "candidate_source_title": "Admissions FAQ",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = (
        "What are your minimum GPA and MCAT requirements? We do not have a minimum GPA or MCAT score. "
        "However, the average GPA and MCAT scores for matriculating students are typically 3.7-3.75 and 509, respectively."
    )

    row = md_extracted_row(candidate, text, "Admissions FAQ")

    assert row["extraction_status"] == "accepted"
    assert row["metric_type"] == "official_published_range_midpoint"
    assert row["mcat_value"] == "509"
    assert row["gpa_value"] == "3.73"
    assert "range-derived" in row["notes"]


def test_md_extractor_accepts_official_class_profile_ranges_as_midpoints() -> None:
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
    text = "Entering class profile for class of 2029. Matriculants had MCAT score range 508-514 and cumulative GPA range 3.70-3.90."

    row = md_extracted_row(candidate, text, "Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["metric_type"] == "official_published_range_midpoint"
    assert row["mcat_value"] == "511"
    assert row["mcat_metric"] == "range_midpoint"
    assert row["gpa_value"] == "3.8"
    assert row["gpa_metric"] == "range_midpoint"
    assert "range-derived" in row["notes"]


def test_md_extractor_accepts_noisy_pdf_class_average_values() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/preparedness-worksheet.pdf",
        "candidate_source_title": "Preparedness Worksheet",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = (
        "Academic Measurables. MCAT - The MCAT exam predicts performance on USMLE Step 1 - "
        "511 College of Medicine average score for the 2024 matriculating class. "
        "G PA - Predicts preparedness for medical school curriculum - "
        "3.83 Average total GPA for the College of Medicine 2024 matriculating class."
    )

    row = md_extracted_row(candidate, text, "Preparedness Worksheet")

    assert row["extraction_status"] == "accepted"
    assert row["stats_cohort_year"] == "2024"
    assert row["mcat_value"] == "511"
    assert row["gpa_value"] == "3.83"


def test_md_extractor_accepts_card_style_overall_gpa_after_value() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/doctor-of-medicine/",
        "candidate_source_title": "Doctor of Medicine",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class of 2029 Profile 503 Average MCAT 3.62 Average BCPM GPA 3.69 Average Overall GPA Admissions Process"

    row = md_extracted_row(candidate, text, "Doctor of Medicine")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "503"
    assert row["gpa_value"] == "3.69"


def test_md_extractor_rejects_card_style_bcpm_when_mean_gpa_is_available() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/class-profiles",
        "candidate_source_title": "Class Profiles",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class of 2029 Class Profile 513 Median MCAT 3.89 Mean GPA 3.87 Mean BCPM GPA Class performance information"

    row = md_extracted_row(candidate, text, "Class Profiles")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "513"
    assert row["gpa_value"] == "3.89"
    assert row["gpa_metric"] == "mean"


def test_md_extractor_accepts_mcat_2015_score_label() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/md-class-profile",
        "candidate_source_title": "Class Profile",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class of 2029 Academics An average undergraduate GPA of 3.81. An average MCAT 2015 score of 513.06."

    row = md_extracted_row(candidate, text, "Class Profile")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "513"
    assert row["gpa_value"] == "3.81"


def test_md_extractor_accepts_mcat_section_total() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions-at-a-glance",
        "candidate_source_title": "Admissions at a Glance",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class of 2029 Average MCAT BBFL 130.38 CARS 128.82 CPBS 130.28 PSBB 130.99 Total 520.48 Average GPA 3.9"

    row = md_extracted_row(candidate, text, "Admissions at a Glance")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "520.4"
    assert row["gpa_value"] == "3.9"


def test_md_extractor_accepts_gpa_mcat_table_pairs() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/selection-factors/",
        "candidate_source_title": "Selection Factors",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = (
        "Entering Class of 2025. Summary of GPA and MCAT Scores for matriculated student data. "
        "Category GPA MCAT Mean 3.76 517 Median 3.84 517"
    )

    row = md_extracted_row(candidate, text, "Selection Factors")

    assert row["extraction_status"] == "accepted"
    assert row["metric_type"] == "official_published_median"
    assert row["mcat_value"] == "517"
    assert row["gpa_value"] == "3.84"


def test_md_extractor_accepts_class_profile_year_grid() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/",
        "candidate_source_title": "Admissions",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = (
        "Class Profiles Get a snapshot of the classes entering over the past three years. "
        "2025 2024 2023 Applied 4207 4320 4448 Enrolled 196 190 186 "
        "MCAT Score 509.4 509 509.5 Average GPA 3.87 3.83 3.83 "
        "Explore Admissions Selection Criteria Read the minimum requirements."
    )

    row = md_extracted_row(candidate, text, "Admissions")

    assert row["extraction_status"] == "accepted"
    assert row["stats_cohort_year"] == "2025"
    assert row["mcat_value"] == "509.4"
    assert row["gpa_value"] == "3.87"


def test_md_extractor_accepts_average_total_gpa_with_mcat() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/statistics/",
        "candidate_source_title": "Statistics of Entering Classes",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Current accepted students: 96 Academic Profile Average GPA BCPM: 3.76 All other: 3.89 Total: 3.82 Average MCAT 512"

    row = md_extracted_row(candidate, text, "Statistics of Entering Classes")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "512"
    assert row["gpa_value"] == "3.82"


def test_md_extractor_prefers_median_when_mean_and_median_are_available() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/admissions/our-students",
        "candidate_source_title": "Our Students",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "Class of 2029 Profile Mean MCAT 514 Median MCAT 515 Mean GPA (total) 3.78 Median GPA (total) 3.84"

    row = md_extracted_row(candidate, text, "Our Students")

    assert row["extraction_status"] == "accepted"
    assert row["metric_type"] == "official_published_median"
    assert row["mcat_value"] == "515"
    assert row["mcat_metric"] == "median"
    assert row["gpa_value"] == "3.84"
    assert row["gpa_metric"] == "median"


def test_md_extractor_rejects_requirement_ranges_as_admissions_stats() -> None:
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
    text = "Applicants are required to have MCAT score range 500-528 and cumulative GPA range 3.00-4.00."

    row = md_extracted_row(candidate, text, "Requirements")

    assert row["extraction_status"] == "rejected_minimum_requirement"
    assert row["mcat_value"] == ""
    assert row["gpa_value"] == ""


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


def test_md_extractor_rejects_non_md_program_profile_values() -> None:
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/pa/admissions/statistics/",
        "candidate_source_title": "Physician Assistant Program Statistics",
        "candidate_source_type": "class_profile",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = "PA program class profile. Matriculants had a median MCAT score of 514 and median GPA of 3.82."

    row = md_extracted_row(candidate, text, "Physician Assistant Program Statistics")

    assert row["extraction_status"] == "rejected_non_md_program_context"
    assert row["data_confidence"] == ""
    assert row["review_status"] == "needs_review"


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


def test_md_extraction_can_fetch_official_domain_seed_when_requested(tmp_path: Path, monkeypatch) -> None:
    extracted_csv = tmp_path / "data/source_tables/md_official_extracted_stats.csv"
    candidates_csv = tmp_path / "data/source_tables/md_official_source_candidates.csv"
    review_csv = tmp_path / "outputs/md_official_review_queue.csv"

    monkeypatch.setattr(md_official_extraction, "MD_OFFICIAL_EXTRACTED_STATS_CSV", extracted_csv)
    monkeypatch.setattr(md_official_extraction, "MD_OFFICIAL_SOURCE_CANDIDATES_CSV", candidates_csv)
    monkeypatch.setattr(md_official_extraction, "MD_OFFICIAL_REVIEW_QUEUE_CSV", review_csv)
    monkeypatch.setattr(
        md_official_extraction,
        "fetch_candidate_text",
        lambda url, timeout: (
            "fetched",
            "MD Admissions",
            "MD admissions entering class profile. Matriculants had a median MCAT score of 512 and median cumulative GPA of 3.84.",
            "",
        ),
    )
    write_csv(
        candidates_csv,
        MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
        [
            {
                "school_id": "md_test",
                "school_name": "Test College of Medicine",
                "degree_type": "MD",
                "candidate_source_url": "https://medicine.example.edu/md-admissions/",
                "candidate_source_title": "MD Admissions",
                "candidate_source_type": "admissions_page",
                "source_host": "medicine.example.edu",
                "official_domain_status": "official_school_domain",
                "official_domain_score": "1.00",
                "review_status": "official_domain_seed_needs_stats_path",
            }
        ],
    )

    default_rows = md_official_extraction.build_md_official_extraction(fetch=True)
    relaxed_rows = md_official_extraction.build_md_official_extraction(fetch=True, fetch_domain_seeds=True)

    assert default_rows[0]["extraction_status"] == "fetch_skipped_needs_stats_path"
    assert relaxed_rows[0]["extraction_status"] == "accepted"
    assert relaxed_rows[0]["mcat_value"] == "512"
    assert relaxed_rows[0]["gpa_value"] == "3.84"
    assert "less conservative mode" in relaxed_rows[0]["notes"]


def test_fetch_candidate_text_extracts_pdf_text(monkeypatch) -> None:
    class FakePage:
        def extract_text(self) -> str:
            return "Class profile median MCAT score of 512 and median GPA of 3.84."

    class FakeReader:
        def __init__(self, stream) -> None:
            self.pages = [FakePage()]

    class FakeResponse:
        headers = {"content-type": "application/pdf"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def read(self) -> bytes:
            return b"%PDF fake"

    monkeypatch.setattr(official_stats_extraction, "PdfReader", FakeReader)
    monkeypatch.setattr(official_stats_extraction.urllib.request, "urlopen", lambda request, timeout: FakeResponse())

    status, title, text, notes = official_stats_extraction.fetch_candidate_text("https://medicine.example.edu/class-profile.pdf", 1)

    assert status == "fetched"
    assert title == "class-profile.pdf"
    assert "median MCAT score of 512" in text
    assert notes == ""


def test_fetch_candidate_text_extracts_image_ocr_text(monkeypatch) -> None:
    class FakeResponse:
        headers = {"content-type": "image/png"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def read(self) -> bytes:
            return b"fake image"

    class FakeResult:
        returncode = 0
        stdout = "Class profile median MCAT score of 512 and median GPA of 3.84."
        stderr = ""

    monkeypatch.setattr(official_stats_extraction.urllib.request, "urlopen", lambda request, timeout: FakeResponse())
    monkeypatch.setattr(official_stats_extraction.shutil, "which", lambda command: "/usr/local/bin/tesseract")
    monkeypatch.setattr(official_stats_extraction.subprocess, "run", lambda *args, **kwargs: FakeResult())

    status, title, text, notes = official_stats_extraction.fetch_candidate_text("https://medicine.example.edu/class-profile.png", 1)

    assert status == "fetched"
    assert title == "class-profile.png"
    assert "median MCAT score of 512" in text
    assert notes == ""


def test_md_extractor_corrects_impossible_image_ocr_gpa() -> None:
    candidate = {
        "school_id": "md_ucf",
        "school_name": "University of Central Florida College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://med.ucf.edu/media/2025/10/CL2029-Class-Profile-Corrected.png",
        "candidate_source_title": "Class Profile Image",
        "candidate_source_type": "class_profile",
        "source_host": "med.ucf.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
    }
    text = (
        "CLASS OF 2029 PROFILE Verified Applications Average Total GPA 5,394 5.90 "
        "Interviews Average Science GPA 512 5.87 Matriculated Average MCAT 120 514"
    )

    row = md_extracted_row(candidate, text, "Class Profile Image")

    assert row["extraction_status"] == "accepted"
    assert row["mcat_value"] == "514"
    assert row["gpa_value"] == "3.9"
    assert "OCR correction" in row["notes"]


def test_md_extraction_refetches_existing_pdf_skips(tmp_path: Path, monkeypatch) -> None:
    extracted_csv = tmp_path / "data/source_tables/md_official_extracted_stats.csv"
    candidates_csv = tmp_path / "data/source_tables/md_official_source_candidates.csv"
    review_csv = tmp_path / "outputs/md_official_review_queue.csv"

    monkeypatch.setattr(md_official_extraction, "MD_OFFICIAL_EXTRACTED_STATS_CSV", extracted_csv)
    monkeypatch.setattr(md_official_extraction, "MD_OFFICIAL_SOURCE_CANDIDATES_CSV", candidates_csv)
    monkeypatch.setattr(md_official_extraction, "MD_OFFICIAL_REVIEW_QUEUE_CSV", review_csv)
    monkeypatch.setattr(
        md_official_extraction,
        "fetch_candidate_text",
        lambda url, timeout: (
            "fetched",
            "Class Profile PDF",
            "MD entering class profile. Matriculants had a median MCAT score of 512 and median cumulative GPA of 3.84.",
            "",
        ),
    )
    candidate = {
        "school_id": "md_test",
        "school_name": "Test College of Medicine",
        "degree_type": "MD",
        "candidate_source_url": "https://medicine.example.edu/class-profile.pdf",
        "candidate_source_title": "Class Profile PDF",
        "candidate_source_type": "pdf_report",
        "source_host": "medicine.example.edu",
        "official_domain_status": "official_school_domain",
        "official_domain_score": "1.00",
        "review_status": "accepted_for_fetch",
    }
    write_csv(candidates_csv, MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS, [candidate])
    skipped = {column: "" for column in MD_OFFICIAL_EXTRACTED_STATS_COLUMNS}
    skipped.update(candidate)
    skipped.update(
        {
            "fetch_status": "unsupported_pdf_without_parser",
            "extraction_status": "unsupported_pdf_without_parser",
            "review_status": "needs_review",
        }
    )
    write_csv(extracted_csv, MD_OFFICIAL_EXTRACTED_STATS_COLUMNS, [skipped])

    reused_rows = md_official_extraction.build_md_official_extraction(fetch=True, reuse_existing=True)
    refetched_rows = md_official_extraction.build_md_official_extraction(
        fetch=True,
        reuse_existing=True,
        refetch_statuses={"unsupported_pdf_without_parser"},
    )

    assert reused_rows[0]["extraction_status"] == "unsupported_pdf_without_parser"
    assert refetched_rows[0]["extraction_status"] == "accepted"
    assert refetched_rows[0]["mcat_value"] == "512"
    assert refetched_rows[0]["gpa_value"] == "3.84"


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
