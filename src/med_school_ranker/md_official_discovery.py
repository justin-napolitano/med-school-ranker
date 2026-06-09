from __future__ import annotations

import argparse
import http.client
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urlunparse

from med_school_ranker.md_official_rules import (
    MD_OFFICIAL_COVERAGE_COLUMNS,
    MD_OFFICIAL_DISCOVERY_REPORT_COLUMNS,
    MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS,
    clean,
    is_fetch_ready_source_type,
    is_md_admissions_like,
    is_md_program_relevant_url,
    is_md_stats_like,
    is_truthy,
    md_source_classification,
    md_source_type_hint,
    normalized_host,
    read_csv,
    same_registrable_domain,
    today_iso,
    write_csv,
)
from med_school_ranker.official_stats_extraction import fetch_candidate_text, html_to_text
from med_school_ranker.paths import (
    ADMISSIONS_SOURCE_QUEUE_CSV,
    ADMISSIONS_STATS_CSV,
    LETTER_REQUIREMENTS_CSV,
    MASTER_CSV,
    MD_OFFICIAL_ASSISTED_SEARCH_SEEDS_CSV,
    MD_OFFICIAL_COVERAGE_CSV,
    MD_OFFICIAL_DISCOVERY_REPORT_CSV,
    MD_OFFICIAL_SOURCE_CANDIDATES_CSV,
    ROOT,
    SOURCE_TABLES,
)
from med_school_ranker.source_integration import fmt_decimal, load_overrides, load_school_master, match_school


PUBLISHED_STATS_SOURCE_CSV = SOURCE_TABLES / "all_published_mcat_gpa_sources.csv"
CYCLETRACK_LOR_REQUIREMENTS_CSV = SOURCE_TABLES / "cycletrack_lor_requirements.csv"
SITEMAP_LOC_RE = re.compile(r"<loc>\s*(?P<url>[^<]+)\s*</loc>", re.IGNORECASE)

MD_KNOWN_STATS_PATHS = (
    "admissions/class-profile/",
    "admissions/entering-class-profile/",
    "admissions/entering-class-statistics/",
    "admissions/class-statistics/",
    "admissions/statistics/",
    "admissions/admissions-statistics/",
    "md-admissions/class-profile/",
    "md-admissions/entering-class-profile/",
    "md-program/admissions/class-profile/",
    "md-program/admissions/entering-class-profile/",
    "education/md/admissions/class-profile/",
    "education/md/admissions/entering-class-profile/",
    "education/md-program/admissions/class-profile/",
    "education/md-program/admissions/entering-class-profile/",
    "medical-student-admissions/md-admissions/class-profile/",
    "medical-student-admissions/class-profile/",
    "academics/medicine/class-profile/",
    "academics/md-program/admissions/class-profile/",
    "class-profile/",
    "entering-class-profile/",
    "entering-class-statistics/",
    "class-statistics/",
    "admissions-profile/",
    "facts-and-figures/",
    "about/facts-and-figures/",
    "fast-facts/",
    "facts/",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href_stack: list[str] = []
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = ""
        for key, value in attrs:
            if key.lower() == "href" and value:
                href = value
                break
        self._href_stack.append(href)
        self._text_parts.append("")

    def handle_data(self, data: str) -> None:
        if self._href_stack:
            self._text_parts[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._href_stack:
            return
        href = self._href_stack.pop()
        text = clean(self._text_parts.pop())
        if href:
            self.links.append((href, text))


def active_md_school_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(MASTER_CSV):
        if clean(row.get("degree_type")).upper() != "MD":
            continue
        if row.get("active_in_universe") and not is_truthy(row.get("active_in_universe")):
            continue
        if is_truthy(row.get("manual_exclusion_flag")):
            continue
        rows.append(row)
    return rows


def search_query_for_school(school: dict[str, str]) -> str:
    return f'"{clean(school.get("school_name"))}" entering class profile MCAT GPA matriculants official'


def inferred_school_for_candidate(school: dict[str, str], seed_url: str = "") -> dict[str, str]:
    inferred = dict(school)
    if seed_url and not clean(inferred.get("website")):
        parsed = urlparse(seed_url)
        if parsed.scheme and parsed.netloc:
            inferred["website"] = urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))
    return inferred


def candidate_row(
    school: dict[str, str],
    candidate_url: str,
    discovery_method: str,
    candidate_title: str = "",
    notes: str = "",
    school_website: str = "",
    candidate_text: str = "",
) -> dict[str, str]:
    school_for_classification = inferred_school_for_candidate(school, school_website or candidate_url)
    source_type = md_source_type_hint(candidate_url, candidate_title, candidate_text)
    classification = md_source_classification(school_for_classification, candidate_url, candidate_title, candidate_text)
    if classification.accepted_for_auto_extraction and is_fetch_ready_source_type(source_type):
        review_status = "accepted_for_fetch"
        fetch_status = "not_fetched"
    elif classification.accepted_for_auto_extraction:
        review_status = "official_domain_seed_needs_stats_path"
        fetch_status = "not_applicable"
    else:
        review_status = "needs_review"
        fetch_status = "not_fetched"
    return {
        "school_id": clean(school.get("school_id")),
        "school_name": clean(school.get("school_name")),
        "degree_type": "MD",
        "state_abbrev": clean(school.get("state_abbrev")),
        "school_website": clean(school_website or school_for_classification.get("website")),
        "candidate_source_url": clean(candidate_url),
        "candidate_source_title": clean(candidate_title),
        "candidate_source_type": source_type,
        "source_host": normalized_host(candidate_url),
        "official_domain_status": classification.status,
        "official_domain_score": f"{classification.score:.2f}",
        "official_match_reason": classification.reason,
        "discovery_method": discovery_method,
        "search_or_sitemap_query": search_query_for_school(school),
        "source_last_checked": today_iso(),
        "fetch_status": fetch_status,
        "review_status": review_status,
        "notes": notes,
    }


def rows_from_school_master(schools: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for school in schools:
        for field, method, title in [
            ("admissions_source_url", "school_master_admissions_source_url", "Admissions source URL from school_master"),
            ("website", "school_master_website", "School website from school_master"),
        ]:
            url = clean(school.get(field))
            if url:
                rows.append(candidate_row(school, url, method, title, school_website=url))
    return rows


def rows_from_manual_queue(schools_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for queue_row in read_csv(ADMISSIONS_SOURCE_QUEUE_CSV):
        school_id = clean(queue_row.get("school_id"))
        url = clean(queue_row.get("candidate_source_url"))
        school = schools_by_id.get(school_id)
        if not school or not url or clean(school.get("degree_type")).upper() != "MD":
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "manual_admissions_source_queue",
                clean(queue_row.get("candidate_source_title") or queue_row.get("source_title")),
                clean(queue_row.get("notes")),
                school_website=url,
            )
        )
    return rows


def rows_from_letter_requirements(schools_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv(LETTER_REQUIREMENTS_CSV):
        if clean(source_row.get("degree_type")).upper() != "MD":
            continue
        school = schools_by_id.get(clean(source_row.get("school_id")))
        url = clean(source_row.get("requirement_url"))
        if not school or not url:
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "normalized_letter_requirement_url",
                "Letter requirement URL from normalized source table",
                "Candidate URL only; letter requirement page is not score evidence unless fetched class-profile context is found.",
                school_website=url,
            )
        )
    return rows


def rows_from_cycletrack_lor_requirements(schools_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    school_records = load_school_master()
    overrides = load_overrides()
    rows = []
    for source_row in read_csv(CYCLETRACK_LOR_REQUIREMENTS_CSV):
        if clean(source_row.get("category")) != "USA MD":
            continue
        source_name = clean(source_row.get("school_name_clean") or source_row.get("school_name_raw"))
        source_row_number = clean(source_row.get("source_row_number"))
        for field, method in [
            ("md_requirements_url", "cycletrack_md_requirement_url"),
            ("md_phd_requirements_url", "cycletrack_md_phd_requirement_url"),
        ]:
            url = clean(source_row.get(field))
            if not source_name or not url:
                continue
            match = match_school(
                "cycletrack_lor_requirements.csv",
                source_row_number,
                source_name,
                "",
                "MD",
                school_records,
                overrides,
            )
            if not match.is_safe or not match.school:
                continue
            school = schools_by_id.get(match.school.school_id)
            if not school:
                continue
            rows.append(
                candidate_row(
                    school,
                    url,
                    method,
                    source_name,
                    f"Matched CycleTrack requirement URL as official candidate seed; match={match.label} score={fmt_decimal(match.score)}.",
                    school_website=url,
                )
            )
    return rows


def rows_from_published_source_urls(schools_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    school_records = load_school_master()
    overrides = load_overrides()
    rows = []
    for source_row in read_csv(PUBLISHED_STATS_SOURCE_CSV):
        url = clean(source_row.get("school_source_url"))
        source_name = clean(source_row.get("school_name_clean") or source_row.get("school_name_raw"))
        if not url or not source_name:
            continue
        match = match_school(
            "all_published_mcat_gpa_sources.csv",
            clean(source_row.get("source_row_number")),
            source_name,
            clean(source_row.get("state")),
            "MD",
            school_records,
            overrides,
        )
        if not match.is_safe or not match.school:
            continue
        school = schools_by_id.get(match.school.school_id)
        if not school:
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "third_party_school_source_url_seed",
                source_name,
                (
                    "URL came from a third-party table's school_source_url field and is used only as "
                    f"an official candidate seed; values from that table are not evidence. match={match.label} score={fmt_decimal(match.score)}."
                ),
                school_website=url,
            )
        )
    return rows


def rows_from_assisted_search_seeds(schools_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for source_row in read_csv(MD_OFFICIAL_ASSISTED_SEARCH_SEEDS_CSV):
        school_id = clean(source_row.get("school_id"))
        school = schools_by_id.get(school_id)
        url = clean(source_row.get("candidate_source_url"))
        if not school or not url or clean(source_row.get("degree_type") or school.get("degree_type")).upper() != "MD":
            continue
        if clean(source_row.get("review_status")) not in {"approved_for_discovery", "accepted_for_fetch", ""}:
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "assisted_search_official_url_seed",
                clean(source_row.get("candidate_source_title")),
                (
                    "Official URL discovered via assisted web search; search result text is not evidence. "
                    f"provider={clean(source_row.get('search_provider'))}; rank={clean(source_row.get('result_rank'))}; "
                    f"query={clean(source_row.get('search_query'))}. {clean(source_row.get('notes'))}"
                ),
                school_website=url,
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
        notes = sorted({clean(existing.get("notes")), clean(row.get("notes"))} - {""})
        existing["notes"] = " ".join(notes)
        if clean(row.get("review_status")) == "accepted_for_fetch" and clean(existing.get("review_status")) != "accepted_for_fetch":
            merged[key] = row
            merged[key]["discovery_method"] = "; ".join(methods)
            merged[key]["notes"] = " ".join(notes)
    return sorted(merged.values(), key=lambda item: (item["school_name"], item["candidate_source_url"]))


def fetch_raw_url(url: str, timeout_seconds: int) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "med-school-ranker-md-official-source-scanner/0.1 (+local research workflow)",
            "Accept": "text/html,application/xhtml+xml,application/xml,text/xml,text/plain;q=0.9,*/*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read()
    except urllib.error.HTTPError:
        return "", ""
    except urllib.error.URLError:
        return "", ""
    except (http.client.HTTPException, OSError):
        return "", ""
    except TimeoutError:
        return "", ""
    return body.decode("utf-8", errors="replace"), response.headers.get("content-type", "")


def origin_for_url(url: str) -> str:
    parsed = urlparse(clean(url))
    if not parsed.scheme or not parsed.netloc:
        return ""
    return urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))


def directory_url(url: str) -> str:
    parsed = urlparse(clean(url))
    if not parsed.scheme or not parsed.netloc:
        return ""
    path = parsed.path
    if not path or path == "/":
        return origin_for_url(url)
    if not path.endswith("/"):
        path = path.rsplit("/", 1)[0] + "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def parent_directory_url(url: str) -> str:
    directory = directory_url(url)
    parsed = urlparse(directory)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) <= 1:
        return origin_for_url(url)
    parent_path = "/" + "/".join(parts[:-1]) + "/"
    return urlunparse((parsed.scheme, parsed.netloc, parent_path, "", "", ""))


def known_path_probe_urls(seed_url: str, max_probe_urls: int) -> list[str]:
    bases = []
    for base in [origin_for_url(seed_url), directory_url(seed_url), parent_directory_url(seed_url)]:
        if base and base not in bases:
            bases.append(base)
    urls: list[str] = []
    seen: set[str] = set()
    for base in bases:
        for suffix in MD_KNOWN_STATS_PATHS:
            url = urljoin(base, suffix)
            if url == clean(seed_url) or url in seen:
                continue
            seen.add(url)
            urls.append(url)
            if max_probe_urls and len(urls) >= max_probe_urls:
                return urls
    return urls


def likely_sitemap_urls(origin: str) -> list[str]:
    return [
        urljoin(origin, "sitemap.xml"),
        urljoin(origin, "sitemap_index.xml"),
        urljoin(origin, "wp-sitemap.xml"),
    ]


def sitemap_urls_from_robots(origin: str, timeout_seconds: int) -> list[str]:
    text, _ = fetch_raw_url(urljoin(origin, "robots.txt"), timeout_seconds)
    urls = []
    for line in text.splitlines():
        if line.lower().startswith("sitemap:"):
            url = clean(line.split(":", 1)[1])
            if url:
                urls.append(url)
    return urls


def parse_sitemap_locs(document: str) -> list[str]:
    urls: list[str] = []
    try:
        root = ET.fromstring(document)
        for element in root.iter():
            if element.tag.lower().endswith("loc") and element.text:
                urls.append(clean(element.text))
    except ET.ParseError:
        urls.extend(clean(match.group("url")) for match in SITEMAP_LOC_RE.finditer(document))
    return [url for url in urls if url]


def discover_sitemap_candidates(
    school: dict[str, str],
    seed_url: str,
    timeout_seconds: int,
    max_sitemap_urls: int,
) -> list[dict[str, str]]:
    origin = origin_for_url(seed_url)
    if not origin:
        return []
    sitemap_urls = []
    for url in sitemap_urls_from_robots(origin, timeout_seconds) + likely_sitemap_urls(origin):
        if url not in sitemap_urls:
            sitemap_urls.append(url)

    locs: list[str] = []
    nested_sitemaps: list[str] = []
    for sitemap_url in sitemap_urls[:12]:
        document, _ = fetch_raw_url(sitemap_url, timeout_seconds)
        if not document:
            continue
        parsed = parse_sitemap_locs(document)
        nested_sitemaps.extend(url for url in parsed if url.lower().split("?", 1)[0].endswith(".xml"))
        locs.extend(url for url in parsed if not url.lower().split("?", 1)[0].endswith(".xml"))
    for sitemap_url in nested_sitemaps[:20]:
        document, _ = fetch_raw_url(sitemap_url, timeout_seconds)
        if document:
            locs.extend(parse_sitemap_locs(document))

    rows = []
    seen: set[str] = set()
    for url in locs:
        if len(rows) >= max_sitemap_urls:
            break
        if url in seen or not same_registrable_domain(seed_url, url):
            continue
        seen.add(url)
        if not is_md_stats_like(url) or not is_md_program_relevant_url(url, seed_url):
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "official_domain_sitemap",
                "Sitemap stats-like URL",
                f"Discovered from sitemap rooted at {origin}.",
                school_website=seed_url,
            )
        )
    return rows


def discover_one_hop_candidates(school: dict[str, str], seed_url: str, timeout_seconds: int) -> list[dict[str, str]]:
    if clean(seed_url).lower().split("?", 1)[0].endswith(".pdf"):
        return []
    fetch_status, title, text, _ = fetch_candidate_text(seed_url, timeout_seconds)
    if fetch_status != "fetched":
        return []

    rows = []
    if is_md_stats_like(seed_url, title, text) and ("mcat" in text.lower() or "gpa" in text.lower()):
        rows.append(
            candidate_row(
                school,
                seed_url,
                "official_page_self_stats_context",
                title,
                "Seed page itself has stats-like context and MCAT/GPA terms.",
                school_website=seed_url,
                candidate_text=text,
            )
        )

    raw_html, content_type = fetch_raw_url(seed_url, timeout_seconds)
    if "html" not in content_type.lower() and "<a " not in raw_html.lower():
        return rows
    parser = LinkParser()
    parser.feed(raw_html)
    seen: set[str] = set()
    for href, link_text in parser.links:
        url = urljoin(seed_url, href)
        if url in seen or not same_registrable_domain(seed_url, url):
            continue
        seen.add(url)
        if not is_md_stats_like(url, link_text) or not is_md_program_relevant_url(url, seed_url, link_text):
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "official_admissions_one_hop_link",
                clean(link_text) or "Stats-like admissions link",
                f"Found as a one-hop link from {seed_url}.",
                school_website=seed_url,
            )
        )
    return rows


def discover_known_path_candidates(
    school: dict[str, str],
    seed_url: str,
    timeout_seconds: int,
    max_probe_urls: int,
) -> list[dict[str, str]]:
    rows = []
    for url in known_path_probe_urls(seed_url, max_probe_urls):
        if not same_registrable_domain(seed_url, url):
            continue
        document, content_type = fetch_raw_url(url, timeout_seconds)
        if not document:
            continue
        if "html" in content_type.lower() or "<html" in document.lower() or "<body" in document.lower():
            title, text = html_to_text(document)
        else:
            title, text = "", clean(document)
        if not is_md_stats_like(url, title, text):
            continue
        if not is_md_program_relevant_url(url, seed_url, title):
            continue
        rows.append(
            candidate_row(
                school,
                url,
                "official_known_path_probe",
                title or "Known class-profile path",
                f"Discovered by probing common public MD class-profile/statistics paths from {seed_url}.",
                school_website=seed_url,
                candidate_text=text,
            )
        )
    return rows


def expand_candidates_with_fetch(
    candidates: list[dict[str, str]],
    schools_by_id: dict[str, dict[str, str]],
    timeout_seconds: int,
    max_sitemap_urls_per_school: int,
    max_hosts: int,
    probe_known_paths: bool = False,
    max_probe_urls_per_host: int = 0,
    skip_sitemap_and_links: bool = False,
) -> list[dict[str, str]]:
    expanded = list(candidates)
    seed_by_school_host: dict[tuple[str, str], dict[str, str]] = {}
    for row in candidates:
        school_id = clean(row.get("school_id"))
        host = clean(row.get("source_host"))
        if school_id and host and (school_id, host) not in seed_by_school_host:
            seed_by_school_host[(school_id, host)] = row

    for index, ((school_id, host), seed) in enumerate(sorted(seed_by_school_host.items()), start=1):
        if max_hosts and index > max_hosts:
            break
        print(f"Discovering MD official candidates from {host} ({index}/{len(seed_by_school_host)})", flush=True)
        school = schools_by_id.get(school_id)
        seed_url = clean(seed.get("candidate_source_url"))
        if not school or not seed_url:
            continue
        if not skip_sitemap_and_links:
            expanded.extend(discover_sitemap_candidates(school, seed_url, timeout_seconds, max_sitemap_urls_per_school))
            if is_md_admissions_like(seed_url, seed.get("candidate_source_title", "")):
                expanded.extend(discover_one_hop_candidates(school, seed_url, timeout_seconds))
        if probe_known_paths:
            expanded.extend(discover_known_path_candidates(school, seed_url, timeout_seconds, max_probe_urls_per_host))
    return merge_candidates(expanded)


def current_stats_by_school() -> dict[str, dict[str, str]]:
    stats = {}
    for row in read_csv(ADMISSIONS_STATS_CSV):
        school_id = clean(row.get("school_id"))
        if school_id and school_id not in stats:
            stats[school_id] = row
    return stats


def build_coverage_rows(schools: list[dict[str, str]], candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    stats = current_stats_by_school()
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in candidates:
        school_id = clean(row.get("school_id"))
        counts[school_id]["candidate"] += 1
        if clean(row.get("review_status")) == "accepted_for_fetch":
            counts[school_id]["official_candidate"] += 1
        if clean(row.get("review_status")) == "official_domain_seed_needs_stats_path":
            counts[school_id]["domain_seed"] += 1
        if clean(row.get("fetch_status")) not in {"", "not_fetched", "not_applicable"}:
            counts[school_id]["fetched"] += 1

    rows = []
    for school in schools:
        school_id = clean(school.get("school_id"))
        stat = stats.get(school_id, {})
        has_mcat = bool(clean(stat.get("published_mcat_average")) or clean(stat.get("mcat_mean_enrolled")) or clean(stat.get("mcat_median_matriculated")))
        has_gpa = bool(clean(stat.get("published_gpa_average")) or clean(stat.get("overall_gpa_mean_enrolled")) or clean(stat.get("overall_gpa_median_matriculated")))
        if counts[school_id]["official_candidate"]:
            status = "official_candidate_ready"
            next_action = "Run med-school-extract-md-official-stats --fetch when network access is available."
        elif counts[school_id]["domain_seed"]:
            status = "official_domain_seed_only"
            next_action = "Use sitemap or one-hop discovery to find a class profile, annual report, fact book, or admissions statistics URL."
        elif counts[school_id]["candidate"]:
            status = "candidate_needs_review"
            next_action = "Review candidate source domain before fetching."
        else:
            status = "missing_candidate"
            next_action = "Find a public official MD class profile, annual report, fact book, or admissions statistics page."
        rows.append(
            {
                "school_id": school_id,
                "school_name": clean(school.get("school_name")),
                "degree_type": "MD",
                "candidate_count": str(counts[school_id]["candidate"]),
                "official_candidate_count": str(counts[school_id]["official_candidate"]),
                "fetched_candidate_count": str(counts[school_id]["fetched"]),
                "accepted_extraction_count": "0",
                "current_canonical_has_mcat": "yes" if has_mcat else "no",
                "current_canonical_has_gpa": "yes" if has_gpa else "no",
                "coverage_status": status,
                "next_action": next_action,
            }
        )
    return rows


def report_rows(schools: list[dict[str, str]], candidates: list[dict[str, str]], fetch: bool) -> list[dict[str, str]]:
    schools_with_candidate = {clean(row.get("school_id")) for row in candidates if clean(row.get("candidate_source_url"))}
    schools_with_ready = {clean(row.get("school_id")) for row in candidates if clean(row.get("review_status")) == "accepted_for_fetch"}
    return [
        {"metric": "active_md_schools", "count": str(len(schools)), "notes": "Active, non-excluded MD rows scanned."},
        {"metric": "candidate_urls", "count": str(len(candidates)), "notes": "Unique MD official candidate URLs."},
        {"metric": "fetch_ready_official_source_urls", "count": str(sum(1 for row in candidates if clean(row.get("review_status")) == "accepted_for_fetch")), "notes": "Official URLs with class/profile/report-like paths."},
        {"metric": "schools_with_any_candidate", "count": str(len(schools_with_candidate)), "notes": "MD schools with at least one candidate URL."},
        {"metric": "schools_with_fetch_ready_candidate", "count": str(len(schools_with_ready)), "notes": "MD schools with at least one candidate ready for extraction."},
        {"metric": "network_discovery_enabled", "count": "1" if fetch else "0", "notes": "When enabled, discovery expands via robots sitemaps, one-hop admissions links, and optional known-path probing."},
    ]


def build_md_official_discovery(
    fetch: bool = False,
    timeout_seconds: int = 10,
    max_sitemap_urls_per_school: int = 40,
    max_hosts: int = 0,
    probe_known_paths: bool = False,
    max_probe_urls_per_host: int = 0,
    reuse_existing_candidates: bool = False,
    skip_sitemap_and_links: bool = False,
) -> list[dict[str, str]]:
    schools = active_md_school_rows()
    schools_by_id = {clean(row.get("school_id")): row for row in schools}
    candidates = merge_candidates(
        rows_from_school_master(schools)
        + rows_from_manual_queue(schools_by_id)
        + rows_from_letter_requirements(schools_by_id)
        + rows_from_cycletrack_lor_requirements(schools_by_id)
        + rows_from_published_source_urls(schools_by_id)
        + rows_from_assisted_search_seeds(schools_by_id)
    )
    if reuse_existing_candidates:
        candidates = merge_candidates(read_csv(MD_OFFICIAL_SOURCE_CANDIDATES_CSV) + candidates)
    if fetch:
        candidates = expand_candidates_with_fetch(
            candidates,
            schools_by_id,
            timeout_seconds,
            max_sitemap_urls_per_school,
            max_hosts,
            probe_known_paths=probe_known_paths,
            max_probe_urls_per_host=max_probe_urls_per_host,
            skip_sitemap_and_links=skip_sitemap_and_links,
        )
    write_csv(MD_OFFICIAL_SOURCE_CANDIDATES_CSV, MD_OFFICIAL_SOURCE_CANDIDATE_COLUMNS, candidates)
    write_csv(MD_OFFICIAL_DISCOVERY_REPORT_CSV, MD_OFFICIAL_DISCOVERY_REPORT_COLUMNS, report_rows(schools, candidates, fetch))
    write_csv(MD_OFFICIAL_COVERAGE_CSV, MD_OFFICIAL_COVERAGE_COLUMNS, build_coverage_rows(schools, candidates))
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover MD official public MCAT/GPA candidate URLs.")
    parser.add_argument("--fetch", action="store_true", help="Fetch official-domain sitemaps and one-hop admissions links. Defaults to local seeds only.")
    parser.add_argument("--timeout-seconds", type=int, default=10)
    parser.add_argument("--max-sitemap-urls-per-school", type=int, default=40)
    parser.add_argument("--max-hosts", type=int, default=0, help="Optional cap on unique school/host pairs visited during --fetch. 0 means no cap.")
    parser.add_argument("--probe-known-paths", action="store_true", help="Probe common official class-profile/statistics paths under each official seed host.")
    parser.add_argument("--max-probe-urls-per-host", type=int, default=0, help="Optional cap on known-path probes per school/host pair. 0 means all known paths.")
    parser.add_argument("--reuse-existing-candidates", action="store_true", help="Merge the existing MD candidate CSV before network expansion.")
    parser.add_argument("--skip-sitemap-and-links", action="store_true", help="During --fetch, skip sitemap and one-hop expansion and only run enabled probe modes.")
    args = parser.parse_args()
    rows = build_md_official_discovery(
        fetch=args.fetch,
        timeout_seconds=args.timeout_seconds,
        max_sitemap_urls_per_school=args.max_sitemap_urls_per_school,
        max_hosts=args.max_hosts,
        probe_known_paths=args.probe_known_paths,
        max_probe_urls_per_host=args.max_probe_urls_per_host,
        reuse_existing_candidates=args.reuse_existing_candidates,
        skip_sitemap_and_links=args.skip_sitemap_and_links,
    )
    print(f"Wrote {MD_OFFICIAL_SOURCE_CANDIDATES_CSV.relative_to(ROOT)} with {len(rows)} MD official candidate URL(s)")


if __name__ == "__main__":
    main()
