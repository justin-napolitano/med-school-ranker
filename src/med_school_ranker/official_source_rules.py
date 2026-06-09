from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


OFFICIAL_SOURCE_CANDIDATE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "state_abbrev",
    "school_website",
    "candidate_source_url",
    "candidate_source_title",
    "candidate_source_type",
    "source_status",
    "official_domain_status",
    "official_domain_score",
    "official_match_reason",
    "discovery_method",
    "search_query",
    "discovered_at",
    "last_checked",
    "fetch_status",
    "review_status",
    "notes",
]

OFFICIAL_STATS_EXTRACTED_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_source_url",
    "candidate_source_title",
    "candidate_source_type",
    "official_domain_status",
    "official_domain_score",
    "fetch_status",
    "extraction_status",
    "review_status",
    "stats_cohort_year",
    "metric_population",
    "metric_type",
    "mcat_value",
    "mcat_metric",
    "gpa_value",
    "gpa_metric",
    "science_gpa_value",
    "source_publication_date",
    "source_last_checked",
    "evidence_text",
    "notes",
]

OFFICIAL_STATS_DISCOVERY_REPORT_COLUMNS = [
    "metric",
    "count",
    "notes",
]

OFFICIAL_STATS_REVIEW_QUEUE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_source_url",
    "candidate_source_title",
    "candidate_source_type",
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

OFFICIAL_STATS_COVERAGE_COLUMNS = [
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

OFFICIAL_STATS_CONFLICT_COLUMNS = [
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

UNSAFE_DISCOVERY_HOST_FRAGMENTS = {
    "google.",
    "bing.",
    "duckduckgo.",
    "perplexity.",
    "openai.",
    "chatgpt.",
    "reddit.",
    "studentdoctor.",
    "forums.studentdoctor.",
    "shemmassianconsulting.",
    "prospectivedoctor.",
    "thematchguy.",
    "cycletrack.",
    "admit.org",
    "beemoacademicconsulting.",
}

SOURCE_TYPE_HINTS = [
    ("class_profile", ("class profile", "student profile", "entering class", "matriculant profile")),
    ("annual_report", ("annual report", "fact book", "facts and figures", "report")),
    ("admissions_statistics", ("admissions statistics", "class statistics", "entering class statistics")),
    ("pdf_report", (".pdf",)),
    ("school_homepage", ("home", "school of medicine")),
]

TRUTHY = {"1", "true", "t", "yes", "y"}


@dataclass(frozen=True)
class OfficialSourceClassification:
    status: str
    score: float
    reason: str

    @property
    def accepted_for_auto_extraction(self) -> bool:
        return self.score >= 0.9 and self.status.startswith("official")


def today_iso() -> str:
    return date.today().isoformat()


def clean(value: object) -> str:
    return str(value or "").strip()


def is_truthy(value: object) -> bool:
    return clean(value).lower() in TRUTHY


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


def normalized_host(url: str) -> str:
    parsed = urlparse(clean(url))
    host = parsed.netloc.lower()
    if "@" in host:
        host = host.rsplit("@", 1)[1]
    host = host.split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def registrable_domain(host: str) -> str:
    host = normalized_host(host) if "://" in host else clean(host).lower().removeprefix("www.")
    parts = [part for part in host.split(".") if part]
    if len(parts) <= 2:
        return host
    if parts[-2] in {"co", "com", "ac", "edu", "org"} and len(parts[-1]) == 2 and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def normalize_words(value: object) -> set[str]:
    text = clean(value).lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    stopwords = {
        "a",
        "an",
        "and",
        "at",
        "college",
        "of",
        "school",
        "the",
        "university",
        "medicine",
        "medical",
    }
    return {word for word in text.split() if len(word) > 2 and word not in stopwords}


def school_name_signal(school_name: str, haystack: str) -> bool:
    school_words = normalize_words(school_name)
    haystack_words = normalize_words(haystack)
    if not school_words or not haystack_words:
        return False
    return len(school_words & haystack_words) >= min(2, len(school_words))


def is_unsafe_discovery_url(url: str) -> bool:
    parsed = urlparse(clean(url))
    host = normalized_host(url)
    if not parsed.scheme or not host:
        return True
    if any(fragment in host for fragment in UNSAFE_DISCOVERY_HOST_FRAGMENTS):
        return True
    if parsed.path.lower().startswith("/search"):
        return True
    return False


def classify_official_source(
    school: dict[str, str],
    candidate_url: str,
    candidate_title: str = "",
    candidate_text: str = "",
) -> OfficialSourceClassification:
    url = clean(candidate_url)
    if is_unsafe_discovery_url(url):
        return OfficialSourceClassification("rejected_non_official_or_search", 0.0, "Search, AI, forum, or third-party advising URL")

    candidate_host = normalized_host(url)
    school_host = normalized_host(school.get("website", ""))
    candidate_domain = registrable_domain(candidate_host)
    school_domain = registrable_domain(school_host)
    context = " ".join([candidate_title, candidate_text, url, candidate_host])

    if school_host and candidate_host == school_host:
        return OfficialSourceClassification("official_school_domain", 1.0, "Candidate host exactly matches school website host")
    if school_domain and candidate_domain == school_domain:
        score = 0.95 if school_name_signal(school.get("school_name", ""), context) else 0.9
        return OfficialSourceClassification("official_school_domain_family", score, "Candidate host shares the school website domain")
    if candidate_host.endswith(".edu") and school_name_signal(school.get("school_name", ""), context):
        return OfficialSourceClassification("official_edu_name_match", 0.9, "EDU host with school-name signal")
    if candidate_host.endswith(".edu"):
        return OfficialSourceClassification("needs_review_edu_domain", 0.7, "EDU host without enough school-name signal")
    if school_name_signal(school.get("school_name", ""), context):
        return OfficialSourceClassification("needs_review_name_match", 0.55, "School-name signal on non-EDU external domain")
    return OfficialSourceClassification("needs_review_unknown_domain", 0.25, "No official-domain evidence")


def source_type_hint(url: str, title: str = "", text: str = "") -> str:
    haystack = " ".join([clean(url), clean(title), clean(text)]).lower()
    for source_type, hints in SOURCE_TYPE_HINTS:
        if any(hint in haystack for hint in hints):
            return source_type
    return "unknown"


def format_float(value: float | None, digits: int) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")
