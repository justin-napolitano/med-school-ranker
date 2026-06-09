from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from urllib.parse import urlparse

from med_school_ranker.md_official_rules import clean, normalized_host, read_csv, write_csv
from med_school_ranker.paths import (
    MASTER_CSV,
    MD_OFFICIAL_COVERAGE_CSV,
    MD_OFFICIAL_EXTRACTED_STATS_CSV,
    MD_OFFICIAL_REVIEW_QUEUE_CSV,
    MD_OFFICIAL_SOURCE_CANDIDATES_CSV,
    MD_OFFICIAL_SOURCE_HUNT_QUEUE_CSV,
    ROOT,
)


SOURCE_HUNT_QUEUE_COLUMNS = [
    "priority_rank",
    "hunt_bucket",
    "school_id",
    "school_name",
    "state_abbrev",
    "city",
    "coverage_status",
    "candidate_count",
    "official_candidate_count",
    "fetched_candidate_count",
    "current_canonical_has_mcat",
    "current_canonical_has_gpa",
    "best_existing_candidate_url",
    "best_existing_candidate_status",
    "review_status_summary",
    "next_action",
    "official_source_policy",
    "google_query_site_specific",
    "google_query_class_profile",
    "google_query_entering_class",
    "google_query_statistics",
    "google_query_fact_sheet",
    "google_query_annual_report",
]


BUCKET_ORDER = {
    "parser_or_extraction_pending": 1,
    "official_domain_path_needed": 2,
    "official_url_search_needed": 3,
    "candidate_needs_review": 4,
}


def active_md_school_index() -> dict[str, dict[str, str]]:
    schools = {}
    for row in read_csv(MASTER_CSV):
        school_id = clean(row.get("school_id"))
        if clean(row.get("degree_type")).upper() != "MD" or not school_id:
            continue
        if clean(row.get("active_in_universe")).upper() == "FALSE":
            continue
        if clean(row.get("manual_exclusion_flag")).upper() == "TRUE":
            continue
        schools[school_id] = row
    return schools


def accepted_school_ids() -> set[str]:
    return {
        clean(row.get("school_id"))
        for row in read_csv(MD_OFFICIAL_EXTRACTED_STATS_CSV)
        if clean(row.get("extraction_status")) == "accepted" and clean(row.get("school_id"))
    }


def candidate_summary_by_school() -> dict[str, dict[str, str]]:
    summary: dict[str, dict[str, str]] = {}
    for row in read_csv(MD_OFFICIAL_SOURCE_CANDIDATES_CSV):
        school_id = clean(row.get("school_id"))
        url = clean(row.get("candidate_source_url"))
        if not school_id or not url:
            continue
        existing = summary.get(school_id)
        score = float(clean(row.get("official_domain_score")) or 0)
        status = clean(row.get("review_status"))
        source_type = clean(row.get("candidate_source_type"))
        rank = (
            status == "accepted_for_fetch",
            source_type in {"class_profile", "admissions_statistics", "annual_report", "pdf_report"},
            score,
        )
        if not existing or rank > existing["_rank"]:
            summary[school_id] = {
                "best_existing_candidate_url": url,
                "best_existing_candidate_status": status,
                "_rank": rank,
            }
    return summary


def review_summary_by_school() -> dict[str, str]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in read_csv(MD_OFFICIAL_REVIEW_QUEUE_CSV):
        school_id = clean(row.get("school_id"))
        status = clean(row.get("extraction_status"))
        if school_id and status:
            counters[school_id][status] += 1
    return {
        school_id: "; ".join(f"{status}:{count}" for status, count in counter.most_common(4))
        for school_id, counter in counters.items()
    }


def school_host(school: dict[str, str], best_url: str = "") -> str:
    for url in [clean(school.get("website")), clean(school.get("admissions_source_url")), best_url]:
        host = normalized_host(url)
        if host:
            return host
    return ""


def site_query_host(host: str) -> str:
    if not host:
        return ""
    parsed = urlparse(f"https://{host}")
    host = parsed.netloc or host
    parts = host.split(".")
    if len(parts) > 2 and parts[0] in {"www", "med", "medicine", "medschool", "som", "school"}:
        return ".".join(parts[1:])
    return host


def quote(value: str) -> str:
    return f'"{value}"'


def query_set(school: dict[str, str], best_url: str = "") -> dict[str, str]:
    name = clean(school.get("school_name"))
    host = site_query_host(school_host(school, best_url))
    site_prefix = f"site:{host} " if host else ""
    return {
        "google_query_site_specific": f'{site_prefix}{quote(name)} "MCAT" "GPA"',
        "google_query_class_profile": f'{quote(name)} "class profile" "MCAT" "GPA" official',
        "google_query_entering_class": f'{quote(name)} "entering class" "MCAT" "GPA" official',
        "google_query_statistics": f'{quote(name)} "admissions statistics" "MCAT" "GPA" official',
        "google_query_fact_sheet": f'{quote(name)} "fact sheet" "MCAT" "GPA" official',
        "google_query_annual_report": f'{quote(name)} "annual report" "MCAT" "GPA" official',
    }


def hunt_bucket(coverage_status: str) -> str:
    if coverage_status in {"md_official_candidate_pending_extraction", "official_candidate_ready"}:
        return "parser_or_extraction_pending"
    if coverage_status in {"md_official_domain_seed_only", "official_domain_seed_only"}:
        return "official_domain_path_needed"
    if coverage_status == "missing_candidate":
        return "official_url_search_needed"
    return "candidate_needs_review"


def build_source_hunt_queue() -> list[dict[str, str]]:
    schools = active_md_school_index()
    accepted = accepted_school_ids()
    candidate_summary = candidate_summary_by_school()
    review_summary = review_summary_by_school()
    rows = []
    for coverage in read_csv(MD_OFFICIAL_COVERAGE_CSV):
        school_id = clean(coverage.get("school_id"))
        if not school_id or school_id in accepted:
            continue
        school = schools.get(school_id, {})
        summary = candidate_summary.get(school_id, {})
        best_url = clean(summary.get("best_existing_candidate_url"))
        bucket = hunt_bucket(clean(coverage.get("coverage_status")))
        row = {
            "priority_rank": "0",
            "hunt_bucket": bucket,
            "school_id": school_id,
            "school_name": clean(coverage.get("school_name")),
            "state_abbrev": clean(school.get("state_abbrev")),
            "city": clean(school.get("city")),
            "coverage_status": clean(coverage.get("coverage_status")),
            "candidate_count": clean(coverage.get("candidate_count")),
            "official_candidate_count": clean(coverage.get("official_candidate_count")),
            "fetched_candidate_count": clean(coverage.get("fetched_candidate_count")),
            "current_canonical_has_mcat": clean(coverage.get("current_canonical_has_mcat")),
            "current_canonical_has_gpa": clean(coverage.get("current_canonical_has_gpa")),
            "best_existing_candidate_url": best_url,
            "best_existing_candidate_status": clean(summary.get("best_existing_candidate_status")),
            "review_status_summary": review_summary.get(school_id, ""),
            "next_action": clean(coverage.get("next_action")),
            "official_source_policy": "Use official school/university public sources only; use search snippets only to discover URLs; third-party fallback only after official-source exhaustion.",
        }
        row.update(query_set({**school, "school_name": row["school_name"]}, best_url))
        rows.append(row)

    rows.sort(
        key=lambda row: (
            BUCKET_ORDER.get(row["hunt_bucket"], 99),
            row["current_canonical_has_mcat"] == "yes" and row["current_canonical_has_gpa"] == "yes",
            row["state_abbrev"] not in {"FL", "GA", "NC", "SC", "AL", "TN"},
            row["school_name"],
        )
    )
    for index, row in enumerate(rows, start=1):
        row["priority_rank"] = str(index)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a prioritized MD official-source hunt queue.")
    parser.parse_args()
    rows = build_source_hunt_queue()
    write_csv(MD_OFFICIAL_SOURCE_HUNT_QUEUE_CSV, SOURCE_HUNT_QUEUE_COLUMNS, rows)
    print(f"Wrote {MD_OFFICIAL_SOURCE_HUNT_QUEUE_CSV.relative_to(ROOT)} with {len(rows)} school(s)")


if __name__ == "__main__":
    main()
