from __future__ import annotations

import argparse
import html
import http.client
import io
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

from med_school_ranker.official_source_rules import (
    OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    OFFICIAL_STATS_EXTRACTED_COLUMNS,
    OFFICIAL_STATS_REVIEW_QUEUE_COLUMNS,
    clean,
    format_float,
    read_csv,
    source_type_hint,
    today_iso,
    write_csv,
)
from med_school_ranker.paths import (
    OFFICIAL_STATS_EXTRACTED_VALUES_CSV,
    OFFICIAL_STATS_REVIEW_QUEUE_CSV,
    OFFICIAL_STATS_SOURCE_CANDIDATES_CSV,
    ROOT,
)


MCAT_RE = re.compile(
    r"(?:(?:median|mean|average|avg)\s+)?(?:total\s+)?mcat(?:\s+score)?[^0-9]{0,60}(?P<after>\b(?:47[2-9]|48\d|49\d|50\d|51\d|52[0-8])(?:\.\d)?)"
    r"|(?P<before>\b(?:47[2-9]|48\d|49\d|50\d|51\d|52[0-8])(?:\.\d)?)[^a-z0-9]{0,30}(?:(?:median|mean|average|avg)\s+)?(?:total\s+)?mcat(?:\s+score)?"
    r"|(?:mcat)(?:\s+\d{1,5}(?:,\d{3})?){1,3}\s+(?P<after_ocr>\b(?:47[2-9]|48\d|49\d|50\d|51\d|52[0-8])(?:\.\d)?)",
    re.IGNORECASE,
)
GPA_RE = re.compile(
    r"(?:(?:median|mean|average|avg)\s+)?(?:(?:overall|cumulative|undergraduate)\s+)?gpa(?:[^0-9]{0,40}(?:overall|cumulative|undergraduate))?[^0-9]{0,60}(?P<after>\b[2345]\.\d{1,3})"
    r"|(?P<before>\b[2345]\.\d{1,3})[^a-z0-9]{0,30}(?:(?:median|mean|average|avg)\s+)?(?:(?:overall|cumulative|undergraduate)\s+)?gpa"
    r"|(?:gpa)(?:\s+\d{1,5}(?:,\d{3})?){1,3}\s+(?P<after_ocr>\b[2345]\.\d{1,3})",
    re.IGNORECASE,
)
MINIMUM_TERMS = {
    "minimum",
    "required",
    "requirement",
    "requirements",
    "must have",
    "eligible",
    "eligibility",
    "screen",
    "screening",
    "cutoff",
    "cut-off",
    "threshold",
}
PROFILE_TERMS = {
    "accepted",
    "average",
    "class profile",
    "class statistics",
    "enrolled",
    "entering class",
    "matriculated",
    "matriculants",
    "mean",
    "median",
    "profile",
}
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff")
COHORT_YEAR_PATTERNS = (
    r"(?:entering|matriculating|incoming)\s+class(?:\s+of)?\s+(20\d{2})",
    r"class\s+of\s+(20\d{2})",
    r"(20\d{2})\s+(?:entering|matriculating|incoming)\s+class",
    r"(20\d{2})\s+class\s+profile",
)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = clean(data)
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        self.text_parts.append(text)

    @property
    def title(self) -> str:
        return compact_text(" ".join(self.title_parts))

    @property
    def text(self) -> str:
        return compact_text(" ".join(self.text_parts))


@dataclass(frozen=True)
class MetricCandidate:
    value: float
    metric: str
    context: str
    score: int
    rejected: bool
    reject_reason: str
    cohort_year: str = ""
    corrected: bool = False


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(clean(value))).strip()


def html_to_text(document: str) -> tuple[str, str]:
    parser = VisibleTextParser()
    parser.feed(document)
    return parser.title, parser.text


def pdf_bytes_to_text(document: bytes) -> str:
    reader = PdfReader(io.BytesIO(document))
    page_text = [compact_text(page.extract_text() or "") for page in reader.pages]
    return compact_text(" ".join(text for text in page_text if text))


def image_bytes_to_text(document: bytes, suffix: str, timeout_seconds: int) -> tuple[str, str]:
    if not shutil.which("tesseract"):
        return "", "image_ocr_unavailable"
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(document)
            temp_path = temp.name
        result = subprocess.run(
            ["tesseract", temp_path, "stdout", "--psm", "6"],
            check=False,
            capture_output=True,
            text=True,
            timeout=max(5, timeout_seconds),
        )
    except subprocess.TimeoutExpired:
        return "", "image_ocr_timeout"
    except OSError as exc:
        return "", f"image_ocr_failed:{exc}"
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
    text = compact_text(result.stdout)
    if result.returncode != 0 and not text:
        return "", f"image_ocr_failed:{compact_text(result.stderr)}"
    if not text:
        return "", "image_ocr_text_empty"
    return text, ""


def metric_name_from_context(context: str) -> str:
    lower = context.lower()
    if "median" in lower:
        return "median"
    if "mean" in lower:
        return "mean"
    if "average" in lower or "avg" in lower:
        return "average"
    return "published"


def context_score(context: str) -> tuple[int, bool, str]:
    lower = context.lower()
    for term in MINIMUM_TERMS:
        if term in lower:
            return 0, True, f"minimum_requirement_context:{term}"
    score = 0
    for term in PROFILE_TERMS:
        if term in lower:
            score += 1
    if "class composition" in lower or "new entrants" in lower:
        score += 3
    if "class of" in lower:
        score += 1
    return score, False, ""


def candidate_context(text: str, start: int, end: int, window: int = 180) -> str:
    return compact_text(text[max(0, start - window) : min(len(text), end + window)])


def cohort_year_anchors(text: str) -> list[tuple[int, str]]:
    anchors: list[tuple[int, str]] = []
    for pattern in COHORT_YEAR_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            anchors.append((match.start(), match.group(1)))
    return sorted(set(anchors), key=lambda item: item[0])


def cohort_year_for_position(anchors: list[tuple[int, str]], position: int, max_distance: int = 2500) -> str:
    selected = ""
    selected_position = -1
    for anchor_position, year in anchors:
        if anchor_position > position:
            break
        selected = year
        selected_position = anchor_position
    if selected and position - selected_position <= max_distance:
        return selected
    return ""


def last_gpa_qualifier_position(window: str, terms: list[str], word_boundary: bool = False) -> int:
    positions = []
    for term in terms:
        if word_boundary:
            pattern = rf"(?<![a-z]){re.escape(term)}(?![a-z])"
            matches = list(re.finditer(pattern, window))
            positions.append(matches[-1].start() if matches else -1)
        else:
            positions.append(window.rfind(term))
    return max(positions)


def find_metric_candidates(
    text: str,
    pattern: re.Pattern[str],
    kind: str,
    allow_ocr_gpa_correction: bool = False,
    anchors: list[tuple[int, str]] | None = None,
) -> list[MetricCandidate]:
    candidates = []
    anchors = anchors if anchors is not None else cohort_year_anchors(text)
    for match in pattern.finditer(text):
        groups = match.groupdict()
        raw_value = next((groups.get(name) for name in ("after", "before", "after_ocr", "before_ocr") if groups.get(name)), "")
        if not raw_value:
            continue
        try:
            value = float(raw_value)
        except ValueError:
            continue
        context = candidate_context(text, match.start(), match.end())
        corrected = False
        if kind == "gpa" and not 0 <= value <= 4.0:
            if allow_ocr_gpa_correction and 5 <= value < 6 and "gpa" in context.lower():
                value = round(value - 2, 3)
                corrected = True
            else:
                continue
        if kind == "mcat" and not 472 <= value <= 528:
            continue
        score, rejected, reject_reason = context_score(context)
        if kind == "gpa":
            qualifier_window = text[max(0, match.start() - 45) : match.end()].lower()
            allowed_position = last_gpa_qualifier_position(
                qualifier_window,
                ["overall", "cumulative", "undergraduate", "total gpa", "total", "class gpa", "class"],
            )
            disallowed_position = max(
                last_gpa_qualifier_position(qualifier_window, ["science", "bcpm", "postbac", "post-bac"]),
                last_gpa_qualifier_position(qualifier_window, ["graduate", "masters", "master's"], word_boundary=True),
            )
            if disallowed_position > allowed_position:
                candidates.append(
                    MetricCandidate(
                        value=value,
                        metric="science_or_bcpm",
                        context=context,
                        score=0,
                        rejected=True,
                        reject_reason="science_or_bcpm_gpa_context",
                        cohort_year=cohort_year_for_position(anchors, match.start()),
                        corrected=corrected,
                    )
                )
                continue
            if allowed_position >= 0:
                score += 2
        candidates.append(
            MetricCandidate(
                value=value,
                metric=metric_name_from_context(context),
                context=context,
                score=score,
                rejected=rejected,
                reject_reason=reject_reason,
                cohort_year=cohort_year_for_position(anchors, match.start()),
                corrected=corrected,
            )
        )
    return candidates


def best_metric_candidate(candidates: list[MetricCandidate]) -> MetricCandidate | None:
    accepted = [candidate for candidate in candidates if not candidate.rejected and candidate.score > 0]
    if not accepted:
        return None
    return sorted(accepted, key=lambda item: (-item.score, item.metric != "median", -int(item.cohort_year or 0), item.value))[0]


def best_metric_pair(
    mcat_candidates: list[MetricCandidate],
    gpa_candidates: list[MetricCandidate],
) -> tuple[MetricCandidate | None, MetricCandidate | None, str]:
    accepted_mcats = [candidate for candidate in mcat_candidates if not candidate.rejected and candidate.score > 0]
    accepted_gpas = [candidate for candidate in gpa_candidates if not candidate.rejected and candidate.score > 0]
    shared_years = {
        candidate.cohort_year
        for candidate in accepted_mcats
        if candidate.cohort_year and any(gpa.cohort_year == candidate.cohort_year for gpa in accepted_gpas)
    }
    for year in sorted(shared_years, key=int, reverse=True):
        best_mcat = best_metric_candidate([candidate for candidate in accepted_mcats if candidate.cohort_year == year])
        best_gpa = best_metric_candidate([candidate for candidate in accepted_gpas if candidate.cohort_year == year])
        if best_mcat and best_gpa:
            return best_mcat, best_gpa, year
    best_mcat = best_metric_candidate(mcat_candidates)
    best_gpa = best_metric_candidate(gpa_candidates)
    return best_mcat, best_gpa, ""


def rejected_only_reason(candidates: list[MetricCandidate]) -> str:
    reasons = sorted({candidate.reject_reason for candidate in candidates if candidate.rejected and candidate.reject_reason})
    return "; ".join(reasons)


def cohort_year_from_text(text: str) -> str:
    years = [year for _, year in cohort_year_anchors(text)]
    return str(max(int(year) for year in years)) if years else ""


def population_from_context(context: str) -> str:
    lower = context.lower()
    if "accepted" in lower or "admitted" in lower:
        return "accepted students"
    if any(term in lower for term in ["matriculant", "matriculated", "enrolled", "entering class"]):
        return "matriculated students"
    return "official published school profile"


def metric_type_from_candidates(mcat: MetricCandidate | None, gpa: MetricCandidate | None) -> str:
    metrics = {candidate.metric for candidate in [mcat, gpa] if candidate}
    if "median" in metrics:
        return "official_published_median"
    if "mean" in metrics or "average" in metrics:
        return "official_published_mean"
    return "official_published_value"


def extract_stats_from_text(
    school: dict[str, str],
    candidate: dict[str, str],
    text: str,
    title: str = "",
) -> dict[str, str]:
    visible_text = compact_text(text)
    title = compact_text(title or clean(candidate.get("candidate_source_title")))
    lower_url = clean(candidate.get("candidate_source_url")).lower().split("?", 1)[0]
    allow_ocr_gpa_correction = lower_url.endswith(IMAGE_EXTENSIONS)
    anchors = cohort_year_anchors(visible_text)
    mcat_candidates = find_metric_candidates(visible_text, MCAT_RE, "mcat", anchors=anchors)
    gpa_candidates = find_metric_candidates(visible_text, GPA_RE, "gpa", allow_ocr_gpa_correction=allow_ocr_gpa_correction, anchors=anchors)
    best_mcat, best_gpa, selected_cohort_year = best_metric_pair(mcat_candidates, gpa_candidates)
    evidence_parts = [candidate.context for candidate in [best_mcat, best_gpa] if candidate]
    evidence = compact_text(" ".join(evidence_parts))[:700]
    official_score = float(clean(candidate.get("official_domain_score")) or 0)

    if best_mcat and best_gpa and official_score >= 0.9:
        extraction_status = "accepted"
        review_status = "approved_official_extraction"
        notes = "Official-domain MCAT/GPA values found in class-profile context."
        if selected_cohort_year:
            notes += f" Selected latest shared cohort year {selected_cohort_year}."
        if best_gpa.corrected:
            notes += " GPA value used OCR correction from impossible 5.xx reading to 3.xx on an official image source."
    elif best_mcat or best_gpa:
        extraction_status = "needs_review_partial_stats"
        review_status = "needs_review"
        notes = "Only one MCAT/GPA value was extracted or source is below official-domain threshold."
    else:
        rejected_reason = rejected_only_reason(mcat_candidates + gpa_candidates)
        if rejected_reason:
            extraction_status = "rejected_minimum_requirement"
            notes = f"Only rejected minimum/eligibility contexts found: {rejected_reason}."
        else:
            extraction_status = "no_relevant_stats_found"
            notes = "No class-profile MCAT/GPA values found."
        review_status = "needs_review"

    combined_context = " ".join(evidence_parts)
    return {
        "school_id": clean(school.get("school_id") or candidate.get("school_id")),
        "school_name": clean(school.get("school_name") or candidate.get("school_name")),
        "degree_type": clean(school.get("degree_type") or candidate.get("degree_type")),
        "candidate_source_url": clean(candidate.get("candidate_source_url")),
        "candidate_source_title": title,
        "candidate_source_type": source_type_hint(candidate.get("candidate_source_url", ""), title, visible_text),
        "official_domain_status": clean(candidate.get("official_domain_status")),
        "official_domain_score": clean(candidate.get("official_domain_score")),
        "fetch_status": clean(candidate.get("fetch_status")) or "fetched",
        "extraction_status": extraction_status,
        "review_status": review_status,
        "stats_cohort_year": selected_cohort_year or cohort_year_from_text(visible_text),
        "metric_population": population_from_context(combined_context),
        "metric_type": metric_type_from_candidates(best_mcat, best_gpa),
        "mcat_value": format_float(best_mcat.value if best_mcat else None, 1),
        "mcat_metric": best_mcat.metric if best_mcat else "",
        "gpa_value": format_float(best_gpa.value if best_gpa else None, 2),
        "gpa_metric": best_gpa.metric if best_gpa else "",
        "science_gpa_value": "",
        "source_publication_date": "",
        "source_last_checked": today_iso(),
        "evidence_text": evidence,
        "notes": notes,
    }


def fetch_candidate_text(url: str, timeout_seconds: int) -> tuple[str, str, str, str]:
    lower_url = clean(url).lower().split("?", 1)[0]
    is_pdf_url = lower_url.endswith(".pdf")
    image_suffix = next((suffix for suffix in IMAGE_EXTENSIONS if lower_url.endswith(suffix)), "")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "med-school-ranker-official-stats-scanner/0.1 (+local research workflow)",
            "Accept": "text/html,application/xhtml+xml,application/pdf,text/plain;q=0.9,*/*;q=0.1",
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
    except http.client.HTTPException as exc:
        return "fetch_failed_http_exception", "", "", str(exc)
    except OSError as exc:
        return "fetch_failed_os_error", "", "", str(exc)
    except TimeoutError:
        return "fetch_failed_timeout", "", "", "Request timed out."

    if is_pdf_url or "pdf" in content_type.lower():
        try:
            visible_text = pdf_bytes_to_text(body)
        except Exception as exc:
            return "pdf_parse_failed", "", "", str(exc)
        if not visible_text:
            return "pdf_text_empty", "", "", "PDF parsed but no extractable text was found."
        title = clean(url).rsplit("/", 1)[-1]
        return "fetched", title, visible_text, ""
    if image_suffix or content_type.lower().startswith("image/"):
        suffix = image_suffix or f".{content_type.lower().split('/', 1)[1].split(';', 1)[0]}"
        visible_text, ocr_error = image_bytes_to_text(body, suffix, timeout_seconds)
        if ocr_error:
            return ocr_error.split(":", 1)[0], "", "", ocr_error
        title = clean(url).rsplit("/", 1)[-1]
        return "fetched", title, visible_text, ""
    text = body.decode("utf-8", errors="replace")
    if "<html" in text.lower() or "<body" in text.lower():
        title, visible_text = html_to_text(text)
    else:
        title, visible_text = "", compact_text(text)
    return "fetched", title, visible_text, ""


def skipped_row(candidate: dict[str, str], status: str, notes: str) -> dict[str, str]:
    return {
        "school_id": clean(candidate.get("school_id")),
        "school_name": clean(candidate.get("school_name")),
        "degree_type": clean(candidate.get("degree_type")),
        "candidate_source_url": clean(candidate.get("candidate_source_url")),
        "candidate_source_title": clean(candidate.get("candidate_source_title")),
        "candidate_source_type": clean(candidate.get("candidate_source_type")),
        "official_domain_status": clean(candidate.get("official_domain_status")),
        "official_domain_score": clean(candidate.get("official_domain_score")),
        "fetch_status": status,
        "extraction_status": status,
        "review_status": "needs_review",
        "stats_cohort_year": "",
        "metric_population": "",
        "metric_type": "",
        "mcat_value": "",
        "mcat_metric": "",
        "gpa_value": "",
        "gpa_metric": "",
        "science_gpa_value": "",
        "source_publication_date": "",
        "source_last_checked": today_iso(),
        "evidence_text": "",
        "notes": notes,
    }


def review_row(extracted: dict[str, str]) -> dict[str, str]:
    status = clean(extracted.get("extraction_status"))
    if status == "accepted":
        recommended = "Apply official stats row."
        reason = ""
    elif status == "fetch_skipped_network_disabled":
        recommended = "Rerun med-school-extract-official-stats --fetch when network access is available."
        reason = "network_disabled"
    elif status == "fetch_skipped_needs_review":
        recommended = "Approve or reject the candidate URL before fetching."
        reason = "domain_needs_review"
    elif status == "fetch_skipped_needs_stats_path":
        recommended = "Find a class profile, annual report, fact book, or admissions statistics URL on the official domain."
        reason = "needs_stats_path"
    elif status == "unsupported_pdf_without_parser":
        recommended = "Extract manually or add a PDF parser in a later slice."
        reason = "pdf_not_parsed"
    elif status == "pdf_parse_failed":
        recommended = "Review source manually; PDF could not be parsed as text."
        reason = "pdf_parse_failed"
    elif status == "pdf_text_empty":
        recommended = "Review source manually or add OCR; PDF appears image-based or has no extractable text."
        reason = "pdf_text_empty"
    elif status == "image_ocr_unavailable":
        recommended = "Install tesseract or review image manually."
        reason = "image_ocr_unavailable"
    elif status == "image_ocr_failed":
        recommended = "Review image manually; OCR failed."
        reason = "image_ocr_failed"
    elif status == "image_ocr_timeout":
        recommended = "Review image manually or rerun OCR with a longer timeout."
        reason = "image_ocr_timeout"
    elif status == "image_ocr_text_empty":
        recommended = "Review image manually; OCR produced no text."
        reason = "image_ocr_text_empty"
    elif status == "rejected_minimum_requirement":
        recommended = "Do not apply unless a reviewer verifies these are class profile values."
        reason = "minimum_requirement_context"
    else:
        recommended = "Review source manually."
        reason = status or "needs_review"
    return {
        "school_id": clean(extracted.get("school_id")),
        "school_name": clean(extracted.get("school_name")),
        "degree_type": clean(extracted.get("degree_type")),
        "candidate_source_url": clean(extracted.get("candidate_source_url")),
        "candidate_source_title": clean(extracted.get("candidate_source_title")),
        "candidate_source_type": clean(extracted.get("candidate_source_type")),
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


def build_official_stats_extraction(fetch: bool = False, timeout_seconds: int = 15, school_id: str = "") -> list[dict[str, str]]:
    candidates = read_csv(OFFICIAL_STATS_SOURCE_CANDIDATES_CSV)
    if school_id:
        candidates = [row for row in candidates if clean(row.get("school_id")) == school_id]

    extracted_rows: list[dict[str, str]] = []
    updated_candidates: list[dict[str, str]] = []
    for candidate in candidates:
        candidate = dict(candidate)
        review_status = clean(candidate.get("review_status"))
        if review_status != "accepted_for_fetch":
            if review_status == "official_domain_seed_needs_stats_path":
                skip_status = "fetch_skipped_needs_stats_path"
                notes = "Official domain seed needs a class profile, annual report, fact book, or admissions statistics path before fetching."
            else:
                skip_status = "fetch_skipped_needs_review"
                notes = "Candidate did not pass the official-domain auto-fetch threshold."
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
        candidate["last_checked"] = today_iso()
        if title and not clean(candidate.get("candidate_source_title")):
            candidate["candidate_source_title"] = title
        if fetch_status != "fetched":
            extracted_rows.append(skipped_row(candidate, fetch_status, fetch_notes))
            updated_candidates.append(candidate)
            continue
        extracted = extract_stats_from_text(candidate, candidate, text, title or clean(candidate.get("candidate_source_title")))
        extracted["fetch_status"] = fetch_status
        extracted_rows.append(extracted)
        updated_candidates.append(candidate)

    write_csv(OFFICIAL_STATS_SOURCE_CANDIDATES_CSV, OFFICIAL_SOURCE_CANDIDATE_COLUMNS, updated_candidates)
    write_csv(OFFICIAL_STATS_EXTRACTED_VALUES_CSV, OFFICIAL_STATS_EXTRACTED_COLUMNS, extracted_rows)
    write_csv(OFFICIAL_STATS_REVIEW_QUEUE_CSV, OFFICIAL_STATS_REVIEW_QUEUE_COLUMNS, [review_row(row) for row in extracted_rows if clean(row.get("extraction_status")) != "accepted"])
    return extracted_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract official MCAT/GPA values from approved candidate source URLs.")
    parser.add_argument("--fetch", action="store_true", help="Fetch approved official URLs over the network. Defaults to no-network deterministic mode.")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--school-id", default="")
    args = parser.parse_args()
    rows = build_official_stats_extraction(fetch=args.fetch, timeout_seconds=args.timeout_seconds, school_id=args.school_id)
    accepted = sum(1 for row in rows if clean(row.get("extraction_status")) == "accepted")
    print(f"Wrote {OFFICIAL_STATS_EXTRACTED_VALUES_CSV.relative_to(ROOT)} with {accepted} accepted official extraction(s)")


if __name__ == "__main__":
    main()
