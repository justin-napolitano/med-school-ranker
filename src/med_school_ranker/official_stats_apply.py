from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from med_school_ranker.official_source_rules import (
    OFFICIAL_STATS_CONFLICT_COLUMNS,
    OFFICIAL_STATS_COVERAGE_COLUMNS,
    clean,
    format_float,
    is_truthy,
    read_csv,
    today_iso,
    write_csv,
)
from med_school_ranker.paths import (
    ADMISSIONS_STATS_CSV,
    MASTER_CSV,
    OFFICIAL_STATS_CONFLICTS_CSV,
    OFFICIAL_STATS_COVERAGE_CSV,
    OFFICIAL_STATS_EXTRACTED_VALUES_CSV,
    OFFICIAL_STATS_SOURCE_CANDIDATES_CSV,
    ROOT,
)
from med_school_ranker.source_integration import (
    acceptance_rate_band,
    aamc_acceptance_rate_for,
    fmt_optional_float,
    gpa_band,
    mcat_band,
)
from med_school_ranker.validation import ADMISSIONS_STATS_COLUMNS


def parse_float(value: object) -> float | None:
    text = clean(value).replace("$", "").replace(",", "").replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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


def current_stats_by_school(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    stats = {}
    for row in rows:
        school_id = clean(row.get("school_id"))
        if school_id and school_id not in stats:
            stats[school_id] = row
    return stats


def accepted_extractions() -> list[dict[str, str]]:
    rows = [
        row
        for row in read_csv(OFFICIAL_STATS_EXTRACTED_VALUES_CSV)
        if clean(row.get("extraction_status")) == "accepted"
        and clean(row.get("review_status")) == "approved_official_extraction"
        and parse_float(row.get("mcat_value")) is not None
        and parse_float(row.get("gpa_value")) is not None
    ]
    return sorted(
        rows,
        key=lambda row: (
            clean(row.get("school_name")),
            -1 * (parse_float(row.get("official_domain_score")) or 0),
            clean(row.get("candidate_source_url")),
        ),
    )


def best_accepted_by_school(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    best = {}
    for row in rows:
        school_id = clean(row.get("school_id"))
        if school_id and school_id not in best:
            best[school_id] = row
    return best


def official_stats_row(extracted: dict[str, str], school: dict[str, str]) -> dict[str, str]:
    mcat_value = parse_float(extracted.get("mcat_value"))
    gpa_value = parse_float(extracted.get("gpa_value"))
    rate = aamc_acceptance_rate_for(gpa_value, mcat_value)
    metric_type = clean(extracted.get("metric_type")) or "official_published_value"
    is_median = "median" in metric_type
    row = {column: "" for column in ADMISSIONS_STATS_COLUMNS}
    row.update(
        {
            "school_id": clean(extracted.get("school_id")),
            "school_name": clean(extracted.get("school_name") or school.get("school_name")),
            "degree_type": clean(extracted.get("degree_type") or school.get("degree_type")),
            "stats_cohort_year": clean(extracted.get("stats_cohort_year")),
            "metric_population": clean(extracted.get("metric_population")) or "official published school profile",
            "metric_type": metric_type,
            "published_source_count": "1",
            "published_mcat_average": format_float(mcat_value, 1),
            "published_gpa_average": format_float(gpa_value, 2),
            "published_mcat_spread": "0",
            "published_gpa_spread": "0",
            "published_mcat_band": mcat_band(mcat_value),
            "published_gpa_band": gpa_band(gpa_value),
            "aamc_acceptance_rate": fmt_optional_float(rate, 1),
            "aamc_acceptance_rate_band": acceptance_rate_band(rate),
            "data_quality_rank": "1",
            "data_quality_band": "high",
            "source_name": "Official school source",
            "source_url": clean(extracted.get("candidate_source_url")),
            "source_snapshot_path": "",
            "source_publication_date": clean(extracted.get("source_publication_date")),
            "source_last_checked": clean(extracted.get("source_last_checked")) or today_iso(),
            "data_confidence": "official_public_source_extracted",
            "notes": "Official public school source extraction. Candidate evidence retained in data/source_tables/official_mcat_gpa_extracted_values.csv.",
        }
    )
    if is_median:
        row["mcat_median_matriculated"] = format_float(mcat_value, 1)
        row["overall_gpa_median_matriculated"] = format_float(gpa_value, 2)
    else:
        row["mcat_mean_enrolled"] = format_float(mcat_value, 1)
        row["overall_gpa_mean_enrolled"] = format_float(gpa_value, 2)
    return row


def delta(left: object, right: object, digits: int) -> str:
    left_number = parse_float(left)
    right_number = parse_float(right)
    if left_number is None or right_number is None:
        return ""
    return format_float(right_number - left_number, digits)


def conflict_rows(
    current_by_school: dict[str, dict[str, str]],
    accepted_by_school: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows = []
    for school_id, official in accepted_by_school.items():
        current = current_by_school.get(school_id, {})
        current_mcat = clean(current.get("published_mcat_average") or current.get("mcat_mean_enrolled") or current.get("mcat_median_matriculated"))
        current_gpa = clean(current.get("published_gpa_average") or current.get("overall_gpa_mean_enrolled") or current.get("overall_gpa_median_matriculated"))
        official_mcat = clean(official.get("mcat_value"))
        official_gpa = clean(official.get("gpa_value"))
        mcat_delta = delta(current_mcat, official_mcat, 1)
        gpa_delta = delta(current_gpa, official_gpa, 2)
        mcat_abs = abs(parse_float(mcat_delta) or 0)
        gpa_abs = abs(parse_float(gpa_delta) or 0)
        if not current_mcat or not current_gpa:
            status = "no_current_pair"
        elif mcat_abs > 2 or gpa_abs > 0.10:
            status = "large_delta_review"
        else:
            status = "aligned_or_small_delta"
        rows.append(
            {
                "school_id": school_id,
                "school_name": clean(official.get("school_name")),
                "degree_type": clean(official.get("degree_type")),
                "current_mcat": current_mcat,
                "current_gpa": current_gpa,
                "official_mcat": official_mcat,
                "official_gpa": official_gpa,
                "mcat_delta": mcat_delta,
                "gpa_delta": gpa_delta,
                "current_source_name": clean(current.get("source_name")),
                "current_source_url": clean(current.get("source_url")),
                "official_source_url": clean(official.get("candidate_source_url")),
                "conflict_status": status,
                "notes": "Official accepted extraction compared to current canonical admissions_stats row.",
            }
        )
    return rows


def coverage_rows(
    schools: list[dict[str, str]],
    candidates: list[dict[str, str]],
    extracted: list[dict[str, str]],
    stats_by_school: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    candidate_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in candidates:
        school_id = clean(row.get("school_id"))
        candidate_counts[school_id]["candidate"] += 1
        if clean(row.get("review_status")) == "accepted_for_fetch":
            candidate_counts[school_id]["official_candidate"] += 1
        if clean(row.get("source_status")) == "domain_seed":
            candidate_counts[school_id]["domain_seed"] += 1
        if clean(row.get("fetch_status")) not in {"", "not_fetched"}:
            candidate_counts[school_id]["fetched"] += 1
    accepted_counts = Counter(clean(row.get("school_id")) for row in extracted if clean(row.get("extraction_status")) == "accepted")
    rows = []
    for school in schools:
        school_id = clean(school.get("school_id"))
        stats = stats_by_school.get(school_id, {})
        has_mcat = bool(clean(stats.get("published_mcat_average")) or clean(stats.get("mcat_mean_enrolled")) or clean(stats.get("mcat_median_matriculated")))
        has_gpa = bool(clean(stats.get("published_gpa_average")) or clean(stats.get("overall_gpa_mean_enrolled")) or clean(stats.get("overall_gpa_median_matriculated")))
        accepted = accepted_counts[school_id]
        if accepted:
            status = "official_stats_applied"
            next_action = "Review official conflict report for large deltas."
        elif candidate_counts[school_id]["official_candidate"]:
            status = "official_candidate_pending_extraction"
            next_action = "Run med-school-extract-official-stats --fetch."
        elif candidate_counts[school_id]["domain_seed"]:
            status = "official_domain_seed_only"
            next_action = "Find a stats/profile/report path on the official domain."
        elif candidate_counts[school_id]["candidate"]:
            status = "candidate_needs_review"
            next_action = "Approve or reject the candidate source URL."
        else:
            status = "missing_candidate"
            next_action = "Find an official class profile, annual report, fact book, or admissions statistics page."
        rows.append(
            {
                "school_id": school_id,
                "school_name": clean(school.get("school_name")),
                "degree_type": clean(school.get("degree_type")),
                "candidate_count": str(candidate_counts[school_id]["candidate"]),
                "official_candidate_count": str(candidate_counts[school_id]["official_candidate"]),
                "fetched_candidate_count": str(candidate_counts[school_id]["fetched"]),
                "accepted_extraction_count": str(accepted),
                "current_canonical_has_mcat": "yes" if has_mcat else "no",
                "current_canonical_has_gpa": "yes" if has_gpa else "no",
                "coverage_status": status,
                "next_action": next_action,
            }
        )
    return rows


def apply_official_stats() -> int:
    current_rows = read_csv(ADMISSIONS_STATS_CSV)
    schools = active_school_rows()
    schools_by_id = {clean(row.get("school_id")): row for row in schools}
    accepted = accepted_extractions()
    accepted_by_school = best_accepted_by_school(accepted)
    current_by_school = current_stats_by_school(current_rows)

    official_rows = [
        official_stats_row(extracted, schools_by_id.get(school_id, {}))
        for school_id, extracted in accepted_by_school.items()
    ]
    replaced_ids = set(accepted_by_school)
    merged_rows = official_rows + [row for row in current_rows if clean(row.get("school_id")) not in replaced_ids]
    write_csv(ADMISSIONS_STATS_CSV, ADMISSIONS_STATS_COLUMNS, merged_rows)
    write_csv(OFFICIAL_STATS_CONFLICTS_CSV, OFFICIAL_STATS_CONFLICT_COLUMNS, conflict_rows(current_by_school, accepted_by_school))
    write_csv(
        OFFICIAL_STATS_COVERAGE_CSV,
        OFFICIAL_STATS_COVERAGE_COLUMNS,
        coverage_rows(
            schools,
            read_csv(OFFICIAL_STATS_SOURCE_CANDIDATES_CSV),
            read_csv(OFFICIAL_STATS_EXTRACTED_VALUES_CSV),
            current_stats_by_school(merged_rows),
        ),
    )
    return len(official_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply accepted official MCAT/GPA extractions to canonical admissions_stats.csv.")
    parser.parse_args()
    count = apply_official_stats()
    print(f"Applied {count} official MCAT/GPA row(s) to {ADMISSIONS_STATS_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
