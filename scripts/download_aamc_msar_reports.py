from __future__ import annotations

import csv
import hashlib
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import Message
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "aamc" / "msar_reports"
SOURCE_DIR = ROOT / "data" / "source_tables"
SUMMARY_DIR = ROOT / "outputs" / "source_diffs"

ROOT_URL = "https://students-residents.aamc.org/medical-school-admission-requirements/medical-school-admission-requirements-reports-applicants-and-advisors"
SOURCE_NAME = "AAMC MSAR Advisor Reports"
SOURCE_KEY = "aamc_msar_advisor_reports"

METADATA_COLUMNS = [
    "source_key",
    "source_name",
    "root_url",
    "source_row_number",
    "link_text",
    "link_title",
    "href_raw",
    "download_url",
    "final_url",
    "local_path",
    "file_name",
    "content_type",
    "content_length_bytes",
    "sha256",
    "is_pdf",
    "status",
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
class Link:
    text: str
    title: str
    href_raw: str
    download_url: str
    data_entity_type: str
    data_entity_substitution: str
    data_entity_uuid: str


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[Link] = []
        self._attrs: dict[str, str] | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._attrs = {key.lower(): value or "" for key, value in attrs}
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._attrs is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._attrs is None:
            return
        href_raw = normalize_space(self._attrs.get("href", ""))
        text = normalize_space("".join(self._text))
        title = normalize_space(self._attrs.get("title", ""))
        data_entity_substitution = normalize_space(self._attrs.get("data-entity-substitution", ""))
        data_entity_type = normalize_space(self._attrs.get("data-entity-type", ""))
        data_entity_uuid = normalize_space(self._attrs.get("data-entity-uuid", ""))
        download_url = urllib.parse.urljoin(ROOT_URL, href_raw)
        if is_report_download_link(href_raw, data_entity_substitution):
            self.links.append(
                Link(
                    text=text,
                    title=title,
                    href_raw=href_raw,
                    download_url=download_url,
                    data_entity_type=data_entity_type,
                    data_entity_substitution=data_entity_substitution,
                    data_entity_uuid=data_entity_uuid,
                )
            )
        self._attrs = None
        self._text = []


def normalize_space(value: str) -> str:
    value = unescape(value).replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def is_report_download_link(href: str, data_entity_substitution: str) -> bool:
    href_lower = href.lower()
    if ".pdf" in href_lower:
        return True
    if data_entity_substitution == "media_download":
        return True
    parsed = urllib.parse.urlsplit(href_lower)
    return bool(re.search(r"/media/\d+/download", parsed.path))


def fetch_bytes(url: str) -> tuple[bytes, str, Message]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 med-school-ranker AAMC report downloader",
            "Accept": "application/pdf,text/html,application/octet-stream,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
        final_url = response.geturl()
        headers = response.headers
    return body, final_url, headers


def fetch_text(url: str) -> str:
    body, _, _ = fetch_bytes(url)
    return body.decode("utf-8", errors="replace")


def parse_links(html: str) -> list[Link]:
    parser = LinkParser()
    parser.feed(html)
    deduped: dict[str, Link] = {}
    for link in parser.links:
        deduped[link.download_url] = link
    return list(deduped.values())


def slugify(value: str) -> str:
    value = normalize_space(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "aamc-msar-report"


def content_disposition_filename(headers: Message) -> str:
    disposition = headers.get("Content-Disposition", "")
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', disposition, flags=re.IGNORECASE)
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1).strip())


def file_extension(final_url: str, headers: Message, body: bytes) -> str:
    path = urllib.parse.urlsplit(final_url).path
    suffix = Path(path).suffix.lower()
    content_type = headers.get_content_type().lower()
    if content_type == "application/pdf" or body.startswith(b"%PDF"):
        return suffix or ".pdf"
    if content_type == "text/html":
        return ".html"
    if suffix:
        return suffix
    return ".bin"


def local_filename(index: int, link: Link, final_url: str, headers: Message, body: bytes) -> str:
    header_name = content_disposition_filename(headers)
    if header_name:
        base = slugify(Path(header_name).stem)
        suffix = Path(header_name).suffix.lower() or file_extension(final_url, headers, body)
    else:
        base = slugify(link.title or link.text)
        suffix = file_extension(final_url, headers, body)
    return f"{index:02d}_{base}{suffix}"


def non_pdf_note(body: bytes) -> str:
    text = body[:5000].decode("utf-8", errors="ignore")
    if "Client Challenge" in text or "_fs-ch-" in text:
        return "downloaded response was an AAMC/Fastly client challenge, not a PDF"
    return "downloaded response was not identified as a PDF"


def write_csv(path: Path, rows: list[dict[str, str | int]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def source_universe_rows() -> list[dict[str, str]]:
    today = datetime.now(timezone.utc).date().isoformat()
    return [
        {
            "source_name": SOURCE_NAME,
            "url": ROOT_URL,
            "used_for": "Root page for public AAMC MSAR Advisor Report PDF downloads and report metadata.",
            "source_page_updated_or_info_as_of": "2027 Entering Class",
            "source_last_checked": today,
            "notes": "Downloaded by scripts/download_aamc_msar_reports.py; AAMC page states reports are updated and republished regularly.",
        }
    ]


def write_summary(path: Path, rows: list[dict[str, str | int]]) -> None:
    total = len(rows)
    downloaded = sum(1 for row in rows if row["status"] == "downloaded")
    pdfs = sum(1 for row in rows if row["is_pdf"] == "TRUE")
    total_bytes = sum(int(row["content_length_bytes"] or 0) for row in rows)
    lines = [
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Root URL: {ROOT_URL}",
        "",
        f"Report links discovered: {total}",
        f"Downloaded files: {downloaded}",
        f"Verified PDF responses: {pdfs}",
        f"Total bytes: {total_bytes}",
        "",
        "Downloaded file names:",
    ]
    for row in rows:
        lines.append(f"- {row['file_name']} | {row['link_text'] or row['link_title']} | {row['status']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    for path in RAW_DIR.iterdir():
        if path.is_file():
            path.unlink()

    html = fetch_text(ROOT_URL)
    (RAW_DIR / "root_page.html").write_text(html)
    links = parse_links(html)

    rows: list[dict[str, str | int]] = []
    for index, link in enumerate(links, start=1):
        row: dict[str, str | int] = {
            "source_key": SOURCE_KEY,
            "source_name": SOURCE_NAME,
            "root_url": ROOT_URL,
            "source_row_number": index,
            "link_text": link.text,
            "link_title": link.title,
            "href_raw": link.href_raw,
            "download_url": link.download_url,
            "final_url": "",
            "local_path": "",
            "file_name": "",
            "content_type": "",
            "content_length_bytes": "",
            "sha256": "",
            "is_pdf": "FALSE",
            "status": "",
            "notes": "",
        }
        try:
            body, final_url, headers = fetch_bytes(link.download_url)
            name = local_filename(index, link, final_url, headers, body)
            path = RAW_DIR / name
            path.write_bytes(body)
            content_type = headers.get_content_type()
            is_pdf = content_type.lower() == "application/pdf" or body.startswith(b"%PDF")
            row.update(
                {
                    "final_url": final_url,
                    "local_path": str(path.relative_to(ROOT)),
                    "file_name": name,
                    "content_type": content_type,
                    "content_length_bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "is_pdf": "TRUE" if is_pdf else "FALSE",
                    "status": "downloaded" if is_pdf else "non_pdf_response",
                    "notes": "" if is_pdf else non_pdf_note(body),
                }
            )
        except Exception as error:  # noqa: BLE001 - keep all link rows and record exact failure.
            row.update({"status": "failed", "notes": str(error)})
        rows.append(row)

    write_csv(SOURCE_DIR / "aamc_msar_report_pdfs.csv", rows, METADATA_COLUMNS)
    write_csv(SOURCE_DIR / "source_universe_aamc_msar_reports.csv", source_universe_rows(), SOURCE_UNIVERSE_COLUMNS)
    write_summary(SUMMARY_DIR / "aamc_msar_report_pdfs_summary.txt", rows)

    print(f"Report links discovered: {len(rows)}")
    print(f"Downloaded files: {sum(1 for row in rows if row['status'] == 'downloaded')}")
    print(f"Verified PDFs: {sum(1 for row in rows if row['is_pdf'] == 'TRUE')}")
    print(f"Wrote {SOURCE_DIR / 'aamc_msar_report_pdfs.csv'}")
    print(f"Wrote {RAW_DIR}")


if __name__ == "__main__":
    main()
