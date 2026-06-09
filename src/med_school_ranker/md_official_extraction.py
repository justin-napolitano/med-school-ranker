from __future__ import annotations

import argparse

from med_school_ranker.md_official_rules import (
    MD_DATA_CONFIDENCE,
    MD_OFFICIAL_EXTRACTED_STATS_COLUMNS,
    MD_OFFICIAL_REVIEW_QUEUE_COLUMNS,
    MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    clean,
    is_fetch_ready_source_type,
    is_non_md_program_context,
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
    if clean(extracted.get("extraction_status")) in {"accepted", "needs_review_partial_stats"} and is_non_md_program_context(
        clean(candidate.get("candidate_source_url")),
        title or clean(candidate.get("candidate_source_title")),
        text,
    ):
        extracted["extraction_status"] = "rejected_non_md_program_context"
        extracted["review_status"] = "needs_review"
        extracted["data_confidence"] = ""
        extracted["notes"] = "Rejected because the official source appears to describe a non-MD program."
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


def normalize_existing_extraction(candidate: dict[str, str], existing: dict[str, str]) -> dict[str, str]:
    row = dict(existing)
    if clean(row.get("extraction_status")) in {"accepted", "needs_review_partial_stats"} and is_non_md_program_context(
        clean(candidate.get("candidate_source_url")),
        clean(candidate.get("candidate_source_title") or row.get("candidate_source_title")),
        clean(row.get("evidence_text")),
    ):
        row["extraction_status"] = "rejected_non_md_program_context"
        row["review_status"] = "needs_review"
        row["data_confidence"] = ""
        row["notes"] = "Rejected because the official source appears to describe a non-MD program."
    return row


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
    elif status == "pdf_parse_failed":
        reason = "pdf_parse_failed"
        recommended = "Review source manually; PDF could not be parsed as text."
    elif status == "pdf_text_empty":
        reason = "pdf_text_empty"
        recommended = "Review source manually or add OCR; PDF appears image-based or has no extractable text."
    elif status == "image_ocr_unavailable":
        reason = "image_ocr_unavailable"
        recommended = "Install tesseract or review image manually."
    elif status == "image_ocr_failed":
        reason = "image_ocr_failed"
        recommended = "Review image manually; OCR failed."
    elif status == "image_ocr_timeout":
        reason = "image_ocr_timeout"
        recommended = "Review image manually or rerun OCR with a longer timeout."
    elif status == "image_ocr_text_empty":
        reason = "image_ocr_text_empty"
        recommended = "Review image manually; OCR produced no text."
    elif status == "rejected_minimum_requirement":
        reason = "minimum_requirement_context"
        recommended = "Do not apply unless a reviewer verifies these are class profile values."
    elif status == "rejected_non_md_program_context":
        reason = "non_md_program_context"
        recommended = "Do not apply to MD admissions stats; source appears to describe another program."
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


def parse_score(value: object) -> float:
    try:
        return float(clean(value) or 0)
    except ValueError:
        return 0.0


def should_fetch_candidate(candidate: dict[str, str], fetch_domain_seeds: bool) -> tuple[bool, str, str]:
    review_status = clean(candidate.get("review_status"))
    source_type = clean(candidate.get("candidate_source_type"))
    discovery_method = clean(candidate.get("discovery_method"))
    official_score = parse_score(candidate.get("official_domain_score"))
    if review_status == "accepted_for_fetch" and is_fetch_ready_source_type(source_type):
        return True, "", ""
    if review_status == "accepted_for_fetch" and discovery_method == "assisted_search_official_url_seed" and official_score >= 0.9:
        return True, "", "Fetched reviewed assisted-search official URL even though the path is not stats-shaped."
    if fetch_domain_seeds and review_status == "official_domain_seed_needs_stats_path" and official_score >= 0.9:
        return True, "", "Fetched official domain seed in less conservative mode."
    if review_status == "official_domain_seed_needs_stats_path":
        return (
            False,
            "fetch_skipped_needs_stats_path",
            "Official domain seed needs a class profile, annual report, fact book, or admissions statistics path before fetching.",
        )
    return False, "fetch_skipped_needs_review", "Candidate did not pass the MD official auto-fetch threshold."


def build_md_official_extraction(
    fetch: bool = False,
    timeout_seconds: int = 15,
    school_id: str = "",
    fetch_domain_seeds: bool = False,
    reuse_existing: bool = False,
    refetch_statuses: set[str] | None = None,
    refetch_url_extensions: set[str] | None = None,
    progress_every: int = 0,
) -> list[dict[str, str]]:
    refetch_statuses = refetch_statuses or set()
    refetch_url_extensions = {extension.lower() if extension.startswith(".") else f".{extension.lower()}" for extension in (refetch_url_extensions or set())}
    candidates = read_csv(MD_OFFICIAL_SOURCE_CANDIDATES_CSV)
    if school_id:
        candidates = [row for row in candidates if clean(row.get("school_id")) == school_id]
    existing_by_url = {
        clean(row.get("candidate_source_url")): row
        for row in read_csv(MD_OFFICIAL_EXTRACTED_STATS_CSV)
        if clean(row.get("candidate_source_url"))
    }

    extracted_rows: list[dict[str, str]] = []
    updated_candidates: list[dict[str, str]] = []
    for index, candidate in enumerate(candidates, start=1):
        if progress_every and (index == 1 or index % progress_every == 0 or index == len(candidates)):
            print(f"Processing MD official candidate {index}/{len(candidates)}", flush=True)
        candidate = dict(candidate)
        if clean(candidate.get("degree_type")).upper() != "MD":
            candidate["fetch_status"] = "fetch_skipped_non_md_candidate"
            extracted_rows.append(skipped_row(candidate, "fetch_skipped_non_md_candidate", "MD official importer only fetches MD rows."))
            updated_candidates.append(candidate)
            continue
        ready_to_fetch, skip_status, notes = should_fetch_candidate(candidate, fetch_domain_seeds)
        if not ready_to_fetch:
            candidate["fetch_status"] = skip_status
            extracted_rows.append(skipped_row(candidate, skip_status, notes))
            updated_candidates.append(candidate)
            continue
        if not fetch:
            candidate["fetch_status"] = "fetch_skipped_network_disabled"
            extracted_rows.append(skipped_row(candidate, "fetch_skipped_network_disabled", "Network fetch disabled for deterministic headless run."))
            updated_candidates.append(candidate)
            continue

        existing = existing_by_url.get(clean(candidate.get("candidate_source_url")))
        should_refetch_relaxed_seed = (
            fetch_domain_seeds
            and clean(candidate.get("review_status")) == "official_domain_seed_needs_stats_path"
            and clean(existing.get("extraction_status") if existing else "") == "fetch_skipped_needs_stats_path"
        )
        lower_url = clean(candidate.get("candidate_source_url")).lower().split("?", 1)[0]
        should_refetch_extension = any(lower_url.endswith(extension) for extension in refetch_url_extensions)
        should_refetch_existing = (
            should_refetch_relaxed_seed
            or clean(existing.get("extraction_status") if existing else "") in refetch_statuses
            or should_refetch_extension
        )
        if reuse_existing and existing and not should_refetch_existing:
            candidate["fetch_status"] = clean(existing.get("fetch_status"))
            extracted_rows.append(normalize_existing_extraction(candidate, existing))
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
        if notes:
            extracted["notes"] = f"{clean(extracted.get('notes'))} {notes}".strip()
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
    parser.add_argument(
        "--fetch-domain-seeds",
        action="store_true",
        help="Also fetch official admissions/domain seed URLs that do not already look like stats pages.",
    )
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reuse existing extracted rows and only fetch candidates newly enabled by the requested mode.",
    )
    parser.add_argument(
        "--refetch-status",
        action="append",
        default=[],
        help="When --reuse-existing is set, refetch rows whose existing extraction_status matches this value. Repeatable.",
    )
    parser.add_argument(
        "--refetch-url-extension",
        action="append",
        default=[],
        help="When --reuse-existing is set, refetch candidate URLs with this file extension, such as .png or .jpg. Repeatable.",
    )
    parser.add_argument("--progress-every", type=int, default=0, help="Print progress every N candidates.")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--school-id", default="")
    args = parser.parse_args()
    rows = build_md_official_extraction(
        fetch=args.fetch,
        timeout_seconds=args.timeout_seconds,
        school_id=args.school_id,
        fetch_domain_seeds=args.fetch_domain_seeds,
        reuse_existing=args.reuse_existing,
        refetch_statuses={clean(status) for status in args.refetch_status},
        refetch_url_extensions={clean(extension) for extension in args.refetch_url_extension},
        progress_every=args.progress_every,
    )
    accepted = sum(1 for row in rows if clean(row.get("extraction_status")) == "accepted")
    print(f"Wrote {MD_OFFICIAL_EXTRACTED_STATS_CSV.relative_to(ROOT)} with {accepted} accepted MD official extraction(s)")


if __name__ == "__main__":
    main()
