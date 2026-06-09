from __future__ import annotations

import base64
import binascii
import csv
import html
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urljoin, urlparse


AACOM_PROFILE_CANDIDATE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "campus_name",
    "state_abbrev",
    "school_website",
    "aacom_profile_url",
    "aacom_profile_title",
    "aacom_city",
    "aacom_state_abbrev",
    "aacom_slug",
    "match_status",
    "match_score",
    "match_reason",
    "discovery_method",
    "source_last_checked",
    "fetch_status",
    "review_status",
    "notes",
]

AACOM_EXTRACTED_STATS_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "aacom_profile_url",
    "aacom_profile_title",
    "match_status",
    "match_score",
    "fetch_status",
    "extraction_status",
    "stats_academic_year",
    "metric_population",
    "metric_type",
    "mcat_mean",
    "overall_gpa_mean",
    "oldest_mcat_considered",
    "latest_mcat_accepted",
    "evidence_text",
    "source_last_checked",
    "data_confidence",
    "review_status",
    "notes",
]

AACOM_COVERAGE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_count",
    "matched_candidate_count",
    "fetched_candidate_count",
    "accepted_extraction_count",
    "current_canonical_has_mcat",
    "current_canonical_has_gpa",
    "coverage_status",
    "next_action",
]

AACOM_REVIEW_QUEUE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "aacom_profile_url",
    "aacom_profile_title",
    "match_status",
    "match_score",
    "fetch_status",
    "review_status",
    "review_reason",
    "evidence_text",
    "recommended_action",
    "last_checked",
    "notes",
]

AACOM_CONFLICT_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "current_mcat",
    "current_gpa",
    "aacom_mcat",
    "aacom_gpa",
    "mcat_delta",
    "gpa_delta",
    "current_source_name",
    "current_source_url",
    "aacom_source_url",
    "conflict_status",
    "notes",
]

AACOM_PROFILE_BASE = "https://www.aacom.org"
AACOM_PROFILE_PATH_RE = re.compile(r"^/detail-pages/com/[^/?#]+/?$", re.IGNORECASE)
AACOM_PROFILE_URL_RE = re.compile(
    r"https?://(?:www\.)?aacom\.org/detail-pages/com/[a-z0-9][a-z0-9-]*/?",
    re.IGNORECASE,
)
AACOM_PROFILE_HREF_RE = re.compile(
    r"""href=["'](?P<href>(?:https?://(?:www\.)?aacom\.org)?/detail-pages/com/[^"']+)["']""",
    re.IGNORECASE,
)
AACOM_PROFILE_DATA_TARGET_RE = re.compile(
    r"""data-srch-target=["'](?P<target>[A-Za-z0-9+/=_-]+)["']""",
    re.IGNORECASE,
)
AACOM_PROFILE_CARD_RE = re.compile(
    r"""<a\b(?=[^>]*data-srch-target=["'](?P<target>[A-Za-z0-9+/=_-]+)["'])[^>]*>(?P<body>.*?)</a>""",
    re.IGNORECASE | re.DOTALL,
)
AACOM_PROFILE_CARD_TITLE_RE = re.compile(
    r"""<span\b[^>]*class=["'][^"']*\bitem-list__title\b[^"']*["'][^>]*>(?P<title>.*?)</span>""",
    re.IGNORECASE | re.DOTALL,
)
AACOM_PROFILE_CARD_LOCATION_RE = re.compile(
    r"""<div\b[^>]*class=["'][^"']*\bitem-list__location\b[^"']*["'][^>]*>.*?<span>(?P<location>.*?)</span>""",
    re.IGNORECASE | re.DOTALL,
)
AACOM_DATA_CONFIDENCE = "aacom_com_submitted_profile"
AACOM_SOURCE_NAME = "AACOM Choose D.O. Explorer"

TRUTHY = {"1", "true", "t", "yes", "y"}


@dataclass(frozen=True)
class AacomProfileMatch:
    school: dict[str, str] | None
    score: float
    status: str
    reason: str
    second_score: float = 0.0


@dataclass(frozen=True)
class AacomProfileCard:
    url: str
    title: str = ""
    city: str = ""
    state_abbrev: str = ""


def today_iso() -> str:
    return date.today().isoformat()


def clean(value: object) -> str:
    return str(value or "").strip()


def compact_text(value: object) -> str:
    return re.sub(r"\s+", " ", html.unescape(clean(value))).strip()


def strip_tags(value: str) -> str:
    return compact_text(re.sub(r"<[^>]+>", " ", value))


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


def parse_float(value: object) -> float | None:
    text = clean(value).replace("$", "").replace(",", "").replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_float(value: float | None, digits: int) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def normalize_url(url: str) -> str:
    text = clean(url)
    if text.startswith("/"):
        text = urljoin(AACOM_PROFILE_BASE, text)
    parsed = urlparse(text)
    if not parsed.scheme or not parsed.netloc:
        return ""
    path = parsed.path.rstrip("/")
    return f"https://www.aacom.org{path}"


def is_aacom_profile_url(url: str) -> bool:
    parsed = urlparse(normalize_url(url))
    host = parsed.netloc.lower().removeprefix("www.")
    return host == "aacom.org" and bool(AACOM_PROFILE_PATH_RE.match(parsed.path))


def decode_srch_target(target: str) -> str:
    text = clean(target)
    padded = text + ("=" * (-len(text) % 4))
    try:
        return base64.b64decode(padded).decode("utf-8", errors="replace")
    except (binascii.Error, ValueError):
        return ""


def aacom_slug_from_url(url: str) -> str:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[-2] == "com":
        return parts[-1]
    return ""


def title_from_slug(slug: str) -> str:
    return clean(slug).replace("-", " ").title()


def normalize_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(
        r"\b(the|of|at|and|for|college|school|university|medicine|medical|osteopathic|sciences|health|healthcare|campus)\b",
        " ",
        text,
    )
    return re.sub(r"\s+", " ", text).strip()


def token_set_ratio(left: str, right: str) -> float:
    left_norm = normalize_name(left)
    right_norm = normalize_name(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    jaccard = intersection / union
    sequence = SequenceMatcher(None, " ".join(sorted(left_tokens)), " ".join(sorted(right_tokens))).ratio()
    containment = intersection / min(len(left_tokens), len(right_tokens))
    return max(jaccard, sequence, containment)


def parse_aacom_profile_urls(document: str, base_url: str = AACOM_PROFILE_BASE) -> list[str]:
    urls = set()
    for match in AACOM_PROFILE_URL_RE.finditer(document):
        urls.add(normalize_url(match.group(0)))
    for match in AACOM_PROFILE_HREF_RE.finditer(document):
        urls.add(normalize_url(urljoin(base_url, match.group("href"))))
    for match in AACOM_PROFILE_DATA_TARGET_RE.finditer(document):
        decoded = decode_srch_target(match.group("target"))
        if is_aacom_profile_url(decoded):
            urls.add(normalize_url(decoded))
    return sorted(url for url in urls if is_aacom_profile_url(url))


def parse_location(location: str) -> tuple[str, str]:
    text = compact_text(location)
    match = re.search(r"(?P<city>.+?),\s*(?P<state>[A-Z]{2})\b", text)
    if not match:
        return "", ""
    return compact_text(match.group("city")), clean(match.group("state")).upper()


def parse_aacom_profile_cards(document: str, base_url: str = AACOM_PROFILE_BASE) -> list[AacomProfileCard]:
    cards: dict[str, AacomProfileCard] = {}
    for match in AACOM_PROFILE_CARD_RE.finditer(document):
        url = normalize_url(urljoin(base_url, decode_srch_target(match.group("target"))))
        if not is_aacom_profile_url(url):
            continue
        body = match.group("body")
        title_match = AACOM_PROFILE_CARD_TITLE_RE.search(body)
        location_match = AACOM_PROFILE_CARD_LOCATION_RE.search(body)
        title = strip_tags(title_match.group("title")) if title_match else title_from_slug(aacom_slug_from_url(url))
        city, state_abbrev = parse_location(strip_tags(location_match.group("location")) if location_match else "")
        cards[url] = AacomProfileCard(url=url, title=title, city=city, state_abbrev=state_abbrev)
    for url in parse_aacom_profile_urls(document, base_url):
        cards.setdefault(url, AacomProfileCard(url=url, title=title_from_slug(aacom_slug_from_url(url))))
    return sorted(cards.values(), key=lambda card: card.url)


def profile_match_text(url: str, title: str = "") -> str:
    slug = aacom_slug_from_url(url)
    return " ".join(part for part in [title, title_from_slug(slug), slug.replace("-", " ")] if part)


def normalized_city(value: object) -> str:
    return normalize_name(value)


def state_matches(school: dict[str, str], state_abbrev: str) -> bool:
    return bool(state_abbrev) and clean(school.get("state_abbrev")).upper() == clean(state_abbrev).upper()


def city_matches(school: dict[str, str], city: str) -> bool:
    return bool(city) and normalized_city(school.get("city")) == normalized_city(city)


def alias_match_score(school: dict[str, str], profile_text: str) -> float:
    acronym = normalize_name(school.get("source_acronym"))
    campus = normalize_name(school.get("campus_name"))
    text = normalize_name(profile_text)
    text_tokens = set(text.split())
    score = 0.0
    for alias in [acronym, campus]:
        alias_tokens = alias.split()
        if alias_tokens and set(alias_tokens).issubset(text_tokens):
            score = max(score, 0.04 + min(len(alias_tokens), 4) * 0.04)
    return score


def score_school_match(
    school: dict[str, str],
    profile_text: str,
    profile_city: str = "",
    profile_state_abbrev: str = "",
) -> float:
    candidates = [
        clean(school.get("school_name")),
        clean(school.get("parent_school_name")),
        clean(school.get("campus_name")),
        clean(school.get("source_acronym")),
    ]
    base = max((token_set_ratio(profile_text, candidate) for candidate in candidates if candidate), default=0.0)
    score = base
    if profile_state_abbrev:
        score += 0.14 if state_matches(school, profile_state_abbrev) else -0.35
    if profile_city:
        score += 0.28 if city_matches(school, profile_city) else -0.10
    score += alias_match_score(school, profile_text)
    return max(score, 0.0)


def best_profile_match(
    url: str,
    title: str,
    do_schools: list[dict[str, str]],
    city: str = "",
    state_abbrev: str = "",
) -> AacomProfileMatch:
    text = profile_match_text(url, title)
    state_filtered = [school for school in do_schools if state_matches(school, state_abbrev)]
    candidate_schools = state_filtered or do_schools
    scored = sorted(
        ((score_school_match(school, text, city, state_abbrev), school) for school in candidate_schools),
        key=lambda item: (-item[0], clean(item[1].get("school_id"))),
    )
    if not scored:
        return AacomProfileMatch(None, 0.0, "no_match", "No active DO schools available.")
    top_score, top_school = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    gap = top_score - second_score
    location_hint = " Location matched." if city_matches(top_school, city) else ""
    if top_score >= 0.92 and gap >= 0.02:
        return AacomProfileMatch(top_school, top_score, "safe_match", f"High-confidence AACOM profile match.{location_hint}", second_score)
    if top_score >= 0.80 and gap >= 0.08:
        return AacomProfileMatch(top_school, top_score, "review_match", f"Likely match but below safe threshold.{location_hint}", second_score)
    if top_score >= 0.70:
        return AacomProfileMatch(top_school, top_score, "ambiguous_match", "Profile match is ambiguous.", second_score)
    return AacomProfileMatch(top_school, top_score, "no_match", "No compatible DO school match above threshold.", second_score)
