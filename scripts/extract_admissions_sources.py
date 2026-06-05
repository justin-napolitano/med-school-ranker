from __future__ import annotations

import csv
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_tables"
DIFF_DIR = ROOT / "outputs" / "source_diffs"

TODAY_UTC = datetime.now(timezone.utc).date().isoformat()

SOURCES = {
    "prospectivedoctor": {
        "name": "ProspectiveDoctor",
        "url": "https://www.prospectivedoctor.com/gpa-and-mcat/",
        "used_for": "Published medical school average GPA, MCAT, minimum MCAT, and row-level source links where provided.",
    },
    "shemmassian": {
        "name": "Shemmassian",
        "url": "https://www.shemmassianconsulting.com/blog/average-gpa-and-mcat-score-for-every-medical-school",
        "used_for": "Published medical school average GPA, average MCAT, minimum MCAT, state, and degree type.",
    },
    "matchguy": {
        "name": "The Match Guy",
        "url": "https://thematchguy.com/average-mcat-gpa-medical-school-acceptance/",
        "used_for": "Published medical school average GPA and average MCAT.",
    },
    "cycletrack_lors": {
        "name": "CycleTrack Letters of Recommendation",
        "url": "https://cycletrack.org/lors",
        "used_for": "MD, MD-PhD, DO, and Canadian MD letter-of-recommendation requirement links by school.",
    },
    "cycletrack_explorer": {
        "name": "CycleTrack School Explorer",
        "url": "https://cycletrack.org/explorer",
        "used_for": "Crowdsourced school index and per-school median cGPA, sGPA, and MCAT for interviews and acceptances.",
    },
}

SOURCE_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "source_row_number",
    "school_name_raw",
    "school_name_clean",
    "school_source_url",
    "state",
    "degree_type",
    "average_gpa_raw",
    "average_gpa",
    "average_mcat_raw",
    "average_mcat",
    "minimum_mcat_raw",
    "minimum_mcat",
    "notes",
]

COMPARABLE_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "value_url",
    "source_row_number",
    "school_name_raw",
    "school_name_clean",
    "metric_context",
    "gpa",
    "mcat",
    "notes",
]

EXPLORER_SCHOOL_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "source_row_number",
    "explorer_slug",
    "explorer_url",
    "school_name_raw",
    "school_name_clean",
    "search_text",
    "school_type",
    "city",
    "state",
    "country",
    "setting",
    "institution_type",
    "applications_tracked",
    "combined_degree_applications_tracked",
    "notes",
]

EXPLORER_STATS_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "explorer_slug",
    "explorer_url",
    "school_name_raw",
    "school_name_clean",
    "school_type",
    "state",
    "country",
    "program_type",
    "outcome",
    "metric_context",
    "total_tracked",
    "percent_applicants_interviewed",
    "percent_applicants_interviewed_n",
    "percent_accepted_post_interview",
    "percent_accepted_post_interview_n",
    "percent_accepted_from_waitlist",
    "percent_accepted_from_waitlist_n",
    "median_cgpa_raw",
    "median_cgpa",
    "cgpa_min",
    "cgpa_max",
    "cgpa_n",
    "median_sgpa_raw",
    "median_sgpa",
    "sgpa_min",
    "sgpa_max",
    "sgpa_n",
    "median_mcat_raw",
    "median_mcat",
    "mcat_min",
    "mcat_max",
    "mcat_n",
    "notes",
]

LOR_REQUIREMENT_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "source_row_number",
    "category",
    "school_name_raw",
    "school_name_clean",
    "md_requirements_url",
    "md_phd_requirements_url",
    "do_requirements_url",
    "missing_md_requirements",
    "missing_md_phd_requirements",
    "missing_do_requirements",
    "notes",
]

LOR_LINK_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "source_row_number",
    "category",
    "school_name_raw",
    "school_name_clean",
    "requirement_type",
    "link_text",
    "requirement_url_raw",
    "requirement_url",
    "is_missing_placeholder",
    "placeholder_title",
    "notes",
]

SOURCE_UNIVERSE_COLUMNS = [
    "source_name",
    "url",
    "used_for",
    "source_page_updated_or_info_as_of",
    "source_last_checked",
    "notes",
]


@dataclass
class CellLink:
    text: str
    href: str
    title: str


@dataclass
class RichCell:
    text: str
    links: list[CellLink]


@dataclass
class SourceRow:
    source_key: str
    source_name: str
    source_url: str
    source_row_number: int
    school_name_raw: str
    school_name_clean: str
    school_source_url: str
    state: str
    degree_type: str
    average_gpa_raw: str
    average_gpa: str
    average_mcat_raw: str
    average_mcat: str
    minimum_mcat_raw: str
    minimum_mcat: str
    notes: str

    def asdict(self) -> dict[str, str | int]:
        return {
            "source_key": self.source_key,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "source_row_number": self.source_row_number,
            "school_name_raw": self.school_name_raw,
            "school_name_clean": self.school_name_clean,
            "school_source_url": self.school_source_url,
            "state": self.state,
            "degree_type": self.degree_type,
            "average_gpa_raw": self.average_gpa_raw,
            "average_gpa": self.average_gpa,
            "average_mcat_raw": self.average_mcat_raw,
            "average_mcat": self.average_mcat,
            "minimum_mcat_raw": self.minimum_mcat_raw,
            "minimum_mcat": self.minimum_mcat,
            "notes": self.notes,
        }


@dataclass
class ComparableRow:
    source_key: str
    source_name: str
    source_url: str
    value_url: str
    source_row_number: int
    school_name_raw: str
    school_name_clean: str
    metric_context: str
    gpa: str
    mcat: str
    notes: str

    def asdict(self) -> dict[str, str | int]:
        return {
            "source_key": self.source_key,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "value_url": self.value_url,
            "source_row_number": self.source_row_number,
            "school_name_raw": self.school_name_raw,
            "school_name_clean": self.school_name_clean,
            "metric_context": self.metric_context,
            "gpa": self.gpa,
            "mcat": self.mcat,
            "notes": self.notes,
        }


class RichTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[RichCell]]] = []
        self._table_depth = 0
        self._current_table: list[list[RichCell]] | None = None
        self._current_row: list[RichCell] | None = None
        self._current_cell_text: list[str] | None = None
        self._current_cell_links: list[CellLink] | None = None
        self._current_link_href = ""
        self._current_link_title = ""
        self._current_link_text: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._current_table = []
        elif tag == "tr" and self._table_depth == 1:
            self._current_row = []
        elif tag in {"td", "th"} and self._table_depth == 1 and self._current_row is not None:
            self._current_cell_text = []
            self._current_cell_links = []
        elif tag == "a" and self._current_cell_text is not None:
            self._current_link_href = normalize_space(attrs_dict.get("href", ""))
            self._current_link_title = normalize_space(attrs_dict.get("title", ""))
            self._current_link_text = []
        elif tag == "br" and self._current_cell_text is not None:
            self._current_cell_text.append("\n")
            if self._current_link_text is not None:
                self._current_link_text.append("\n")

    def handle_data(self, data: str) -> None:
        if self._current_cell_text is None:
            return
        self._current_cell_text.append(data)
        if self._current_link_text is not None:
            self._current_link_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "a" and self._current_link_text is not None and self._current_cell_links is not None:
            self._current_cell_links.append(
                CellLink(
                    text=normalize_space("".join(self._current_link_text)),
                    href=self._current_link_href,
                    title=self._current_link_title,
                )
            )
            self._current_link_href = ""
            self._current_link_title = ""
            self._current_link_text = None
        elif tag in {"td", "th"} and self._current_cell_text is not None:
            if self._current_row is not None:
                self._current_row.append(
                    RichCell(
                        text=normalize_space("".join(self._current_cell_text)),
                        links=self._current_cell_links or [],
                    )
                )
            self._current_cell_text = None
            self._current_cell_links = None
            self._current_link_text = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_table is not None:
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._table_depth:
            if self._table_depth == 1 and self._current_table is not None:
                self.tables.append(self._current_table)
                self._current_table = None
            self._table_depth -= 1


class ExplorerListParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, str | int]] = []
        self._current: dict[str, str | int] | None = None
        self._entry_depth = 0
        self._capture_strong = False
        self._capture_center = False
        self._name_parts: list[str] = []
        self._center_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        class_value = attrs_dict.get("class", "")
        if tag == "div" and self._current is None and "school_entry" in class_value.split():
            self._current = {
                "search_text": normalize_space(attrs_dict.get("id", "")),
                "state": class_token_value(class_value, "state"),
                "country": class_token_value(class_value, "country"),
                "school_type": class_token_value(class_value, "school_type"),
            }
            self._entry_depth = 1
            self._name_parts = []
            self._center_parts = []
            return
        if self._current is None:
            return
        if tag == "div":
            self._entry_depth += 1
        elif tag == "a" and not self._current.get("explorer_url"):
            href = normalize_space(attrs_dict.get("href", ""))
            if href.startswith("/explorer/school/"):
                self._current["explorer_url"] = urllib.parse.urljoin(SOURCES["cycletrack_explorer"]["url"], href)
                self._current["explorer_slug"] = urllib.parse.unquote(href.rsplit("/", 1)[-1])
        elif tag == "strong":
            self._capture_strong = True
        elif tag == "center":
            self._capture_center = True
        elif tag == "br" and self._capture_center:
            self._center_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._current is None:
            return
        if self._capture_strong:
            self._name_parts.append(data)
        if self._capture_center:
            self._center_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._current is None:
            return
        if tag == "strong":
            self._capture_strong = False
        elif tag == "center":
            self._capture_center = False
        elif tag == "div":
            self._entry_depth -= 1
            if self._entry_depth == 0:
                self._finish_current()

    def _finish_current(self) -> None:
        assert self._current is not None
        school_name = normalize_space("".join(self._name_parts))
        center_lines = [
            normalize_space(line)
            for line in "".join(self._center_parts).splitlines()
            if normalize_space(line)
        ]
        detail_line = next((line for line in center_lines if "|" in line), "")
        tracked_line = next((line for line in center_lines if "Applications Tracked" in line), "")
        city = ""
        setting = ""
        institution_type = ""
        degree_type = str(self._current.get("school_type", ""))
        if detail_line:
            parts = [normalize_space(part) for part in detail_line.split("|")]
            city_state = parts[0] if parts else ""
            if "," in city_state:
                city = normalize_space(city_state.rsplit(",", 1)[0])
            if len(parts) > 1:
                setting = parts[1]
            if len(parts) > 2:
                institution_type = parts[2]
            if len(parts) > 3:
                degree_type = parts[3]
        apps = regex_group(r"([\d,]+)\s+Applications Tracked", tracked_line)
        combined_apps = regex_group(r"\(([\d,]+)\s+(?:MD-PhD|DO-PhD)\)", tracked_line)

        self._current.update(
            {
                "source_key": "cycletrack_explorer",
                "source_name": SOURCES["cycletrack_explorer"]["name"],
                "source_url": SOURCES["cycletrack_explorer"]["url"],
                "source_row_number": len(self.rows) + 1,
                "school_name_raw": school_name,
                "school_name_clean": clean_school_name(school_name),
                "city": city,
                "setting": setting,
                "institution_type": institution_type,
                "school_type": normalize_space(degree_type),
                "applications_tracked": number_text(apps),
                "combined_degree_applications_tracked": number_text(combined_apps),
                "notes": "",
            }
        )
        self.rows.append(dict(self._current))
        self._current = None
        self._capture_strong = False
        self._capture_center = False
        self._name_parts = []
        self._center_parts = []


def normalize_space(value: str) -> str:
    value = unescape(value).replace("\xa0", " ")
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_school_name(value: str) -> str:
    value = normalize_space(value)
    value = re.sub(r"\s*\*\s*$", "", value)
    value = re.sub(r"\s+Note:.*$", "", value, flags=re.IGNORECASE)
    return normalize_space(value)


def safe_request_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/:%")
    query = urllib.parse.quote(parts.query, safe="=&%/:?+")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def fetch_html(url: str, retries: int = 2) -> str:
    safe_url = safe_request_url(url)
    request = urllib.request.Request(
        safe_url,
        headers={
            "User-Agent": "Mozilla/5.0 med-school-ranker deterministic source extractor",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as error:  # noqa: BLE001 - surface exact URL in caller summaries.
            last_error = error
            if attempt < retries:
                time.sleep(0.25 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def parse_rich_tables(html: str) -> list[list[list[RichCell]]]:
    parser = RichTableParser()
    parser.feed(html)
    return parser.tables


def rich_table_with_header(tables: list[list[list[RichCell]]], required: Iterable[str]) -> list[list[RichCell]]:
    required_lower = [item.lower() for item in required]
    for table in tables:
        if not table:
            continue
        header = " | ".join(cell.text for cell in table[0]).lower()
        if all(item in header for item in required_lower):
            return table
    raise ValueError(f"Could not find table with required header pieces: {required_lower}")


def parse_float(value: str, low: float | None = None, high: float | None = None) -> str:
    value = normalize_space(value)
    if not value or value.upper() in {"NR", "N/A"}:
        return ""
    numbers = re.findall(r"(?<!\d)(?:\d+\.\d+|\d+)(?!\d)", value.replace(",", ""))
    for number in numbers:
        parsed = float(number)
        if low is not None and parsed < low:
            continue
        if high is not None and parsed > high:
            continue
        return strip_float(parsed)
    return ""


def parse_gpa(value: str) -> str:
    average_match = re.search(r"Average\s*-\s*(\d+(?:\.\d+)?)", normalize_space(value), flags=re.IGNORECASE)
    if average_match:
        return strip_float(float(average_match.group(1)))
    return parse_float(value)


def parse_mcat(value: str) -> str:
    average_match = re.search(r"MCAT\s+Average\s*-\s*(\d+(?:\.\d+)?)", normalize_space(value), flags=re.IGNORECASE)
    if average_match:
        return strip_float(float(average_match.group(1)))
    return parse_float(value, low=472, high=528)


def parse_min_mcat(value: str) -> str:
    minimum_match = re.search(r"MCAT\s+Minimum\s*-\s*(\d+(?:\.\d+)?)", normalize_space(value), flags=re.IGNORECASE)
    if minimum_match:
        return strip_float(float(minimum_match.group(1)))
    return parse_float(value, low=472, high=528)


def strip_float(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def number_text(value: str) -> str:
    return normalize_space(value).replace(",", "")


def is_valid_gpa(value: str) -> bool:
    return not value or 0 < float(value) <= 4.3


def is_valid_mcat(value: str) -> bool:
    return not value or 472 <= float(value) <= 528


def notes_for(gpa: str, mcat: str, raw_name: str) -> str:
    notes: list[str] = []
    if gpa and not is_valid_gpa(gpa):
        notes.append("parsed GPA outside expected range")
    if mcat and not is_valid_mcat(mcat):
        notes.append("parsed MCAT outside expected range")
    if "*" in raw_name:
        notes.append("source row carried an asterisk")
    return "; ".join(notes)


def normalize_href(href: str, base_url: str) -> str:
    href = normalize_space(href)
    if not href or href in {"#", "None", "none", "NULL", "null"}:
        return ""
    return urllib.parse.urljoin(base_url, href)


def first_link(cell: RichCell, base_url: str) -> tuple[str, str, str]:
    if not cell.links:
        return "", "", ""
    link = cell.links[0]
    return link.text, link.href, normalize_href(link.href, base_url)


def extract_prospectivedoctor(html: str) -> list[SourceRow]:
    source = SOURCES["prospectivedoctor"]
    table = rich_table_with_header(parse_rich_tables(html), ["US MEDICAL SCHOOLS", "AVERAGE GPA", "MCAT"])
    rows: list[SourceRow] = []
    current_state = ""
    for index, cells in enumerate(table[1:], start=2):
        if len(cells) < 3:
            continue
        school_raw, gpa_raw, mcat_raw = cells[0].text, cells[1].text, cells[2].text
        if not school_raw or "Find Out Your Chances" in school_raw:
            continue
        if school_raw.isupper() and not gpa_raw and not mcat_raw:
            current_state = school_raw.title()
            continue
        if not re.search(r"\d", gpa_raw + mcat_raw):
            continue
        school = clean_school_name(school_raw)
        gpa = parse_gpa(gpa_raw)
        mcat = parse_mcat(mcat_raw)
        school_url = normalize_href(cells[0].links[0].href, source["url"]) if cells[0].links else ""
        rows.append(
            SourceRow(
                source_key="prospectivedoctor",
                source_name=source["name"],
                source_url=source["url"],
                source_row_number=index,
                school_name_raw=school_raw,
                school_name_clean=school,
                school_source_url=school_url,
                state=current_state,
                degree_type="",
                average_gpa_raw=gpa_raw,
                average_gpa=gpa,
                average_mcat_raw=mcat_raw,
                average_mcat=mcat,
                minimum_mcat_raw=mcat_raw,
                minimum_mcat=parse_min_mcat(mcat_raw),
                notes=notes_for(gpa, mcat, school_raw),
            )
        )
    return rows


def extract_shemmassian(html: str) -> list[SourceRow]:
    source = SOURCES["shemmassian"]
    table = rich_table_with_header(parse_rich_tables(html), ["Medical School", "State", "Average GPA", "Average MCAT"])
    rows: list[SourceRow] = []
    for index, cells in enumerate(table[1:], start=2):
        if len(cells) < 6:
            continue
        school_raw, state, degree_type, gpa_raw, mcat_raw, min_mcat_raw = [cell.text for cell in cells[:6]]
        if not school_raw or school_raw.lower() == "medical school":
            continue
        school = clean_school_name(school_raw)
        gpa = parse_gpa(gpa_raw)
        mcat = parse_mcat(mcat_raw)
        rows.append(
            SourceRow(
                source_key="shemmassian",
                source_name=source["name"],
                source_url=source["url"],
                source_row_number=index,
                school_name_raw=school_raw,
                school_name_clean=school,
                school_source_url="",
                state=state,
                degree_type=degree_type,
                average_gpa_raw=gpa_raw,
                average_gpa=gpa,
                average_mcat_raw=mcat_raw,
                average_mcat=mcat,
                minimum_mcat_raw=min_mcat_raw,
                minimum_mcat=parse_min_mcat(min_mcat_raw),
                notes=notes_for(gpa, mcat, school_raw),
            )
        )
    return rows


def extract_matchguy(html: str) -> list[SourceRow]:
    source = SOURCES["matchguy"]
    table = rich_table_with_header(parse_rich_tables(html), ["School Name", "Average GPA", "Average MCAT"])
    rows: list[SourceRow] = []
    for index, cells in enumerate(table[1:], start=2):
        if len(cells) < 3:
            continue
        school_raw, gpa_raw, mcat_raw = [cell.text for cell in cells[:3]]
        if not school_raw or school_raw.lower() == "school name":
            continue
        school = clean_school_name(school_raw)
        gpa = parse_gpa(gpa_raw)
        mcat = parse_mcat(mcat_raw)
        rows.append(
            SourceRow(
                source_key="matchguy",
                source_name=source["name"],
                source_url=source["url"],
                source_row_number=index,
                school_name_raw=school_raw,
                school_name_clean=school,
                school_source_url="",
                state="",
                degree_type="",
                average_gpa_raw=gpa_raw,
                average_gpa=gpa,
                average_mcat_raw=mcat_raw,
                average_mcat=mcat,
                minimum_mcat_raw="",
                minimum_mcat="",
                notes=notes_for(gpa, mcat, school_raw),
            )
        )
    return rows


def extract_cycletrack_lors(html: str) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
    school_rows: list[dict[str, str | int]] = []
    link_rows: list[dict[str, str | int]] = []
    tabs = [
        ("md", "USA MD", ["MD", "MD-PhD"]),
        ("do", "DO", ["DO"]),
        ("ca", "CAN MD", ["MD", "MD-PhD"]),
    ]
    source = SOURCES["cycletrack_lors"]

    for tab_id, category, requirement_types in tabs:
        segment = tab_segment(html, tab_id)
        table = parse_rich_tables(segment)[0] if segment else []
        for row_index, cells in enumerate(table, start=1):
            if len(cells) < 2:
                continue
            school_raw = cells[0].text
            if not school_raw:
                continue
            school = clean_school_name(school_raw)
            row_links: dict[str, str] = {"MD": "", "MD-PhD": "", "DO": ""}
            row_missing: dict[str, str] = {"MD": "", "MD-PhD": "", "DO": ""}
            row_notes: list[str] = []
            for offset, requirement_type in enumerate(requirement_types, start=1):
                cell = cells[offset] if len(cells) > offset else RichCell("", [])
                link_text, href_raw, href = first_link(cell, source["url"])
                missing = not href
                if missing and not cell.text:
                    row_notes.append(f"{requirement_type} requirement cell blank")
                elif missing:
                    row_notes.append(f"{requirement_type} requirement link missing or placeholder")
                row_links[requirement_type] = href
                row_missing[requirement_type] = "TRUE" if missing else "FALSE"
                link_rows.append(
                    {
                        "source_key": "cycletrack_lors",
                        "source_name": source["name"],
                        "source_url": source["url"],
                        "source_row_number": row_index,
                        "category": category,
                        "school_name_raw": school_raw,
                        "school_name_clean": school,
                        "requirement_type": requirement_type,
                        "link_text": link_text or cell.text,
                        "requirement_url_raw": href_raw,
                        "requirement_url": href,
                        "is_missing_placeholder": "TRUE" if missing else "FALSE",
                        "placeholder_title": cell.links[0].title if cell.links else "",
                        "notes": "; ".join(row_notes),
                    }
                )

            school_rows.append(
                {
                    "source_key": "cycletrack_lors",
                    "source_name": source["name"],
                    "source_url": source["url"],
                    "source_row_number": row_index,
                    "category": category,
                    "school_name_raw": school_raw,
                    "school_name_clean": school,
                    "md_requirements_url": row_links["MD"],
                    "md_phd_requirements_url": row_links["MD-PhD"],
                    "do_requirements_url": row_links["DO"],
                    "missing_md_requirements": row_missing["MD"],
                    "missing_md_phd_requirements": row_missing["MD-PhD"],
                    "missing_do_requirements": row_missing["DO"],
                    "notes": "; ".join(dict.fromkeys(row_notes)),
                }
            )
    return school_rows, link_rows


def tab_segment(html: str, tab_id: str) -> str:
    start_match = re.search(
        rf"<div\b[^>]*\bid=[\"']{re.escape(tab_id)}[\"'][^>]*>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not start_match:
        return ""
    table_end = re.search(r"</table>", html[start_match.start() :], flags=re.IGNORECASE)
    if not table_end:
        return ""
    end = start_match.start() + table_end.end()
    return html[start_match.start() : end]


def extract_explorer_school_index(html: str) -> list[dict[str, str | int]]:
    parser = ExplorerListParser()
    parser.feed(html)
    return parser.rows


def class_token_value(class_value: str, prefix: str) -> str:
    for token in class_value.split():
        if token.startswith(prefix + "_"):
            return token[len(prefix) + 1 :]
    return ""


def html_to_lines(html: str) -> list[str]:
    text = re.sub(r"<script\b.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(?:h[1-6]|p|div|li|tr|td)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    lines = [normalize_space(line) for line in unescape(text).splitlines()]
    return [line for line in lines if line]


def extract_explorer_stats(school: dict[str, str | int], html: str) -> list[dict[str, str | int]]:
    lines = html_to_lines(html)
    sections: list[tuple[str, list[str]]] = []
    current_header = ""
    current_lines: list[str] = []
    for line in lines:
        if re.fullmatch(r"(?:MD|DO|MD-PhD|DO-PhD) (?:Interviews|Acceptances)", line):
            if current_header:
                sections.append((current_header, current_lines))
            current_header = line
            current_lines = []
        elif current_header:
            current_lines.append(line)
    if current_header:
        sections.append((current_header, current_lines))

    rows: list[dict[str, str | int]] = []
    for header, section in sections:
        header_match = re.fullmatch(r"(MD|DO|MD-PhD|DO-PhD) (Interviews|Acceptances)", header)
        if not header_match:
            continue
        program_type = header_match.group(1)
        outcome = header_match.group(2).lower()
        cgpa_raw = metric_value(section, "Median cGPA (Range)")
        sgpa_raw = metric_value(section, "Median sGPA (Range)")
        mcat_raw = metric_value(section, "Median MCAT (Range)")
        cgpa = parse_median_range(cgpa_raw)
        sgpa = parse_median_range(sgpa_raw)
        mcat = parse_median_range(mcat_raw)
        total_label = "Total Interviews Tracked" if outcome == "interviews" else "Total Acceptances Tracked"
        notes = []
        for label, raw in (("cGPA", cgpa_raw), ("sGPA", sgpa_raw), ("MCAT", mcat_raw)):
            if raw and "X" in raw:
                notes.append(f"{label} suppressed by CycleTrack for small n")
        rows.append(
            {
                "source_key": "cycletrack_explorer",
                "source_name": SOURCES["cycletrack_explorer"]["name"],
                "source_url": SOURCES["cycletrack_explorer"]["url"],
                "explorer_slug": school.get("explorer_slug", ""),
                "explorer_url": school.get("explorer_url", ""),
                "school_name_raw": school.get("school_name_raw", ""),
                "school_name_clean": school.get("school_name_clean", ""),
                "school_type": school.get("school_type", ""),
                "state": school.get("state", ""),
                "country": school.get("country", ""),
                "program_type": program_type,
                "outcome": outcome,
                "metric_context": f"CycleTrack crowdsourced {program_type} {outcome} median stats",
                "total_tracked": integer_metric(metric_value(section, total_label)),
                "percent_applicants_interviewed": parse_percent(metric_value(section, "Percent Applicants Interviewed"))[0],
                "percent_applicants_interviewed_n": parse_percent(metric_value(section, "Percent Applicants Interviewed"))[1],
                "percent_accepted_post_interview": parse_percent(metric_value(section, "Percent Accepted Post-Interview"))[0],
                "percent_accepted_post_interview_n": parse_percent(metric_value(section, "Percent Accepted Post-Interview"))[1],
                "percent_accepted_from_waitlist": parse_percent(metric_value(section, "Percent Accepted From Waitlist"))[0],
                "percent_accepted_from_waitlist_n": parse_percent(metric_value(section, "Percent Accepted From Waitlist"))[1],
                "median_cgpa_raw": cgpa_raw,
                "median_cgpa": cgpa["median"],
                "cgpa_min": cgpa["min"],
                "cgpa_max": cgpa["max"],
                "cgpa_n": cgpa["n"],
                "median_sgpa_raw": sgpa_raw,
                "median_sgpa": sgpa["median"],
                "sgpa_min": sgpa["min"],
                "sgpa_max": sgpa["max"],
                "sgpa_n": sgpa["n"],
                "median_mcat_raw": mcat_raw,
                "median_mcat": mcat["median"],
                "mcat_min": mcat["min"],
                "mcat_max": mcat["max"],
                "mcat_n": mcat["n"],
                "notes": "; ".join(notes),
            }
        )
    return rows


def metric_value(section_lines: list[str], label: str) -> str:
    for index, line in enumerate(section_lines):
        if not line.startswith(label):
            continue
        after_colon = line.split(":", 1)[1].strip() if ":" in line else ""
        if after_colon:
            return after_colon
        for next_line in section_lines[index + 1 :]:
            if next_line:
                return next_line
    return ""


def integer_metric(value: str) -> str:
    value = normalize_space(value)
    match = re.search(r"[\d,]+", value)
    return number_text(match.group(0)) if match else ""


def parse_percent(value: str) -> tuple[str, str]:
    value = normalize_space(value)
    if not value or "X" in value:
        return "", ""
    percent = regex_group(r"(\d+(?:\.\d+)?)%", value)
    n = regex_group(r"\(n=([\d,]+)\)", value)
    return percent, number_text(n)


def parse_median_range(value: str) -> dict[str, str]:
    value = normalize_space(value)
    output = {"median": "", "min": "", "max": "", "n": ""}
    if not value or "X" in value:
        return output
    match = re.search(
        r"(?P<median>\d+(?:\.\d+)?)\s*\((?P<min>\d+(?:\.\d+)?)\s*-\s*(?P<max>\d+(?:\.\d+)?)\),?\s*\(n=(?P<n>[\d,]+)\)",
        value,
    )
    if not match:
        return output
    output["median"] = strip_float(float(match.group("median")))
    output["min"] = strip_float(float(match.group("min")))
    output["max"] = strip_float(float(match.group("max")))
    output["n"] = number_text(match.group("n"))
    return output


def regex_group(pattern: str, value: str, default: str = "") -> str:
    match = re.search(pattern, value)
    return match.group(1) if match else default


def source_rows_to_comparable(rows: Iterable[SourceRow]) -> list[ComparableRow]:
    output: list[ComparableRow] = []
    for row in rows:
        notes = [row.notes] if row.notes else []
        gpa = row.average_gpa
        mcat = row.average_mcat
        if gpa and not is_valid_gpa(gpa):
            notes.append(f"excluded invalid GPA from comparison math: {gpa}")
            gpa = ""
        if mcat and not is_valid_mcat(mcat):
            notes.append(f"excluded invalid MCAT from comparison math: {mcat}")
            mcat = ""
        output.append(
            ComparableRow(
                source_key=row.source_key,
                source_name=row.source_name,
                source_url=row.source_url,
                value_url=row.school_source_url,
                source_row_number=row.source_row_number,
                school_name_raw=row.school_name_raw,
                school_name_clean=row.school_name_clean,
                metric_context="published school average GPA and MCAT",
                gpa=gpa,
                mcat=mcat,
                notes="; ".join(notes),
            )
        )
    return output


def explorer_stats_to_comparable(rows: Iterable[dict[str, str | int]]) -> list[ComparableRow]:
    output: list[ComparableRow] = []
    for index, row in enumerate(rows, start=1):
        if row.get("outcome") != "acceptances":
            continue
        program_type = str(row.get("program_type", ""))
        if program_type not in {"MD", "DO"}:
            continue
        gpa = str(row.get("median_cgpa", ""))
        mcat = str(row.get("median_mcat", ""))
        if not gpa and not mcat:
            continue
        output.append(
            ComparableRow(
                source_key="cycletrack_acceptance_median",
                source_name="CycleTrack Explorer acceptance medians",
                source_url=SOURCES["cycletrack_explorer"]["url"],
                value_url=str(row.get("explorer_url", "")),
                source_row_number=index,
                school_name_raw=str(row.get("school_name_raw", "")),
                school_name_clean=str(row.get("school_name_clean", "")),
                metric_context=f"CycleTrack crowdsourced {program_type} acceptance median cGPA and MCAT",
                gpa=gpa,
                mcat=mcat,
                notes="Not an official entering-class average; CycleTrack is crowdsourced applicant/outcome data.",
            )
        )
    return output


def match_clean_name(value: str) -> str:
    value = clean_school_name(value).lower()
    replacements = {
        "&": " and ",
        "sch": "school",
        "med": "medicine",
        "univ": "university",
        "college of osteopathic medicine": "osteopathic medicine",
        "school of osteopathic medicine": "osteopathic medicine",
        "college of medicine": "medicine",
        "school of medicine": "medicine",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return normalize_space(value)


STOPWORDS = {
    "a",
    "and",
    "at",
    "college",
    "health",
    "in",
    "medical",
    "medicine",
    "of",
    "school",
    "science",
    "sciences",
    "the",
    "university",
}


def distinctive_tokens(value: str) -> set[str]:
    return {token for token in match_clean_name(value).split() if token not in STOPWORDS}


def match_score(left: str, right: str) -> float:
    left_clean = match_clean_name(left)
    right_clean = match_clean_name(right)
    if left_clean == right_clean:
        return 1.0
    left_tokens = distinctive_tokens(left)
    right_tokens = distinctive_tokens(right)
    shared = len(left_tokens & right_tokens)
    token_score = 0.0 if not left_tokens or not right_tokens else 2 * shared / (len(left_tokens) + len(right_tokens))
    seq_score = SequenceMatcher(None, left_clean, right_clean).ratio()
    return max(token_score, seq_score)


def should_match(left: str, right: str) -> bool:
    left_tokens = distinctive_tokens(left)
    right_tokens = distinctive_tokens(right)
    shared = len(left_tokens & right_tokens)
    score = match_score(left, right)
    if match_clean_name(left) == match_clean_name(right):
        return True
    if score >= 0.92 and shared >= 1:
        return True
    if score >= 0.86 and shared >= 2:
        return True
    if score >= 0.88 and shared >= 1 and min(len(left_tokens), len(right_tokens)) <= 1:
        return True
    return False


def choose_representative(rows: list[ComparableRow]) -> str:
    for preferred_source in ("shemmassian", "prospectivedoctor", "matchguy", "cycletrack_acceptance_median"):
        for row in rows:
            if row.source_key == preferred_source:
                return row.school_name_clean
    return min((row.school_name_clean for row in rows), key=len)


def cluster_comparable_rows(rows: list[ComparableRow]) -> list[list[ComparableRow]]:
    clusters: list[list[ComparableRow]] = []
    representatives: list[str] = []
    for row in rows:
        best_index: int | None = None
        best_score = 0.0
        for index, representative in enumerate(representatives):
            if not should_match(row.school_name_clean, representative):
                continue
            score = match_score(row.school_name_clean, representative)
            if score > best_score:
                best_index = index
                best_score = score
        if best_index is None:
            clusters.append([row])
            representatives.append(row.school_name_clean)
        else:
            clusters[best_index].append(row)
            representatives[best_index] = choose_representative(clusters[best_index])
    return clusters


def numeric_values(rows: Iterable[ComparableRow], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = getattr(row, field)
        if value:
            values.append(float(value))
    return values


def range_text(values: list[float]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return strip_float(values[0])
    return f"{strip_float(min(values))} - {strip_float(max(values))}"


def conflict_label(gpa_values: list[float], mcat_values: list[float], source_count: int) -> str:
    if source_count == 1:
        return "single_source"
    gpa_range = max(gpa_values) - min(gpa_values) if len(gpa_values) > 1 else 0
    mcat_range = max(mcat_values) - min(mcat_values) if len(mcat_values) > 1 else 0
    if gpa_range > 0.10 or mcat_range > 2:
        return "major_conflict"
    if gpa_range > 0.05 or mcat_range > 1:
        return "minor_conflict"
    return "close_agreement"


def row_join(rows: list[ComparableRow], source_key: str, field: str) -> str:
    values = [str(getattr(row, field)) for row in rows if row.source_key == source_key and str(getattr(row, field))]
    return "; ".join(dict.fromkeys(values))


def comparison_rows(rows: list[ComparableRow]) -> tuple[list[dict[str, str | int]], list[str]]:
    source_order = ["prospectivedoctor", "shemmassian", "matchguy", "cycletrack_acceptance_median"]
    fields = [
        "cluster_id",
        "canonical_school_name",
        "sources_present",
        "source_count",
        "agreement_label",
        "gpa_values",
        "gpa_range",
        "gpa_spread",
        "mcat_values",
        "mcat_range",
        "mcat_spread",
        "metric_definition_note",
    ]
    for source_key in source_order:
        fields.extend(
            [
                f"{source_key}_school_name",
                f"{source_key}_metric_context",
                f"{source_key}_gpa",
                f"{source_key}_mcat",
                f"{source_key}_value_url",
                f"{source_key}_notes",
            ]
        )

    output: list[dict[str, str | int]] = []
    clusters = cluster_comparable_rows(rows)
    for cluster_id, cluster in enumerate(sorted(clusters, key=lambda item: choose_representative(item)), start=1):
        sources_present = sorted({row.source_key for row in cluster})
        gpa_values = numeric_values(cluster, "gpa")
        mcat_values = numeric_values(cluster, "mcat")
        row: dict[str, str | int] = {
            "cluster_id": cluster_id,
            "canonical_school_name": choose_representative(cluster),
            "sources_present": ";".join(sources_present),
            "source_count": len(sources_present),
            "agreement_label": conflict_label(gpa_values, mcat_values, len(sources_present)),
            "gpa_values": ";".join(strip_float(value) for value in gpa_values),
            "gpa_range": range_text(gpa_values),
            "gpa_spread": strip_float(max(gpa_values) - min(gpa_values)) if len(gpa_values) > 1 else "",
            "mcat_values": ";".join(strip_float(value) for value in mcat_values),
            "mcat_range": range_text(mcat_values),
            "mcat_spread": strip_float(max(mcat_values) - min(mcat_values)) if len(mcat_values) > 1 else "",
            "metric_definition_note": "Published source rows are school averages; CycleTrack rows are crowdsourced acceptance medians.",
        }
        for source_key in source_order:
            row[f"{source_key}_school_name"] = row_join(cluster, source_key, "school_name_clean")
            row[f"{source_key}_metric_context"] = row_join(cluster, source_key, "metric_context")
            row[f"{source_key}_gpa"] = row_join(cluster, source_key, "gpa")
            row[f"{source_key}_mcat"] = row_join(cluster, source_key, "mcat")
            row[f"{source_key}_value_url"] = row_join(cluster, source_key, "value_url")
            row[f"{source_key}_notes"] = row_join(cluster, source_key, "notes")
        output.append(row)
    return output, fields


def write_csv(path: Path, rows: list[dict[str, str | int]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_source_csv(path: Path, rows: list[SourceRow]) -> None:
    write_csv(path, [row.asdict() for row in rows], SOURCE_COLUMNS)


def write_comparable_csv(path: Path, rows: list[ComparableRow]) -> None:
    write_csv(path, [row.asdict() for row in rows], COMPARABLE_COLUMNS)


def source_universe_rows() -> list[dict[str, str]]:
    return [
        {
            "source_name": source["name"],
            "url": source["url"],
            "used_for": source["used_for"],
            "source_page_updated_or_info_as_of": "",
            "source_last_checked": TODAY_UTC,
            "notes": "Generated by scripts/extract_admissions_sources.py; review before appending to data/sources.csv.",
        }
        for source in SOURCES.values()
    ]


def write_summary(
    path: Path,
    source_rows: dict[str, list[SourceRow]],
    explorer_schools: list[dict[str, str | int]],
    explorer_stats: list[dict[str, str | int]],
    lor_rows: list[dict[str, str | int]],
    lor_links: list[dict[str, str | int]],
    comparisons: list[dict[str, str | int]],
    failed_explorer_pages: list[str],
) -> None:
    label_counts: dict[str, int] = {}
    for row in comparisons:
        label = str(row["agreement_label"])
        label_counts[label] = label_counts.get(label, 0) + 1

    actual_lor_links = [row for row in lor_links if row["requirement_url"]]
    lines = [
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "Published MCAT/GPA source row counts:",
    ]
    for source_key, rows in source_rows.items():
        lines.append(f"- {SOURCES[source_key]['name']}: {len(rows)}")
    lines.extend(
        [
            "",
            "CycleTrack row counts:",
            f"- Explorer school cards: {len(explorer_schools)}",
            f"- Explorer stats rows: {len(explorer_stats)}",
            f"- LOR school rows: {len(lor_rows)}",
            f"- LOR link rows: {len(lor_links)}",
            f"- LOR rows with actual requirement URL: {len(actual_lor_links)}",
            "",
            f"Matched GPA/MCAT comparison clusters: {len(comparisons)}",
            "Agreement labels:",
        ]
    )
    for label in sorted(label_counts):
        lines.append(f"- {label}: {label_counts[label]}")
    lines.extend(
        [
            "",
            "Conflict thresholds:",
            "- close_agreement: all available values within 0.05 GPA and 1 MCAT point",
            "- minor_conflict: GPA spread > 0.05 or MCAT spread > 1",
            "- major_conflict: GPA spread > 0.10 or MCAT spread > 2",
            "",
            "Metric definition note:",
            "- Published source rows are school averages.",
            "- CycleTrack Explorer rows are crowdsourced acceptance medians and are not official entering-class averages.",
        ]
    )
    if failed_explorer_pages:
        lines.extend(["", "Failed CycleTrack Explorer detail pages:"])
        lines.extend(f"- {item}" for item in failed_explorer_pages)
    lines.extend(["", "Source URLs:"])
    for source in SOURCES.values():
        lines.append(f"- {source['name']}: {source['url']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    DIFF_DIR.mkdir(parents=True, exist_ok=True)

    html_by_source = {
        "prospectivedoctor": fetch_html(SOURCES["prospectivedoctor"]["url"]),
        "shemmassian": fetch_html(SOURCES["shemmassian"]["url"]),
        "matchguy": fetch_html(SOURCES["matchguy"]["url"]),
        "cycletrack_lors": fetch_html(SOURCES["cycletrack_lors"]["url"]),
        "cycletrack_explorer": fetch_html(SOURCES["cycletrack_explorer"]["url"]),
    }

    source_rows = {
        "prospectivedoctor": extract_prospectivedoctor(html_by_source["prospectivedoctor"]),
        "shemmassian": extract_shemmassian(html_by_source["shemmassian"]),
        "matchguy": extract_matchguy(html_by_source["matchguy"]),
    }
    for source_key, rows in source_rows.items():
        write_source_csv(SOURCE_DIR / f"{source_key}_mcat_gpa.csv", rows)

    published_rows = [row for rows in source_rows.values() for row in rows]
    write_source_csv(SOURCE_DIR / "all_published_mcat_gpa_sources.csv", published_rows)

    lor_rows, lor_links = extract_cycletrack_lors(html_by_source["cycletrack_lors"])
    write_csv(SOURCE_DIR / "cycletrack_lor_requirements.csv", lor_rows, LOR_REQUIREMENT_COLUMNS)
    write_csv(SOURCE_DIR / "cycletrack_lor_links.csv", lor_links, LOR_LINK_COLUMNS)

    explorer_schools = extract_explorer_school_index(html_by_source["cycletrack_explorer"])
    write_csv(SOURCE_DIR / "cycletrack_explorer_school_index.csv", explorer_schools, EXPLORER_SCHOOL_COLUMNS)

    explorer_stats: list[dict[str, str | int]] = []
    failed_explorer_pages: list[str] = []
    for school in explorer_schools:
        explorer_url = str(school.get("explorer_url", ""))
        if not explorer_url:
            failed_explorer_pages.append(f"{school.get('school_name_clean', '')}: missing explorer URL")
            continue
        try:
            detail_html = fetch_html(explorer_url)
            explorer_stats.extend(extract_explorer_stats(school, detail_html))
        except Exception as error:  # noqa: BLE001 - keep the run useful while recording exact failures.
            failed_explorer_pages.append(f"{school.get('school_name_clean', '')}: {error}")
    write_csv(SOURCE_DIR / "cycletrack_explorer_stats.csv", explorer_stats, EXPLORER_STATS_COLUMNS)

    comparable_rows = source_rows_to_comparable(published_rows) + explorer_stats_to_comparable(explorer_stats)
    write_comparable_csv(SOURCE_DIR / "all_comparable_mcat_gpa_sources.csv", comparable_rows)

    comparisons, comparison_fields = comparison_rows(comparable_rows)
    write_csv(DIFF_DIR / "mcat_gpa_source_comparison.csv", comparisons, comparison_fields)
    conflicts = [row for row in comparisons if str(row["agreement_label"]).endswith("conflict")]
    write_csv(DIFF_DIR / "mcat_gpa_conflicts.csv", conflicts, comparison_fields)
    write_csv(SOURCE_DIR / "source_universe_additions.csv", source_universe_rows(), SOURCE_UNIVERSE_COLUMNS)
    write_summary(
        DIFF_DIR / "mcat_gpa_source_summary.txt",
        source_rows,
        explorer_schools,
        explorer_stats,
        lor_rows,
        lor_links,
        comparisons,
        failed_explorer_pages,
    )

    print(f"Wrote {SOURCE_DIR.relative_to(ROOT)} and {DIFF_DIR.relative_to(ROOT)}")
    for source_key, rows in source_rows.items():
        print(f"{SOURCES[source_key]['name']}: {len(rows)} published rows")
    print(f"CycleTrack Explorer schools: {len(explorer_schools)}")
    print(f"CycleTrack Explorer stats rows: {len(explorer_stats)}")
    print(f"CycleTrack LOR school rows: {len(lor_rows)}")
    print(f"CycleTrack LOR link rows: {len(lor_links)}")
    print(f"Comparison clusters: {len(comparisons)}")
    print(f"Conflicts: {len(conflicts)}")
    print(f"Failed CycleTrack detail pages: {len(failed_explorer_pages)}")


if __name__ == "__main__":
    main()
