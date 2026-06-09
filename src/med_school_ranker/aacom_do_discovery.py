from __future__ import annotations

import argparse
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from med_school_ranker.aacom_do_rules import (
    AACOM_COVERAGE_COLUMNS,
    AACOM_PROFILE_CANDIDATE_COLUMNS,
    AacomProfileCard,
    AacomProfileMatch,
    best_profile_match,
    clean,
    compact_text,
    is_aacom_profile_url,
    is_truthy,
    parse_aacom_profile_cards,
    read_csv,
    today_iso,
    write_csv,
)
from med_school_ranker.paths import (
    AACOM_DO_PROFILE_CANDIDATES_CSV,
    AACOM_DO_PROFILE_COVERAGE_CSV,
    ADMISSIONS_STATS_CSV,
    MASTER_CSV,
    ROOT,
)


AACOM_DISCOVERY_SEED_URLS = [
    "https://www.aacom.org/sitemap.xml",
    "https://www.aacom.org/sitemap_index.xml",
    "https://www.aacom.org/wp-sitemap.xml",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=0&rowsPerPage=12",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=12&rowsPerPage=12",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=24&rowsPerPage=12",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=36&rowsPerPage=12",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=48&rowsPerPage=12",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=60&rowsPerPage=12",
    "https://www.aacom.org/explore-med-schools/choose-do-explorer?startRow=72&rowsPerPage=12",
    "https://www.aacom.org/searches/reports/report/US-osteopathic-medical-schools-dashboard",
]


def active_do_schools() -> list[dict[str, str]]:
    schools = []
    for row in read_csv(MASTER_CSV):
        if clean(row.get("degree_type")).upper() != "DO":
            continue
        if row.get("active_in_universe") and not is_truthy(row.get("active_in_universe")):
            continue
        if is_truthy(row.get("manual_exclusion_flag")):
            continue
        schools.append(row)
    return schools


def current_stats_by_school() -> dict[str, dict[str, str]]:
    stats = {}
    for row in read_csv(ADMISSIONS_STATS_CSV):
        school_id = clean(row.get("school_id"))
        if school_id and school_id not in stats:
            stats[school_id] = row
    return stats


def fetch_text(url: str, timeout_seconds: int) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "med-school-ranker-aacom-do-scanner/0.1 (+local research workflow)",
            "Accept": "text/html,application/xhtml+xml,text/xml,text/plain;q=0.9,*/*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        return "", f"fetch_failed_http_{exc.code}"
    except urllib.error.URLError as exc:
        return "", f"fetch_failed_url_error:{exc.reason}"
    except TimeoutError:
        return "", "fetch_failed_timeout"
    return body.decode("utf-8", errors="replace"), "fetched"


def profiles_from_url_list(path: Path) -> list[AacomProfileCard]:
    profiles = []
    for line in path.read_text().splitlines():
        text = clean(line)
        if not text or text.startswith("#"):
            continue
        if is_aacom_profile_url(text):
            profiles.append(AacomProfileCard(url=text))
    return sorted({profile.url: profile for profile in profiles}.values(), key=lambda profile: profile.url)


def merge_profile(profiles: dict[str, AacomProfileCard], profile: AacomProfileCard) -> None:
    existing = profiles.get(profile.url)
    if not existing:
        profiles[profile.url] = profile
        return
    if profile.title and profile.city and profile.state_abbrev:
        profiles[profile.url] = profile


def discover_profiles(
    fetch: bool,
    timeout_seconds: int,
    url_list: Path | None = None,
) -> tuple[list[AacomProfileCard], list[str]]:
    profiles: dict[str, AacomProfileCard] = {}
    notes = []
    if url_list:
        list_profiles = profiles_from_url_list(url_list)
        for profile in list_profiles:
            merge_profile(profiles, profile)
        notes.append(f"url_list:{len(list_profiles)}")
    if not fetch:
        return sorted(profiles.values(), key=lambda profile: profile.url), notes
    for seed_url in AACOM_DISCOVERY_SEED_URLS:
        text, status = fetch_text(seed_url, timeout_seconds)
        notes.append(f"{seed_url}:{status}")
        if status != "fetched":
            continue
        for profile in parse_aacom_profile_cards(text, seed_url):
            merge_profile(profiles, profile)
    return sorted(profiles.values(), key=lambda profile: profile.url), notes


def candidate_row(profile: AacomProfileCard, match: AacomProfileMatch, discovery_method: str) -> dict[str, str]:
    school = match.school or {}
    title = compact_text(profile.title or profile.url.rsplit("/", 1)[-1].replace("-", " ").title())
    fetch_status = "not_fetched" if match.status in {"safe_match", "review_match"} else "not_applicable"
    review_status = "accepted_for_fetch" if match.status == "safe_match" else "needs_review"
    return {
        "school_id": clean(school.get("school_id")),
        "school_name": clean(school.get("school_name")),
        "degree_type": clean(school.get("degree_type") or "DO"),
        "campus_name": clean(school.get("campus_name")),
        "state_abbrev": clean(school.get("state_abbrev")),
        "school_website": clean(school.get("website")),
        "aacom_profile_url": profile.url,
        "aacom_profile_title": title,
        "aacom_city": clean(profile.city),
        "aacom_state_abbrev": clean(profile.state_abbrev),
        "aacom_slug": profile.url.rstrip("/").rsplit("/", 1)[-1],
        "match_status": match.status,
        "match_score": f"{match.score:.2f}",
        "match_reason": match.reason,
        "discovery_method": discovery_method,
        "source_last_checked": today_iso(),
        "fetch_status": fetch_status,
        "review_status": review_status,
        "notes": f"second_match_score={match.second_score:.2f}",
    }


def build_coverage_rows(
    schools: list[dict[str, str]],
    candidates: list[dict[str, str]],
) -> list[dict[str, str]]:
    stats = current_stats_by_school()
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

    rows = []
    for school in schools:
        school_id = clean(school.get("school_id"))
        stat = stats.get(school_id, {})
        has_mcat = bool(clean(stat.get("published_mcat_average")) or clean(stat.get("mcat_mean_enrolled")) or clean(stat.get("mcat_median_matriculated")))
        has_gpa = bool(clean(stat.get("published_gpa_average")) or clean(stat.get("overall_gpa_mean_enrolled")) or clean(stat.get("overall_gpa_median_matriculated")))
        if counts[school_id]["matched"]:
            coverage_status = "aacom_profile_candidate_ready"
            next_action = "Run med-school-extract-aacom-do-stats --fetch when network access is available."
        elif counts[school_id]["candidate"]:
            coverage_status = "aacom_profile_needs_review"
            next_action = "Review AACOM profile match before fetching."
        else:
            coverage_status = "missing_aacom_profile_candidate"
            next_action = "Run discovery with --fetch or provide a URL list of AACOM /detail-pages/com/ profile URLs."
        rows.append(
            {
                "school_id": school_id,
                "school_name": clean(school.get("school_name")),
                "degree_type": clean(school.get("degree_type")),
                "candidate_count": str(counts[school_id]["candidate"]),
                "matched_candidate_count": str(counts[school_id]["matched"]),
                "fetched_candidate_count": str(counts[school_id]["fetched"]),
                "accepted_extraction_count": "0",
                "current_canonical_has_mcat": "yes" if has_mcat else "no",
                "current_canonical_has_gpa": "yes" if has_gpa else "no",
                "coverage_status": coverage_status,
                "next_action": next_action,
            }
        )
    return rows


def build_aacom_do_discovery(
    fetch: bool = False,
    timeout_seconds: int = 15,
    url_list: Path | None = None,
) -> list[dict[str, str]]:
    schools = active_do_schools()
    profiles, discovery_notes = discover_profiles(fetch, timeout_seconds, url_list)
    rows = [
        candidate_row(
            profile,
            best_profile_match(profile.url, profile.title, schools, profile.city, profile.state_abbrev),
            "; ".join(["aacom_profile_url_list" if url_list else "", "aacom_seed_fetch" if fetch else "no_network"]).strip("; "),
        )
        for profile in profiles
    ]
    rows = sorted(rows, key=lambda row: (row["school_name"], row["aacom_profile_url"]))
    if discovery_notes and rows:
        rows[0]["notes"] = "; ".join([rows[0].get("notes", ""), f"discovery_notes={' | '.join(discovery_notes)}"]).strip("; ")
    write_csv(AACOM_DO_PROFILE_CANDIDATES_CSV, AACOM_PROFILE_CANDIDATE_COLUMNS, rows)
    write_csv(AACOM_DO_PROFILE_COVERAGE_CSV, AACOM_COVERAGE_COLUMNS, build_coverage_rows(schools, rows))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover deterministic AACOM DO profile URLs.")
    parser.add_argument("--fetch", action="store_true", help="Fetch AACOM seed pages over the network. Defaults to no-network deterministic mode.")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--url-list", type=Path, default=None, help="Optional local newline-delimited AACOM profile URL list.")
    args = parser.parse_args()
    rows = build_aacom_do_discovery(fetch=args.fetch, timeout_seconds=args.timeout_seconds, url_list=args.url_list)
    print(f"Wrote {AACOM_DO_PROFILE_CANDIDATES_CSV.relative_to(ROOT)} with {len(rows)} AACOM candidate profile(s)")


if __name__ == "__main__":
    main()
