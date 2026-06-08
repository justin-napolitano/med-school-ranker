from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from med_school_ranker.aacom_do_rules import (
    AACOM_CONFLICT_COLUMNS,
    AACOM_COVERAGE_COLUMNS,
    AACOM_DATA_CONFIDENCE,
    AACOM_SOURCE_NAME,
    clean,
    format_float,
    is_aacom_profile_url,
    is_truthy,
    read_csv,
    today_iso,
    write_csv,
)
from med_school_ranker.paths import (
    AACOM_DO_EXTRACTED_STATS_CSV,
    AACOM_DO_PROFILE_CANDIDATES_CSV,
    AACOM_DO_PROFILE_CONFLICTS_CSV,
    AACOM_DO_PROFILE_COVERAGE_CSV,
    ADMISSIONS_STATS_CSV,
    MASTER_CSV,
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


def active_do_school_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(MASTER_CSV):
        if clean(row.get("degree_type")).upper() != "DO":
            continue
        if row.get("active_in_universe") and not is_truthy(row.get("active_in_universe")):
            continue
        if is_truthy(row.get("manual_exclusion_flag")):
            continue
        rows.append(row)
    return rows


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
        for row in read_csv(AACOM_DO_EXTRACTED_STATS_CSV)
        if clean(row.get("extraction_status")) == "accepted"
        and clean(row.get("review_status")) == "approved_aacom_extraction"
        and clean(row.get("data_confidence")) == AACOM_DATA_CONFIDENCE
        and clean(row.get("degree_type")).upper() == "DO"
        and is_aacom_profile_url(clean(row.get("aacom_profile_url")))
        and parse_float(row.get("mcat_mean")) is not None
        and parse_float(row.get("overall_gpa_mean")) is not None
    ]
    return sorted(rows, key=lambda row: (clean(row.get("school_name")), clean(row.get("aacom_profile_url"))))


def best_accepted_by_school(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    best = {}
    for row in rows:
        school_id = clean(row.get("school_id"))
        if school_id and school_id not in best:
            best[school_id] = row
    return best


def aacom_stats_row(extracted: dict[str, str], school: dict[str, str]) -> dict[str, str]:
    mcat_value = parse_float(extracted.get("mcat_mean"))
    gpa_value = parse_float(extracted.get("overall_gpa_mean"))
    rate = aamc_acceptance_rate_for(gpa_value, mcat_value)
    row = {column: "" for column in ADMISSIONS_STATS_COLUMNS}
    row.update(
        {
            "school_id": clean(extracted.get("school_id")),
            "school_name": clean(extracted.get("school_name") or school.get("school_name")),
            "degree_type": "DO",
            "stats_cohort_year": clean(extracted.get("stats_academic_year")),
            "metric_population": clean(extracted.get("metric_population")) or "AACOM COM-submitted profile",
            "metric_type": clean(extracted.get("metric_type")) or "aacom_reported_mean",
            "mcat_mean_enrolled": format_float(mcat_value, 1),
            "overall_gpa_mean_enrolled": format_float(gpa_value, 2),
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
            "source_name": AACOM_SOURCE_NAME,
            "source_url": clean(extracted.get("aacom_profile_url")),
            "source_snapshot_path": "",
            "source_publication_date": "",
            "source_last_checked": clean(extracted.get("source_last_checked")) or today_iso(),
            "data_confidence": AACOM_DATA_CONFIDENCE,
            "notes": "AACOM Choose D.O. Explorer COM-submitted profile extraction. Candidate evidence retained in data/source_tables/aacom_do_extracted_stats.csv.",
        }
    )
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
    for school_id, aacom in accepted_by_school.items():
        current = current_by_school.get(school_id, {})
        current_mcat = clean(current.get("published_mcat_average") or current.get("mcat_mean_enrolled") or current.get("mcat_median_matriculated"))
        current_gpa = clean(current.get("published_gpa_average") or current.get("overall_gpa_mean_enrolled") or current.get("overall_gpa_median_matriculated"))
        aacom_mcat = clean(aacom.get("mcat_mean"))
        aacom_gpa = clean(aacom.get("overall_gpa_mean"))
        mcat_delta = delta(current_mcat, aacom_mcat, 1)
        gpa_delta = delta(current_gpa, aacom_gpa, 2)
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
                "school_name": clean(aacom.get("school_name")),
                "degree_type": "DO",
                "current_mcat": current_mcat,
                "current_gpa": current_gpa,
                "aacom_mcat": aacom_mcat,
                "aacom_gpa": aacom_gpa,
                "mcat_delta": mcat_delta,
                "gpa_delta": gpa_delta,
                "current_source_name": clean(current.get("source_name")),
                "current_source_url": clean(current.get("source_url")),
                "aacom_source_url": clean(aacom.get("aacom_profile_url")),
                "conflict_status": status,
                "notes": "Accepted AACOM profile extraction compared to current non-AACOM canonical admissions_stats row.",
            }
        )
    return rows


def coverage_rows(
    schools: list[dict[str, str]],
    candidates: list[dict[str, str]],
    extracted: list[dict[str, str]],
    stats_by_school: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in candidates:
        school_id = clean(row.get("school_id"))
        if not school_id:
            continue
        counts[school_id]["candidate"] += 1
        if clean(row.get("match_status")) == "safe_match":
            counts[school_id]["matched"] += 1
        if clean(row.get("fetch_status")) not in {"", "not_fetched", "not_applicable"}:
            counts[school_id]["fetched"] += 1
    accepted_counts = Counter(
        clean(row.get("school_id"))
        for row in extracted
        if clean(row.get("extraction_status")) == "accepted" and clean(row.get("review_status")) == "approved_aacom_extraction"
    )
    rows = []
    for school in schools:
        school_id = clean(school.get("school_id"))
        stats = stats_by_school.get(school_id, {})
        has_mcat = bool(clean(stats.get("published_mcat_average")) or clean(stats.get("mcat_mean_enrolled")) or clean(stats.get("mcat_median_matriculated")))
        has_gpa = bool(clean(stats.get("published_gpa_average")) or clean(stats.get("overall_gpa_mean_enrolled")) or clean(stats.get("overall_gpa_median_matriculated")))
        accepted = accepted_counts[school_id]
        if accepted:
            status = "aacom_stats_applied"
            next_action = "Review AACOM conflict report for large deltas."
        elif counts[school_id]["matched"]:
            status = "aacom_profile_pending_extraction"
            next_action = "Run med-school-extract-aacom-do-stats --fetch."
        elif counts[school_id]["candidate"]:
            status = "aacom_profile_needs_review"
            next_action = "Review AACOM profile match before fetching."
        else:
            status = "missing_aacom_profile_candidate"
            next_action = "Run AACOM discovery with --fetch or provide a URL list."
        rows.append(
            {
                "school_id": school_id,
                "school_name": clean(school.get("school_name")),
                "degree_type": "DO",
                "candidate_count": str(counts[school_id]["candidate"]),
                "matched_candidate_count": str(counts[school_id]["matched"]),
                "fetched_candidate_count": str(counts[school_id]["fetched"]),
                "accepted_extraction_count": str(accepted),
                "current_canonical_has_mcat": "yes" if has_mcat else "no",
                "current_canonical_has_gpa": "yes" if has_gpa else "no",
                "coverage_status": status,
                "next_action": next_action,
            }
        )
    return rows


def apply_aacom_do_stats() -> int:
    current_rows = read_csv(ADMISSIONS_STATS_CSV)
    non_aacom_current = [row for row in current_rows if clean(row.get("data_confidence")) != AACOM_DATA_CONFIDENCE]
    schools = active_do_school_rows()
    schools_by_id = {clean(row.get("school_id")): row for row in schools}
    accepted = accepted_extractions()
    accepted_by_school = best_accepted_by_school(accepted)
    current_by_school = current_stats_by_school(non_aacom_current)

    aacom_rows = [
        aacom_stats_row(extracted, schools_by_id.get(school_id, {}))
        for school_id, extracted in accepted_by_school.items()
        if school_id in schools_by_id
    ]
    merged_rows = aacom_rows + non_aacom_current
    write_csv(ADMISSIONS_STATS_CSV, ADMISSIONS_STATS_COLUMNS, merged_rows)
    write_csv(AACOM_DO_PROFILE_CONFLICTS_CSV, AACOM_CONFLICT_COLUMNS, conflict_rows(current_by_school, accepted_by_school))
    write_csv(
        AACOM_DO_PROFILE_COVERAGE_CSV,
        AACOM_COVERAGE_COLUMNS,
        coverage_rows(
            schools,
            read_csv(AACOM_DO_PROFILE_CANDIDATES_CSV),
            read_csv(AACOM_DO_EXTRACTED_STATS_CSV),
            current_stats_by_school(merged_rows),
        ),
    )
    return len(aacom_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply accepted AACOM DO MCAT/GPA extractions to canonical admissions_stats.csv.")
    parser.parse_args()
    count = apply_aacom_do_stats()
    print(f"Applied {count} AACOM DO MCAT/GPA row(s) to {ADMISSIONS_STATS_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
