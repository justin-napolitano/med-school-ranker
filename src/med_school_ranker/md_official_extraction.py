from __future__ import annotations

import argparse

from med_school_ranker.md_official_rules import (
    MD_DATA_CONFIDENCE,
    MD_OFFICIAL_EXTRACTED_STATS_COLUMNS,
    MD_OFFICIAL_REVIEW_QUEUE_COLUMNS,
    MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    clean,
    is_fetch_ready_source_type,
    read_csv,
    today_iso,
    write_csv,
)
from med_school_ranker.official_stats_extraction import extract_stats_from_text, fetch_candidate_text
from med_school_ranker.paths import (
    MD_OFFICIAL_EXTRACTED_STATS_CSV,
    MD_OFFICIAL_REVIEW_QUEUE_CSV,
    MD_OFFICIAL_SOURCE_CANDIDATES_CSV,
    ROOT,
)


def skipped_row(candidate: dict[str, str], status: str, notes: str) -> dict[str, str]:
    return {
        "school_id": clean(candidate.get("school_id")),
        "school_name": clean(candidate.get("school_name")),
        "degree_type": clean(candidate.get("degree_type") or "MD"),
        "candidate_source_url": clean(candidate.get("candidate_source_url")),
        "candidate_source_title": clean(candidate.get("candidate_source_title")),
        "candidate_source_type": clean(candidate.get("candidate_source_type")),
        "source_host": clean(candidate.get("source_host")),
        "official_domain_status": clean(candidate.get("official_domain_status")),
        "official_domain_score": clean(candidate.get("official_domain_score")),
        "fetch_status": status,
        "extraction_status": status,
        "stats_cohort_year": "",
        "metric_population": "",
        "metric_type": "",
        "mcat_value": "",
        "mcat_metric": "",
        "gpa_value": "",
        "gpa_metric": "",
        "science_gpa_value": "",
        "evidence_text": "",
        "source_publication_date": "",
        "source_last_checked": today_iso(),
        "data_confidence": "",
        "review_status": "needs_review",
        "notes": notes,
    }


def md_extracted_row(candidate: dict[str, str], text: str, title: str) -> dict[str, str]:
    extracted = extract_stats_from_text(candidate, candidate, text, title)
    status = clean(extracted.get("extraction_status"))
    degree = clean(candidate.get("degree_type")).upper()
    if status == "accepted" and degree != "MD":
        extracted["extraction_status"] = "rejected_non_md_candidate"
        extracted["review_status"] = "needs_review"
        extracted["notes"] = "MD official stats importer only applies accepted rows to MD schools."
    extracted.update(
        {
            "degree_type": clean(candidate.get("degree_type") or "MD"),
            "source_host": clean(candidate.get("source_host")),
            "official_domain_status": clean(candidate.get("official_domain_status")),
            "official_domain_score": clean(candidate.get("official_domain_score")),
            "source_last_checked": today_iso(),
            "data_confidence": MD_DATA_CONFIDENCE if clean(extracted.get("extraction_status")) == "accepted" else "",
        }
    )
    return extracted


def review_row(extracted: dict[str, str]) -> dict[str, str]:
    status = clean(extracted.get("extraction_status"))
    if status == "fetch_skipped_network_disabled":
        reason = "network_disabled"
        recommended = "Rerun med-school-extract-md-official-stats --fetch when network access is available."
    elif status == "fetch_skipped_needs_stats_path":
        reason = "needs_stats_path"
        recommended = "Find a class profile, annual report, fact book, or admissions statistics URL on this official domain."
    elif status == "fetch_skipped_needs_review":
        reason = "candidate_needs_review"
        recommended = "Review official-domain match before fetching."
    elif status == "unsupported_pdf_without_parser":
        reason = "pdf_not_parsed"
        recommended = "Extract manually or add a PDF parser in a later slice."
    elif status == "rejected_minimum_requirement":
        reason = "minimum_requirement_context"
        recommended = "Do not apply unless a reviewer verifies these are class profile values."
    elif status == "needs_review_partial_stats":
        reason = "partial_stats"
        recommended = "Review source manually; accepted rows require both MCAT and GPA."
    elif status == "no_relevant_stats_found":
        reason = "stats_not_found"
        recommended = "Review source manually or keep as official source missing."
    else:
        reason = status or "needs_review"
        recommended = "Review source manually."
    return {
        "school_id": clean(extracted.get("school_id")),
        "school_name": clean(extracted.get("school_name")),
        "degree_type": clean(extracted.get("degree_type") or "MD"),
        "candidate_source_url": clean(extracted.get("candidate_source_url")),
        "candidate_source_title": clean(extracted.get("candidate_source_title")),
        "candidate_source_type": clean(extracted.get("candidate_source_type")),
        "source_host": clean(extracted.get("source_host")),
        "official_domain_status": clean(extracted.get("official_domain_status")),
        "official_domain_score": clean(extracted.get("official_domain_score")),
        "fetch_status": clean(extracted.get("fetch_status")),
        "extraction_status": status,
        "review_status": clean(extracted.get("review_status")),
        "review_reason": reason,
        "evidence_text": clean(extracted.get("evidence_text")),
        "recommended_action": recommended,
        "last_checked": today_iso(),
        "notes": clean(extracted.get("notes")),
    }


def build_md_official_extraction(fetch: bool = False, timeout_seconds: int = 15, school_id: str = "") -> list[dict[str, str]]:
    candidates = read_csv(MD_OFFICIAL_SOURCE_CANDIDATES_CSV)
    if school_id:
        candidates = [row for row in candidates if clean(row.get("school_id")) == school_id]

    extracted_rows: list[dict[str, str]] = []
    updated_candidates: list[dict[str, str]] = []
    for candidate in candidates:
        candidate = dict(candidate)
        review_status = clean(candidate.get("review_status"))
        source_type = clean(candidate.get("candidate_source_type"))
        if clean(candidate.get("degree_type")).upper() != "MD":
            candidate["fetch_status"] = "fetch_skipped_non_md_candidate"
            extracted_rows.append(skipped_row(candidate, "fetch_skipped_non_md_candidate", "MD official importer only fetches MD rows."))
            updated_candidates.append(candidate)
            continue
        if review_status != "accepted_for_fetch" or not is_fetch_ready_source_type(source_type):
            if review_status == "official_domain_seed_needs_stats_path":
                skip_status = "fetch_skipped_needs_stats_path"
                notes = "Official domain seed needs a class profile, annual report, fact book, or admissions statistics path before fetching."
            else:
                skip_status = "fetch_skipped_needs_review"
                notes = "Candidate did not pass the MD official auto-fetch threshold."
            candidate["fetch_status"] = skip_status
            extracted_rows.append(skipped_row(candidate, skip_status, notes))
            updated_candidates.append(candidate)
            continue
        if not fetch:
            candidate["fetch_status"] = "fetch_skipped_network_disabled"
            extracted_rows.append(skipped_row(candidate, "fetch_skipped_network_disabled", "Network fetch disabled for deterministic headless run."))
            updated_candidates.append(candidate)
            continue

        fetch_status, title, text, fetch_notes = fetch_candidate_text(clean(candidate.get("candidate_source_url")), timeout_seconds)
        candidate["fetch_status"] = fetch_status
        candidate["source_last_checked"] = today_iso()
        if title and not clean(candidate.get("candidate_source_title")):
            candidate["candidate_source_title"] = title
        if fetch_status != "fetched":
            extracted_rows.append(skipped_row(candidate, fetch_status, fetch_notes))
            updated_candidates.append(candidate)
            continue
        extracted = md_extracted_row(candidate, text, title or clean(candidate.get("candidate_source_title")))
        extracted["fetch_status"] = fetch_status
        extracted_rows.append(extracted)
        updated_candidates.append(candidate)

    write_csv(MD_OFFICIAL_SOURCE_CANDIDATES_CSV, MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS, updated_candidates)
    write_csv(MD_OFFICIAL_EXTRACTED_STATS_CSV, MD_OFFICIAL_EXTRACTED_STATS_COLUMNS, extracted_rows)
    write_csv(
        MD_OFFICIAL_REVIEW_QUEUE_CSV,
        MD_OFFICIAL_REVIEW_QUEUE_COLUMNS,
        [review_row(row) for row in extracted_rows if clean(row.get("extraction_status")) != "accepted"],
    )
    return extracted_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract MD official public MCAT/GPA values from approved candidate URLs.")
    parser.add_argument("--fetch", action="store_true", help="Fetch approved official URLs over the network. Defaults to deterministic no-network mode.")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--school-id", default="")
    args = parser.parse_args()
    rows = build_md_official_extraction(fetch=args.fetch, timeout_seconds=args.timeout_seconds, school_id=args.school_id)
    accepted = sum(1 for row in rows if clean(row.get("extraction_status")) == "accepted")
    print(f"Wrote {MD_OFFICIAL_EXTRACTED_STATS_CSV.relative_to(ROOT)} with {accepted} accepted MD official extraction(s)")


if __name__ == "__main__":
    main()
