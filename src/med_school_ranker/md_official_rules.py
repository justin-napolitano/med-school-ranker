from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from med_school_ranker.official_source_rules import (
    OfficialSourceClassification,
    classify_official_source,
    clean,
    format_float,
    is_truthy,
    normalized_host,
    registrable_domain,
)


MD_DATA_CONFIDENCE = "md_official_public_source"

MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "state_abbrev",
    "school_website",
    "candidate_source_url",
    "candidate_source_title",
    "candidate_source_type",
    "source_host",
    "official_domain_status",
    "official_domain_score",
    "official_match_reason",
    "discovery_method",
    "search_or_sitemap_query",
    "source_last_checked",
    "fetch_status",
    "review_status",
    "notes",
]

MD_OFFICIAL_ASSISTED_SEARCH_SEED_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_source_url",
    "candidate_source_title",
    "search_query",
    "search_provider",
    "result_rank",
    "discovered_date",
    "review_status",
    "notes",
]

MD_OFFICIAL_EXTRACTED_STATS_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_source_url",
    "candidate_source_title",
    "candidate_source_type",
    "source_host",
    "official_domain_status",
    "official_domain_score",
    "fetch_status",
    "extraction_status",
    "stats_cohort_year",
    "metric_population",
    "metric_type",
    "mcat_value",
    "mcat_metric",
    "gpa_value",
    "gpa_metric",
    "science_gpa_value",
    "evidence_text",
    "source_publication_date",
    "source_last_checked",
    "data_confidence",
    "review_status",
    "notes",
]

MD_OFFICIAL_DISCOVERY_REPORT_COLUMNS = [
    "metric",
    "count",
    "notes",
]

MD_OFFICIAL_REVIEW_QUEUE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_source_url",
    "candidate_source_title",
    "candidate_source_type",
    "source_host",
    "official_domain_status",
    "official_domain_score",
    "fetch_status",
    "extraction_status",
    "review_status",
    "review_reason",
    "evidence_text",
    "recommended_action",
    "last_checked",
    "notes",
]

MD_OFFICIAL_COVERAGE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_count",
    "official_candidate_count",
    "fetched_candidate_count",
    "accepted_extraction_count",
    "current_canonical_has_mcat",
    "current_canonical_has_gpa",
    "coverage_status",
    "next_action",
]

MD_OFFICIAL_CONFLICT_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "current_mcat",
    "current_gpa",
    "official_mcat",
    "official_gpa",
    "mcat_delta",
    "gpa_delta",
    "current_source_name",
    "current_source_url",
    "official_source_url",
    "conflict_status",
    "notes",
]

MD_STATS_PATH_TERMS = (
    "class-profile",
    "class_profile",
    "classprofile",
    "student-profile",
    "student_profile",
    "entering-class",
    "entering_class",
    "incoming-class",
    "incoming_class",
    "matriculant",
    "matriculants",
    "facts-and-figures",
    "facts_figures",
    "facts",
    "figures",
    "fact-sheet",
    "fact_sheet",
    "admissions-statistics",
    "admissions_statistics",
    "class-statistics",
    "class_statistics",
    "by-the-numbers",
    "annual-report",
    "annual_report",
    "fact-book",
    "factbook",
)

MD_STATS_TEXT_TERMS = (
    "class profile",
    "class of",
    "student profile",
    "entering class",
    "incoming class",
    "matriculant",
    "matriculants",
    "facts and figures",
    "admissions statistics",
    "class statistics",
    "by the numbers",
    "annual report",
    "fact book",
    "fact sheet",
)

MD_ADMISSIONS_PATH_TERMS = (
    "admission",
    "admissions",
    "apply",
    "application",
    "requirements",
    "md-program",
    "doctor-of-medicine",
    "medicine",
)

MD_PROGRAM_PATH_TERMS = (
    "allopathic medicine",
    "college medicine",
    "doctor medicine",
    "doctor of medicine",
    "medicine md",
    "md program",
    "md admissions",
    "medical school",
    "school medicine",
    "school of medicine",
    "chicago medical school",
)

MD_SCOPED_HOST_PREFIXES = (
    "med.",
    "medschool.",
    "medicine.",
    "som.",
)

NON_MD_PROGRAM_TERMS = (
    "ba md",
    "dental",
    "dentistry",
    "dmd",
    "graduate program",
    "master of",
    "masters",
    "md phd",
    "md/phd",
    "mph",
    "mstp",
    "nursing",
    "occupational therapy",
    "pa admissions",
    "pa online",
    "pa program",
    "pharmacy",
    "physical therapy",
    "physician assistant",
    "school of dentistry",
    "veterinary",
)


def today_iso() -> str:
    return date.today().isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def path_text(url: str) -> str:
    parsed = urlparse(clean(url))
    text = " ".join([parsed.path, parsed.query, parsed.fragment])
    return re.sub(r"[%_\-/]+", " ", text.lower())


def same_registrable_domain(left_url: str, right_url: str) -> bool:
    left_host = normalized_host(left_url)
    right_host = normalized_host(right_url)
    return bool(left_host and right_host and registrable_domain(left_host) == registrable_domain(right_host))


def is_md_stats_like(url: str, title: str = "", text: str = "") -> bool:
    haystack = " ".join([path_text(url), clean(title).lower(), clean(text).lower()])
    return any(term in haystack for term in MD_STATS_PATH_TERMS + MD_STATS_TEXT_TERMS)


def is_md_admissions_like(url: str, title: str = "", text: str = "") -> bool:
    haystack = " ".join([path_text(url), clean(title).lower(), clean(text).lower()])
    return any(term in haystack for term in MD_ADMISSIONS_PATH_TERMS)


def is_md_program_relevant_url(candidate_url: str, seed_url: str = "", title: str = "") -> bool:
    candidate_host = normalized_host(candidate_url)
    if any(candidate_host.startswith(prefix) for prefix in MD_SCOPED_HOST_PREFIXES):
        return True
    haystack = " ".join([path_text(candidate_url), clean(title).lower()])
    if any(term in haystack for term in MD_PROGRAM_PATH_TERMS):
        return True
    seed_terms = set(path_text(seed_url).split()) & {"medicine", "medical", "med", "md", "som"}
    candidate_terms = set(path_text(candidate_url).split())
    return bool(seed_terms & candidate_terms)


def is_non_md_program_context(candidate_url: str, title: str = "", text: str = "") -> bool:
    haystack = " ".join([path_text(candidate_url), clean(title).lower()])
    return any(term in haystack for term in NON_MD_PROGRAM_TERMS)


def md_source_type_hint(url: str, title: str = "", text: str = "") -> str:
    lower_url = clean(url).lower().split("?", 1)[0]
    if lower_url.endswith(".pdf"):
        return "pdf_report"
    if is_md_stats_like(url, title, text):
        haystack = " ".join([path_text(url), clean(title).lower(), clean(text).lower()])
        if "annual report" in haystack or "annual-report" in haystack or "fact book" in haystack or "factbook" in haystack:
            return "annual_report"
        if "statistic" in haystack:
            return "admissions_statistics"
        return "class_profile"
    if is_md_admissions_like(url, title, text):
        return "admissions_page"
    return "unknown"


def md_source_classification(
    school: dict[str, str],
    candidate_url: str,
    candidate_title: str = "",
    candidate_text: str = "",
) -> OfficialSourceClassification:
    return classify_official_source(school, candidate_url, candidate_title, candidate_text)


def is_fetch_ready_source_type(source_type: str) -> bool:
    return clean(source_type) in {"class_profile", "annual_report", "admissions_statistics", "pdf_report"}


__all__ = [
    "MD_DATA_CONFIDENCE",
    "MD_OFFICIAL_ASSISTED_SEARCH_SEED_COLUMNS",
    "MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS",
    "MD_OFFICIAL_EXTRACTED_STATS_COLUMNS",
    "MD_OFFICIAL_DISCOVERY_REPORT_COLUMNS",
    "MD_OFFICIAL_REVIEW_QUEUE_COLUMNS",
    "MD_OFFICIAL_COVERAGE_COLUMNS",
    "MD_OFFICIAL_CONFLICT_COLUMNS",
    "clean",
    "format_float",
    "is_fetch_ready_source_type",
    "is_md_admissions_like",
    "is_md_program_relevant_url",
    "is_non_md_program_context",
    "is_md_stats_like",
    "is_truthy",
    "md_source_classification",
    "md_source_type_hint",
    "normalized_host",
    "read_csv",
    "same_registrable_domain",
    "today_iso",
    "write_csv",
]
