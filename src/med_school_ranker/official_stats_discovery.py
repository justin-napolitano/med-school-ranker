from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from med_school_ranker.official_source_rules import (
    OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    OFFICIAL_STATS_COVERAGE_COLUMNS,
    OFFICIAL_STATS_DISCOVERY_REPORT_COLUMNS,
    classify_official_source,
    clean,
    is_truthy,
    read_csv,
    source_type_hint,
    today_iso,
    write_csv,
)
from med_school_ranker.paths import (
    ADMISSIONS_SOURCE_QUEUE_CSV,
    ADMISSIONS_STATS_CSV,
    MASTER_CSV,
    OFFICIAL_STATS_COVERAGE_CSV,
    OFFICIAL_STATS_DISCOVERY_REPORT_CSV,
    OFFICIAL_STATS_SOURCE_CANDIDATES_CSV,
    ROOT,
)


def active_school_rows() -> list[dict[str, str]]:
    schools = []
    for row in read_csv(MASTER_CSV):
        if not clean(row.get("school_id")):
            continue
        if row.get("active_in_universe") and not is_truthy(row.get("active_in_universe")):
            continue
        if is_truthy(row.get("manual_exclusion_flag")):
            continue
        schools.append(row)
    return schools


def search_query_for_school(school: dict[str, str]) -> str:
    name = clean(school.get("school_name"))
    campus = clean(school.get("campus_name"))
    name_part = campus if campus and campus.lower() not in name.lower() else name
    return f'"{name_part}" entering class profile MCAT GPA matriculants'


def candidate_row(
    school: dict[str, str],
    candidate_url: str,
    discovery_method: str,
    candidate_title: str = "",
    notes: str = "",
) -> dict[str, str]:
    classification = classify_official_source(school, candidate_url, candidate_title)
    candidate_type = source_type_hint(candidate_url, candidate_title)
    likely_stats_source = (
        discovery_method in {"school_master_admissions_source_url", "manual_admissions_source_queue"}
        or candidate_type in {"class_profile", "annual_report", "admissions_statistics", "pdf_report"}
    )
    if classification.accepted_for_auto_extraction and likely_stats_source:
        review_status = "accepted_for_fetch"
        source_status = "candidate"
        fetch_status = "not_fetched"
    elif classification.accepted_for_auto_extraction:
        review_status = "official_domain_seed_needs_stats_path"
        source_status = "domain_seed"
        fetch_status = "not_applicable"
    else:
        review_status = "needs_review"
        source_status = "candidate"
        fetch_status = "not_fetched"
    return {
        "school_id": clean(school.get("school_id")),
        "school_name": clean(school.get("school_name")),
        "degree_type": clean(school.get("degree_type")),
        "state_abbrev": clean(school.get("state_abbrev")),
        "school_website": clean(school.get("website")),
        "candidate_source_url": clean(candidate_url),
        "candidate_source_title": clean(candidate_title),
        "candidate_source_type": candidate_type,
        "source_status": source_status,
        "official_domain_status": classification.status,
        "official_domain_score": f"{classification.score:.2f}",
        "official_match_reason": classification.reason,
        "discovery_method": discovery_method,
        "search_query": search_query_for_school(school),
        "discovered_at": today_iso(),
        "last_checked": today_iso(),
        "fetch_status": fetch_status,
        "review_status": review_status,
        "notes": notes,
    }


def candidate_rows_from_school_master(schools: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for school in schools:
        for field, method, title in [
            ("admissions_source_url", "school_master_admissions_source_url", "Admissions source URL from school_master"),
            ("website", "school_master_website", "School website from school_master"),
        ]:
            url = clean(school.get(field))
            if not url:
                continue
            key = (clean(school.get("school_id")), url)
            if key in seen:
                continue
            seen.add(key)
            rows.append(candidate_row(school, url, method, title))
    return rows


def candidate_rows_from_manual_queue(schools_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for queue_row in read_csv(ADMISSIONS_SOURCE_QUEUE_CSV):
        school_id = clean(queue_row.get("school_id"))
        url = clean(queue_row.get("candidate_source_url"))
        school = schools_by_id.get(school_id)
        if not school or not url:
            continue
        key = (school_id, url)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            candidate_row(
                school,
                url,
                "manual_admissions_source_queue",
                clean(queue_row.get("candidate_source_title") or queue_row.get("source_title")),
                clean(queue_row.get("notes")),
            )
        )
    return rows


def merge_candidates(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (clean(row.get("school_id")), clean(row.get("candidate_source_url")))
        if not key[0] or not key[1]:
            continue
        existing = merged.get(key)
        if not existing:
            merged[key] = row
            continue
        methods = sorted({clean(existing.get("discovery_method")), clean(row.get("discovery_method"))} - {""})
        existing["discovery_method"] = "; ".join(methods)
        if not clean(existing.get("candidate_source_title")):
            existing["candidate_source_title"] = clean(row.get("candidate_source_title"))
        row_score = float(clean(row.get("official_domain_score")) or 0)
        existing_score = float(clean(existing.get("official_domain_score")) or 0)
        if row_score > existing_score:
            existing.update(row)
    return sorted(merged.values(), key=lambda item: (item["school_name"], item["candidate_source_url"]))


def current_stats_by_school() -> dict[str, dict[str, str]]:
    stats = {}
    for row in read_csv(ADMISSIONS_STATS_CSV):
        school_id = clean(row.get("school_id"))
        if school_id and school_id not in stats:
            stats[school_id] = row
    return stats


def build_coverage_rows(
    schools: list[dict[str, str]],
    candidates: list[dict[str, str]],
) -> list[dict[str, str]]:
    stats = current_stats_by_school()
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in candidates:
        school_id = clean(row.get("school_id"))
        counts[school_id]["candidate"] += 1
        if clean(row.get("review_status")) == "accepted_for_fetch":
            counts[school_id]["official_candidate"] += 1
        if clean(row.get("source_status")) == "domain_seed":
            counts[school_id]["domain_seed"] += 1
        if clean(row.get("fetch_status")) not in {"", "not_fetched"}:
            counts[school_id]["fetched"] += 1

    rows = []
    for school in schools:
        school_id = clean(school.get("school_id"))
        stat = stats.get(school_id, {})
        candidate_count = counts[school_id]["candidate"]
        official_count = counts[school_id]["official_candidate"]
        has_mcat = bool(clean(stat.get("published_mcat_average")) or clean(stat.get("mcat_mean_enrolled")) or clean(stat.get("mcat_median_matriculated")))
        has_gpa = bool(clean(stat.get("published_gpa_average")) or clean(stat.get("overall_gpa_mean_enrolled")) or clean(stat.get("overall_gpa_median_matriculated")))
        if official_count:
            status = "official_candidate_ready"
            next_action = "Run med-school-extract-official-stats --fetch when network access is available."
        elif counts[school_id]["domain_seed"]:
            status = "official_domain_seed_only"
            next_action = "Use the search query to find a class profile, annual report, fact book, or admissions statistics path on this domain."
        elif candidate_count:
            status = "candidate_needs_review"
            next_action = "Review candidate source domain before fetching."
        else:
            status = "missing_candidate"
            next_action = "Find an official school class profile, annual report, fact book, or admissions statistics page."
        rows.append(
            {
                "school_id": school_id,
                "school_name": clean(school.get("school_name")),
                "degree_type": clean(school.get("degree_type")),
                "candidate_count": str(candidate_count),
                "official_candidate_count": str(official_count),
                "fetched_candidate_count": str(counts[school_id]["fetched"]),
                "accepted_extraction_count": "0",
                "current_canonical_has_mcat": "yes" if has_mcat else "no",
                "current_canonical_has_gpa": "yes" if has_gpa else "no",
                "coverage_status": status,
                "next_action": next_action,
            }
        )
    return rows


def build_report_rows(schools: list[dict[str, str]], candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    official_domain_count = sum(1 for row in candidates if clean(row.get("official_domain_status")).startswith("official"))
    fetch_ready_count = sum(1 for row in candidates if clean(row.get("review_status")) == "accepted_for_fetch")
    schools_with_candidate = {clean(row.get("school_id")) for row in candidates if clean(row.get("candidate_source_url"))}
    schools_with_official_domain = {clean(row.get("school_id")) for row in candidates if clean(row.get("official_domain_status")).startswith("official")}
    schools_with_fetch_ready = {clean(row.get("school_id")) for row in candidates if clean(row.get("review_status")) == "accepted_for_fetch"}
    return [
        {"metric": "active_schools", "count": str(len(schools)), "notes": "Active, non-excluded school rows scanned."},
        {"metric": "candidate_urls", "count": str(len(candidates)), "notes": "Unique candidate URLs generated from school_master and manual queue."},
        {"metric": "official_domain_urls", "count": str(official_domain_count), "notes": "Candidate URLs that pass the strict official-domain classifier."},
        {"metric": "fetch_ready_official_source_urls", "count": str(fetch_ready_count), "notes": "Official URLs that look like stats/profile/report sources and can be fetched automatically."},
        {"metric": "schools_with_any_candidate", "count": str(len(schools_with_candidate)), "notes": "Schools with at least one candidate URL."},
        {"metric": "schools_with_official_domain_seed", "count": str(len(schools_with_official_domain)), "notes": "Schools with at least one known official-domain URL."},
        {"metric": "schools_with_fetch_ready_official_source", "count": str(len(schools_with_fetch_ready)), "notes": "Schools with at least one official stats-like URL accepted for fetch."},
    ]


def build_official_source_discovery() -> list[dict[str, str]]:
    schools = active_school_rows()
    schools_by_id = {clean(row.get("school_id")): row for row in schools}
    candidates = merge_candidates(
        candidate_rows_from_school_master(schools)
        + candidate_rows_from_manual_queue(schools_by_id)
    )
    write_csv(OFFICIAL_STATS_SOURCE_CANDIDATES_CSV, OFFICIAL_SOURCE_CANDIDATE_COLUMNS, candidates)
    write_csv(OFFICIAL_STATS_DISCOVERY_REPORT_CSV, OFFICIAL_STATS_DISCOVERY_REPORT_COLUMNS, build_report_rows(schools, candidates))
    write_csv(OFFICIAL_STATS_COVERAGE_CSV, OFFICIAL_STATS_COVERAGE_COLUMNS, build_coverage_rows(schools, candidates))
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover official candidate MCAT/GPA source URLs from local seed data.")
    parser.parse_args()
    candidates = build_official_source_discovery()
    print(f"Wrote {OFFICIAL_STATS_SOURCE_CANDIDATES_CSV.relative_to(ROOT)} with {len(candidates)} candidate URL(s)")


if __name__ == "__main__":
    main()
