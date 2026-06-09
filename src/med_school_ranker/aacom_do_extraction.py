from __future__ import annotations

import argparse
import re
import urllib.error
import urllib.request

from med_school_ranker.aacom_do_rules import (
    AACOM_DATA_CONFIDENCE,
    AACOM_EXTRACTED_STATS_COLUMNS,
    AACOM_PROFILE_CANDIDATE_COLUMNS,
    AACOM_REVIEW_QUEUE_COLUMNS,
    clean,
    compact_text,
    format_float,
    is_aacom_profile_url,
    read_csv,
    today_iso,
    write_csv,
)
from med_school_ranker.official_stats_extraction import html_to_text
from med_school_ranker.paths import (
    AACOM_DO_EXTRACTED_STATS_CSV,
    AACOM_DO_PROFILE_CANDIDATES_CSV,
    AACOM_DO_PROFILE_REVIEW_QUEUE_CSV,
    ROOT,
)


MCAT_MEAN_RE = re.compile(
    r"\bMean\s+MCAT\s+Score\b\s*:?\s*(?P<value>\b(?:47[2-9]|48\d|49\d|50\d|51\d|52[0-8])(?:\.\d)?)",
    re.IGNORECASE,
)
GPA_MEAN_RE = re.compile(
    r"\bAvg\.?\s+Cum\.?\s+Undergrad\s+GPA\s+Score\b\s*:?\s*(?P<value>\b[0-4](?:\.\d{1,3})?)",
    re.IGNORECASE,
)
OLDEST_MCAT_RE = re.compile(
    r"\bOldest\s+MCAT\s+Considered\b\s*:?\s*(?P<value>(?:20\d{2}|[A-Za-z]+\s+20\d{2}|[0-1]?\d/[0-3]?\d/20\d{2}))",
    re.IGNORECASE,
)
LATEST_MCAT_RE = re.compile(
    r"\bLatest\s+MCAT\s+Score\s+Accepted\b\s*:?\s*(?P<value>(?:20\d{2}|[A-Za-z]+\s+20\d{2}|[0-1]?\d/[0-3]?\d/20\d{2}))",
    re.IGNORECASE,
)
ACADEMIC_YEAR_RE = re.compile(r"\b(20\d{2})\s*[-/]\s*(?:20)?(\d{2})\b")


def parse_float(value: object) -> float | None:
    text = clean(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def aacom_stats_section(text: str) -> str:
    visible_text = compact_text(text)
    match = re.search(r"\bMCAT/GPA\s+Information\b", visible_text, re.IGNORECASE)
    if not match:
        return visible_text
    return visible_text[match.start() : match.start() + 1400]


def first_match_value(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return compact_text(match.group("value")) if match else ""


def stats_academic_year(text: str) -> str:
    match = ACADEMIC_YEAR_RE.search(text)
    if not match:
        return ""
    start, end = match.groups()
    return f"{start}-{end}"


def extract_aacom_stats_from_text(
    school: dict[str, str],
    candidate: dict[str, str],
    text: str,
    title: str = "",
) -> dict[str, str]:
    section = aacom_stats_section(text)
    mcat = parse_float(first_match_value(MCAT_MEAN_RE, section))
    gpa = parse_float(first_match_value(GPA_MEAN_RE, section))
    notes = ""

    if clean(school.get("degree_type") or candidate.get("degree_type")).upper() != "DO":
        extraction_status = "rejected_non_do_candidate"
        review_status = "needs_review"
        notes = "AACOM COM profile importer only applies to DO schools."
    elif not is_aacom_profile_url(clean(candidate.get("aacom_profile_url"))):
        extraction_status = "rejected_invalid_aacom_profile_url"
        review_status = "needs_review"
        notes = "Candidate URL is not an AACOM /detail-pages/com/ profile."
    elif mcat is not None and gpa is not None and 472 <= mcat <= 528 and 0 <= gpa <= 4.0:
        extraction_status = "accepted"
        review_status = "approved_aacom_extraction"
        notes = "AACOM COM-submitted profile mean MCAT and cumulative undergraduate GPA were extracted."
    elif mcat is not None or gpa is not None:
        extraction_status = "needs_review_partial_aacom_stats"
        review_status = "needs_review"
        notes = "Only one AACOM MCAT/GPA value was extracted."
    else:
        extraction_status = "no_relevant_aacom_stats_found"
        review_status = "needs_review"
        notes = "No AACOM MCAT/GPA Information values were found in the fetched profile text."

    return {
        "school_id": clean(school.get("school_id") or candidate.get("school_id")),
        "school_name": clean(school.get("school_name") or candidate.get("school_name")),
        "degree_type": clean(school.get("degree_type") or candidate.get("degree_type") or "DO"),
        "aacom_profile_url": clean(candidate.get("aacom_profile_url")),
        "aacom_profile_title": compact_text(title or clean(candidate.get("aacom_profile_title"))),
        "match_status": clean(candidate.get("match_status")),
        "match_score": clean(candidate.get("match_score")),
        "fetch_status": clean(candidate.get("fetch_status")) or "fetched",
        "extraction_status": extraction_status,
        "stats_academic_year": stats_academic_year(section),
        "metric_population": "AACOM COM-submitted profile",
        "metric_type": "aacom_reported_mean",
        "mcat_mean": format_float(mcat, 1),
        "overall_gpa_mean": format_float(gpa, 2),
        "oldest_mcat_considered": first_match_value(OLDEST_MCAT_RE, section),
        "latest_mcat_accepted": first_match_value(LATEST_MCAT_RE, section),
        "evidence_text": section[:700],
        "source_last_checked": today_iso(),
        "data_confidence": AACOM_DATA_CONFIDENCE,
        "review_status": review_status,
        "notes": notes,
    }


def fetch_aacom_profile_text(url: str, timeout_seconds: int) -> tuple[str, str, str, str]:
    if not is_aacom_profile_url(url):
        return "fetch_skipped_invalid_aacom_url", "", "", "Candidate URL is not an AACOM profile URL."
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "med-school-ranker-aacom-do-stats-scanner/0.1 (+local research workflow)",
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            content_type = response.headers.get("content-type", "")
            body = response.read()
    except urllib.error.HTTPError as exc:
        return f"fetch_failed_http_{exc.code}", "", "", str(exc)
    except urllib.error.URLError as exc:
        return "fetch_failed_url_error", "", "", str(exc.reason)
    except TimeoutError:
        return "fetch_failed_timeout", "", "", "Request timed out."

    text = body.decode("utf-8", errors="replace")
    if "html" in content_type.lower() or "<html" in text.lower() or "<body" in text.lower():
        title, visible_text = html_to_text(text)
    else:
        title, visible_text = "", compact_text(text)
    return "fetched", title, visible_text, ""


def skipped_row(candidate: dict[str, str], status: str, notes: str) -> dict[str, str]:
    return {
        "school_id": clean(candidate.get("school_id")),
        "school_name": clean(candidate.get("school_name")),
        "degree_type": clean(candidate.get("degree_type") or "DO"),
        "aacom_profile_url": clean(candidate.get("aacom_profile_url")),
        "aacom_profile_title": clean(candidate.get("aacom_profile_title")),
        "fetch_status": status,
        "extraction_status": status,
        "stats_academic_year": "",
        "metric_population": "",
        "metric_type": "",
        "mcat_mean": "",
        "overall_gpa_mean": "",
        "oldest_mcat_considered": "",
        "latest_mcat_accepted": "",
        "evidence_text": "",
        "source_last_checked": today_iso(),
        "data_confidence": AACOM_DATA_CONFIDENCE if is_aacom_profile_url(clean(candidate.get("aacom_profile_url"))) else "",
        "review_status": "needs_review",
        "match_status": clean(candidate.get("match_status")),
        "match_score": clean(candidate.get("match_score")),
        "notes": notes,
    }


def review_row(extracted: dict[str, str]) -> dict[str, str]:
    status = clean(extracted.get("extraction_status"))
    if status == "fetch_skipped_network_disabled":
        reason = "network_disabled"
        recommended = "Rerun med-school-extract-aacom-do-stats --fetch when network access is available."
    elif status == "fetch_skipped_needs_review":
        reason = "candidate_needs_review"
        recommended = "Review and approve the AACOM profile match before fetching."
    elif status == "fetch_skipped_invalid_aacom_url":
        reason = "invalid_aacom_url"
        recommended = "Replace the candidate with an AACOM /detail-pages/com/ profile URL."
    elif status == "needs_review_partial_aacom_stats":
        reason = "partial_stats"
        recommended = "Review the AACOM profile text and verify both mean MCAT and mean cumulative GPA."
    elif status == "no_relevant_aacom_stats_found":
        reason = "stats_not_found"
        recommended = "Review the AACOM profile manually or update extraction patterns if the page changed."
    else:
        reason = status or "needs_review"
        recommended = "Review source manually."
    return {
        "school_id": clean(extracted.get("school_id")),
        "school_name": clean(extracted.get("school_name")),
        "degree_type": clean(extracted.get("degree_type") or "DO"),
        "aacom_profile_url": clean(extracted.get("aacom_profile_url")),
        "aacom_profile_title": clean(extracted.get("aacom_profile_title")),
        "match_status": clean(extracted.get("match_status")),
        "match_score": clean(extracted.get("match_score")),
        "fetch_status": clean(extracted.get("fetch_status")),
        "review_status": clean(extracted.get("review_status")),
        "review_reason": reason,
        "evidence_text": clean(extracted.get("evidence_text")),
        "recommended_action": recommended,
        "last_checked": today_iso(),
        "notes": clean(extracted.get("notes")),
    }


def build_aacom_do_extraction(fetch: bool = False, timeout_seconds: int = 15, school_id: str = "") -> list[dict[str, str]]:
    candidates = read_csv(AACOM_DO_PROFILE_CANDIDATES_CSV)
    if school_id:
        candidates = [row for row in candidates if clean(row.get("school_id")) == school_id]

    extracted_rows: list[dict[str, str]] = []
    updated_candidates: list[dict[str, str]] = []
    for candidate in candidates:
        candidate = dict(candidate)
        review_status = clean(candidate.get("review_status"))
        match_status = clean(candidate.get("match_status"))
        if review_status != "accepted_for_fetch" or match_status != "safe_match":
            candidate["fetch_status"] = "fetch_skipped_needs_review"
            extracted_rows.append(
                skipped_row(candidate, "fetch_skipped_needs_review", "Candidate did not pass the AACOM safe-match threshold.")
            )
            updated_candidates.append(candidate)
            continue
        if not fetch:
            candidate["fetch_status"] = "fetch_skipped_network_disabled"
            extracted_rows.append(
                skipped_row(candidate, "fetch_skipped_network_disabled", "Network fetch disabled for deterministic headless run.")
            )
            updated_candidates.append(candidate)
            continue

        fetch_status, title, text, fetch_notes = fetch_aacom_profile_text(clean(candidate.get("aacom_profile_url")), timeout_seconds)
        candidate["fetch_status"] = fetch_status
        candidate["source_last_checked"] = today_iso()
        if title and not clean(candidate.get("aacom_profile_title")):
            candidate["aacom_profile_title"] = title
        if fetch_status != "fetched":
            extracted_rows.append(skipped_row(candidate, fetch_status, fetch_notes))
            updated_candidates.append(candidate)
            continue

        extracted = extract_aacom_stats_from_text(candidate, candidate, text, title or clean(candidate.get("aacom_profile_title")))
        extracted["fetch_status"] = fetch_status
        extracted_rows.append(extracted)
        updated_candidates.append(candidate)

    write_csv(AACOM_DO_PROFILE_CANDIDATES_CSV, AACOM_PROFILE_CANDIDATE_COLUMNS, updated_candidates)
    write_csv(AACOM_DO_EXTRACTED_STATS_CSV, AACOM_EXTRACTED_STATS_COLUMNS, extracted_rows)
    write_csv(
        AACOM_DO_PROFILE_REVIEW_QUEUE_CSV,
        AACOM_REVIEW_QUEUE_COLUMNS,
        [review_row(row) for row in extracted_rows if clean(row.get("extraction_status")) != "accepted"],
    )
    return extracted_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract DO MCAT/GPA values from approved AACOM profile URLs.")
    parser.add_argument("--fetch", action="store_true", help="Fetch approved AACOM URLs over the network. Defaults to deterministic no-network mode.")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--school-id", default="")
    args = parser.parse_args()
    rows = build_aacom_do_extraction(fetch=args.fetch, timeout_seconds=args.timeout_seconds, school_id=args.school_id)
    accepted = sum(1 for row in rows if clean(row.get("extraction_status")) == "accepted")
    print(f"Wrote {AACOM_DO_EXTRACTED_STATS_CSV.relative_to(ROOT)} with {accepted} accepted AACOM extraction(s)")


if __name__ == "__main__":
    main()
