from __future__ import annotations

import csv
import re
import unicodedata
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "data" / "raw" / "aamc" / "msar_reports" / "19_msar015-msar-tuition-fees-and-insurance-information.pdf"
SOURCE_DIR = ROOT / "data" / "source_tables"
SUMMARY_DIR = ROOT / "outputs" / "source_diffs"
MASTER_PATH = ROOT / "data" / "school_master.csv"

SOURCE_KEY = "aamc_msar_tuition_fees_insurance"
SOURCE_NAME = "AAMC MSAR Tuition, Fees and Insurance Information"
SOURCE_URL = "https://students-residents.aamc.org/medical-school-admission-requirements/medical-school-admission-requirements-reports-applicants-and-advisors"
PDF_FILE = str(PDF_PATH.relative_to(ROOT))

TUITION_CSV = SOURCE_DIR / "aamc_msar_tuition_fees_insurance.csv"
JOIN_CANDIDATES_CSV = SOURCE_DIR / "aamc_msar_tuition_school_master_join_candidates.csv"
PATCH_CANDIDATES_CSV = SOURCE_DIR / "aamc_msar_tuition_school_master_patch_candidates.csv"
SUMMARY_PATH = SUMMARY_DIR / "aamc_msar_tuition_parse_summary.txt"

CELL_RE = re.compile(
    r"(?:^|[\r\n])q\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"re W n(.*?)[\r\n]+Q",
    re.S,
)
PDF_STRING_RE = re.compile(r"\(((?:\\.|[^\\)])*)\)\s*Tj", re.S)

COLUMN_X = {
    "state": 18.65,
    "school": 46.01,
    "in_state_total_cost_of_attendance": 377.93,
    "in_state_tuition_fees": 442.73,
    "in_state_health_insurance": 507.53,
    "out_state_total_cost_of_attendance": 572.33,
    "out_state_tuition_fees": 637.13,
    "out_state_health_insurance": 701.93,
}
COLUMN_ORDER = list(COLUMN_X)
US_STATE_CODES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "PR",
}
CANADIAN_PROVINCE_CODES = {"AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"}
STATE_NAME_BY_ABBREV = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "PR": "Puerto Rico",
}

TUITION_COLUMNS = [
    "source_key",
    "source_name",
    "source_url",
    "pdf_file",
    "source_row_number",
    "stream_index",
    "row_y",
    "state",
    "school_name_raw",
    "school_name_clean",
    "in_state_total_cost_of_attendance_raw",
    "in_state_total_cost_of_attendance",
    "in_state_tuition_fees_raw",
    "in_state_tuition_fees",
    "in_state_health_insurance_raw",
    "in_state_health_insurance",
    "out_state_total_cost_of_attendance_raw",
    "out_state_total_cost_of_attendance",
    "out_state_tuition_fees_raw",
    "out_state_tuition_fees",
    "out_state_health_insurance_raw",
    "out_state_health_insurance",
    "in_state_tuition_fees_insurance",
    "out_state_tuition_fees_insurance",
    "report_year",
    "academic_year",
    "notes",
]

JOIN_COLUMNS = [
    "aamc_source_row_number",
    "aamc_school_name",
    "aamc_state",
    "master_school_id",
    "master_school_name",
    "master_state_abbrev",
    "master_degree_type",
    "match_score",
    "match_label",
    "second_match_score",
    "second_master_school_id",
    "second_master_school_name",
    "in_state_tuition_fees",
    "out_state_tuition_fees",
    "in_state_health_insurance",
    "out_state_health_insurance",
    "in_state_tuition_fees_insurance",
    "out_state_tuition_fees_insurance",
    "estimated_coa_in_state",
    "estimated_coa_out_state",
    "tuition_source_url",
    "pdf_file",
    "notes",
]

PATCH_COLUMNS = [
    "school_id",
    "school_name",
    "state_abbrev",
    "in_state_tuition_fees_insurance",
    "out_state_tuition_fees_insurance",
    "estimated_coa_in_state",
    "estimated_coa_out_state",
    "tuition_source_url",
    "tuition_source_name",
    "aamc_source_row_number",
    "aamc_school_name",
    "match_score",
    "match_label",
    "notes",
]


@dataclass
class ParsedCell:
    stream_index: int
    x: float
    y: float
    text: str


@dataclass
class TuitionRow:
    source_row_number: int
    stream_index: int
    row_y: float
    state: str
    school_name_raw: str
    in_state_total_cost_of_attendance_raw: str
    in_state_tuition_fees_raw: str
    in_state_health_insurance_raw: str
    out_state_total_cost_of_attendance_raw: str
    out_state_tuition_fees_raw: str
    out_state_health_insurance_raw: str
    report_year: str
    academic_year: str
    notes: str

    def asdict(self) -> dict[str, str | int | float]:
        in_state_tuition_fees = parse_currency(self.in_state_tuition_fees_raw)
        in_state_health_insurance = parse_currency(self.in_state_health_insurance_raw)
        out_state_tuition_fees = parse_currency(self.out_state_tuition_fees_raw)
        out_state_health_insurance = parse_currency(self.out_state_health_insurance_raw)
        return {
            "source_key": SOURCE_KEY,
            "source_name": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "pdf_file": PDF_FILE,
            "source_row_number": self.source_row_number,
            "stream_index": self.stream_index,
            "row_y": f"{self.row_y:.3f}",
            "state": self.state,
            "school_name_raw": self.school_name_raw,
            "school_name_clean": clean_school_name(self.school_name_raw),
            "in_state_total_cost_of_attendance_raw": self.in_state_total_cost_of_attendance_raw,
            "in_state_total_cost_of_attendance": currency_text(parse_currency(self.in_state_total_cost_of_attendance_raw)),
            "in_state_tuition_fees_raw": self.in_state_tuition_fees_raw,
            "in_state_tuition_fees": currency_text(in_state_tuition_fees),
            "in_state_health_insurance_raw": self.in_state_health_insurance_raw,
            "in_state_health_insurance": currency_text(in_state_health_insurance),
            "out_state_total_cost_of_attendance_raw": self.out_state_total_cost_of_attendance_raw,
            "out_state_total_cost_of_attendance": currency_text(parse_currency(self.out_state_total_cost_of_attendance_raw)),
            "out_state_tuition_fees_raw": self.out_state_tuition_fees_raw,
            "out_state_tuition_fees": currency_text(out_state_tuition_fees),
            "out_state_health_insurance_raw": self.out_state_health_insurance_raw,
            "out_state_health_insurance": currency_text(out_state_health_insurance),
            "in_state_tuition_fees_insurance": currency_text(add_optional(in_state_tuition_fees, in_state_health_insurance)),
            "out_state_tuition_fees_insurance": currency_text(add_optional(out_state_tuition_fees, out_state_health_insurance)),
            "report_year": self.report_year,
            "academic_year": self.academic_year,
            "notes": self.notes,
        }


def normalize_space(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    return re.sub(r"\s+", " ", value).strip()


def clean_school_name(value: str) -> str:
    value = normalize_space(value)
    value = re.sub(r"\s*\*\s*$", "", value)
    return normalize_space(value)


def pdf_literal_unescape(value: str) -> str:
    chars: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\":
            chars.append(char)
            index += 1
            continue

        index += 1
        if index >= len(value):
            chars.append("\\")
            break

        escaped = value[index]
        if escaped in "nrtbf":
            chars.append({"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}[escaped])
            index += 1
        elif escaped in "\r\n":
            index += 1
            if escaped == "\r" and index < len(value) and value[index] == "\n":
                index += 1
        elif escaped in "01234567":
            octal = escaped
            index += 1
            while index < len(value) and len(octal) < 3 and value[index] in "01234567":
                octal += value[index]
                index += 1
            chars.append(chr(int(octal, 8)))
        else:
            chars.append(escaped)
            index += 1
    return "".join(chars)


def extract_pdf_strings(block: str) -> list[str]:
    return [pdf_literal_unescape(match.group(1)) for match in PDF_STRING_RE.finditer(block)]


def decompressed_streams(pdf_path: Path) -> list[tuple[int, str]]:
    pdf = pdf_path.read_bytes()
    streams: list[tuple[int, str]] = []
    for stream_index, marker in enumerate(re.finditer(rb"stream\r?\n", pdf)):
        start = marker.end()
        end = pdf.find(b"endstream", start)
        if end < 0:
            continue
        raw_stream = pdf[start:end].rstrip(b"\r\n")
        try:
            stream = zlib.decompress(raw_stream)
        except zlib.error:
            continue
        streams.append((stream_index, stream.decode("latin-1", errors="replace")))
    return streams


def nearest_column(x: float) -> str:
    column, distance = min(
        ((column_name, abs(x - column_x)) for column_name, column_x in COLUMN_X.items()),
        key=lambda item: item[1],
    )
    return column if distance <= 1.0 else ""


def extract_cells(stream_index: int, stream_text: str) -> list[ParsedCell]:
    cells: list[ParsedCell] = []
    for match in CELL_RE.finditer(stream_text):
        x = float(match.group(1))
        y = float(match.group(2))
        column = nearest_column(x)
        if not column:
            continue
        if not 40.0 < y < 530.0:
            continue
        cell_text = normalize_space("".join(extract_pdf_strings(match.group(5))))
        if not cell_text and column == "state":
            continue
        cells.append(ParsedCell(stream_index=stream_index, x=x, y=y, text=cell_text))
    return cells


def table_metadata(streams: list[tuple[int, str]]) -> tuple[str, str]:
    text = "\n".join(extract_pdf_strings(streams[0][1])) if streams else ""
    report_year = ""
    if "MSAR Tuition, Fees and Insurance Information" in text:
        report_year = regex_group(r"\b(20\d{2})\s+MSAR Tuition, Fees and Insurance Information", text)
    academic_year = regex_group(r"Academic Year\s+([0-9-]+)", text)
    return report_year, academic_year


def extract_tuition_rows(streams: list[tuple[int, str]]) -> list[TuitionRow]:
    report_year, academic_year = table_metadata(streams)
    rows: list[TuitionRow] = []
    for stream_index, stream_text in streams:
        cells = extract_cells(stream_index, stream_text)
        rows_by_y: dict[float, dict[str, str]] = {}
        row_y_lookup: dict[float, float] = {}
        for cell in cells:
            column = nearest_column(cell.x)
            if not column:
                continue
            row_key = round(cell.y, 1)
            rows_by_y.setdefault(row_key, {})[column] = cell.text
            row_y_lookup[row_key] = cell.y

        for row_key in sorted(rows_by_y, reverse=True):
            row = rows_by_y[row_key]
            state = normalize_space(row.get("state", ""))
            school = clean_school_name(row.get("school", ""))
            if not is_data_row(state, school, row):
                continue
            notes = data_notes(row)
            rows.append(
                TuitionRow(
                    source_row_number=len(rows) + 1,
                    stream_index=stream_index,
                    row_y=row_y_lookup[row_key],
                    state=state,
                    school_name_raw=school,
                    in_state_total_cost_of_attendance_raw=row.get("in_state_total_cost_of_attendance", ""),
                    in_state_tuition_fees_raw=row.get("in_state_tuition_fees", ""),
                    in_state_health_insurance_raw=row.get("in_state_health_insurance", ""),
                    out_state_total_cost_of_attendance_raw=row.get("out_state_total_cost_of_attendance", ""),
                    out_state_tuition_fees_raw=row.get("out_state_tuition_fees", ""),
                    out_state_health_insurance_raw=row.get("out_state_health_insurance", ""),
                    report_year=report_year,
                    academic_year=academic_year,
                    notes=notes,
                )
            )
    return rows


def is_data_row(state: str, school: str, row: dict[str, str]) -> bool:
    if not state or state in {"USA", "CAN", "State"}:
        return False
    if not school or school == "Medical School":
        return False
    if not re.fullmatch(r"[A-Z]{2,3}", state):
        return False
    return row.get("in_state_total_cost_of_attendance", "").startswith("$")


def data_notes(row: dict[str, str]) -> str:
    money_columns = [
        "in_state_total_cost_of_attendance",
        "in_state_tuition_fees",
        "in_state_health_insurance",
        "out_state_total_cost_of_attendance",
        "out_state_tuition_fees",
        "out_state_health_insurance",
    ]
    parsed = [parse_currency(row.get(column, "")) for column in money_columns]
    notes: list[str] = []
    if all(value == 0 for value in parsed):
        notes.append("all reported cost fields are zero")
    elif all(parse_currency(row.get(column, "")) == 0 for column in money_columns[3:]):
        notes.append("out-of-state reported cost fields are zero")
    if parse_currency(row.get("in_state_total_cost_of_attendance", "")) == 0 and parse_currency(row.get("in_state_tuition_fees", "")) not in {"", 0}:
        notes.append("in-state total cost of attendance is zero but tuition and fees is populated")
    if parse_currency(row.get("out_state_total_cost_of_attendance", "")) == 0 and parse_currency(row.get("out_state_tuition_fees", "")) not in {"", 0}:
        notes.append("out-of-state total cost of attendance is zero but tuition and fees is populated")
    return "; ".join(notes)


def parse_currency(value: str) -> int | None:
    value = normalize_space(value)
    if not value:
        return None
    if not re.fullmatch(r"\$?-?[\d,]+", value):
        return None
    return int(value.replace("$", "").replace(",", ""))


def add_optional(left: int | None, right: int | None) -> int | None:
    if left is None and right is None:
        return None
    return (left or 0) + (right or 0)


def currency_text(value: int | None) -> str:
    return "" if value is None else str(value)


def regex_group(pattern: str, value: str) -> str:
    match = re.search(pattern, value, flags=re.IGNORECASE)
    return normalize_space(match.group(1)) if match else ""


def normalize_for_match(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"\blsu\b", " louisiana state university ", value)
    value = re.sub(r"\bpenn state\b", " pennsylvania state university ", value)
    value = re.sub(r"\btcu\b", " texas christian university ", value)
    value = re.sub(r"\buthealth\b", " university texas health science center ", value)
    value = re.sub(r"\bm\.?\s*d\.?\b", " md ", value)
    value = value.replace("–", " ").replace("—", " ").replace("-", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    replacements = {
        "univ": "university",
        "ut": "university texas",
        "uc": "university california",
        "ucla": "university california los angeles",
        "ucsf": "university california san francisco",
    }
    tokens = [replacements.get(token, token) for token in value.split()]
    return " ".join(" ".join(tokens).split())


STOPWORDS = {
    "a",
    "and",
    "at",
    "college",
    "dr",
    "faculty",
    "for",
    "health",
    "in",
    "jr",
    "md",
    "medical",
    "medicine",
    "of",
    "school",
    "sciences",
    "the",
    "university",
}


def match_tokens(value: str) -> set[str]:
    return {token for token in normalize_for_match(value).split() if token not in STOPWORDS}


def match_score(left: str, right: str) -> float:
    left_clean = normalize_for_match(left)
    right_clean = normalize_for_match(right)
    if not left_clean or not right_clean:
        return 0.0
    if left_clean == right_clean:
        return 1.0
    if left_clean in right_clean or right_clean in left_clean:
        return max(0.94, SequenceMatcher(None, left_clean, right_clean).ratio())

    left_tokens = match_tokens(left)
    right_tokens = match_tokens(right)
    shared = len(left_tokens & right_tokens)
    token_f1 = 0.0 if not left_tokens or not right_tokens else 2 * shared / (len(left_tokens) + len(right_tokens))
    seq_score = SequenceMatcher(None, left_clean, right_clean).ratio()
    if len(left_tokens) >= 2 and left_tokens <= right_tokens:
        return max(0.91, seq_score, token_f1)
    subset_bonus = 0.0
    if left_tokens and right_tokens and (left_tokens <= right_tokens or right_tokens <= left_tokens):
        subset_bonus = 0.06
    distinctive_conflict = bool((left_tokens - right_tokens) and (right_tokens - left_tokens))
    blended_score = max(token_f1 + subset_bonus, 0.65 * token_f1 + 0.35 * seq_score)
    if not distinctive_conflict:
        blended_score = max(blended_score, seq_score)
    return min(1.0, blended_score)


def load_master_rows() -> list[dict[str, str]]:
    with MASTER_PATH.open(newline="") as file:
        return list(csv.DictReader(file))


def best_master_matches(tuition_row: dict[str, str | int | float], master_rows: list[dict[str, str]]) -> list[tuple[float, dict[str, str]]]:
    state = str(tuition_row["state"])
    school_name = str(tuition_row["school_name_clean"])
    candidates = [row for row in master_rows if row.get("degree_type") == "MD"]
    if state in US_STATE_CODES:
        same_state = [row for row in candidates if row.get("state_abbrev") == state]
        if not same_state:
            return []
        candidates = same_state
    else:
        return []

    scored = sorted(
        ((candidate_match_score(school_name, candidate), candidate) for candidate in candidates),
        key=lambda item: (item[0], item[1]["school_name"]),
        reverse=True,
    )
    return scored[:2]


def candidate_match_score(school_name: str, candidate: dict[str, str]) -> float:
    score = match_score(school_name, candidate["school_name"])
    if score >= 0.999:
        return score
    city = normalize_for_match(candidate.get("city", ""))
    if city and re.search(rf"\b{re.escape(city)}\b", normalize_for_match(school_name)):
        boosted = min(1.0, score + 0.25)
        geography_tokens = set(city.split())
        geography_tokens |= set(normalize_for_match(STATE_NAME_BY_ABBREV.get(candidate.get("state_abbrev", ""), "")).split())
        shared_non_geographic_tokens = (match_tokens(school_name) & match_tokens(candidate["school_name"])) - geography_tokens
        score = boosted if shared_non_geographic_tokens else 0.87
    return score


def match_label(score: float, tuition_row: dict[str, str | int | float], master_row: dict[str, str] | None) -> str:
    if master_row is None:
        return "no_match"
    if master_row.get("state_abbrev") != tuition_row.get("state"):
        return "review"
    if normalize_for_match(str(tuition_row["school_name_clean"])) == normalize_for_match(master_row["school_name"]):
        return "exact"
    if score >= 0.88:
        return "high_confidence"
    if score >= 0.72:
        return "review"
    return "no_match"


def join_candidate_rows(tuition_rows: list[dict[str, str | int | float]], master_rows: list[dict[str, str]]) -> list[dict[str, str | int | float]]:
    output: list[dict[str, str | int | float]] = []
    for row in tuition_rows:
        matches = best_master_matches(row, master_rows)
        best_score, best = matches[0] if matches else (0.0, None)
        second_score, second = matches[1] if len(matches) > 1 else (0.0, None)
        label = match_label(best_score, row, best)
        notes = str(row.get("notes", ""))
        if str(row["state"]) in CANADIAN_PROVINCE_CODES:
            notes = append_note(notes, "Canadian/province row; no U.S. master row expected")
        elif str(row["state"]) not in US_STATE_CODES:
            notes = append_note(notes, "non-U.S.-state code; no master row expected")
        elif not best:
            notes = append_note(notes, "no master row with matching state_abbrev")
        elif label == "no_match":
            notes = append_note(notes, "no reliable master match")
        elif label == "review":
            notes = append_note(notes, "review before updating master")

        output.append(
            {
                "aamc_source_row_number": row["source_row_number"],
                "aamc_school_name": row["school_name_clean"],
                "aamc_state": row["state"],
                "master_school_id": best["school_id"] if best else "",
                "master_school_name": best["school_name"] if best else "",
                "master_state_abbrev": best["state_abbrev"] if best else "",
                "master_degree_type": best["degree_type"] if best else "",
                "match_score": f"{best_score:.3f}",
                "match_label": label,
                "second_match_score": f"{second_score:.3f}" if second else "",
                "second_master_school_id": second["school_id"] if second else "",
                "second_master_school_name": second["school_name"] if second else "",
                "in_state_tuition_fees": row["in_state_tuition_fees"],
                "out_state_tuition_fees": row["out_state_tuition_fees"],
                "in_state_health_insurance": row["in_state_health_insurance"],
                "out_state_health_insurance": row["out_state_health_insurance"],
                "in_state_tuition_fees_insurance": row["in_state_tuition_fees_insurance"],
                "out_state_tuition_fees_insurance": row["out_state_tuition_fees_insurance"],
                "estimated_coa_in_state": row["in_state_total_cost_of_attendance"],
                "estimated_coa_out_state": row["out_state_total_cost_of_attendance"],
                "tuition_source_url": SOURCE_URL,
                "pdf_file": PDF_FILE,
                "notes": notes,
            }
        )
    return output


def patch_candidate_rows(join_rows: list[dict[str, str | int | float]]) -> list[dict[str, str | int | float]]:
    safe_labels = {"exact", "high_confidence"}
    safe_counts: dict[str, int] = {}
    for row in join_rows:
        school_id = str(row["master_school_id"])
        if str(row["match_label"]) in safe_labels and school_id:
            safe_counts[school_id] = safe_counts.get(school_id, 0) + 1

    output: list[dict[str, str | int | float]] = []
    for row in join_rows:
        if str(row["match_label"]) not in safe_labels:
            continue
        if safe_counts.get(str(row["master_school_id"]), 0) != 1:
            continue
        output.append(
            {
                "school_id": row["master_school_id"],
                "school_name": row["master_school_name"],
                "state_abbrev": row["master_state_abbrev"],
                "in_state_tuition_fees_insurance": row["in_state_tuition_fees_insurance"],
                "out_state_tuition_fees_insurance": row["out_state_tuition_fees_insurance"],
                "estimated_coa_in_state": row["estimated_coa_in_state"],
                "estimated_coa_out_state": row["estimated_coa_out_state"],
                "tuition_source_url": row["tuition_source_url"],
                "tuition_source_name": SOURCE_NAME,
                "aamc_source_row_number": row["aamc_source_row_number"],
                "aamc_school_name": row["aamc_school_name"],
                "match_score": row["match_score"],
                "match_label": row["match_label"],
                "notes": row["notes"],
            }
        )
    return output


def append_note(existing: str, note: str) -> str:
    return "; ".join(item for item in [existing, note] if item)


def write_csv(path: Path, rows: list[dict[str, str | int | float]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    tuition_rows: list[dict[str, str | int | float]],
    join_rows: list[dict[str, str | int | float]],
    patch_rows: list[dict[str, str | int | float]],
) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    label_counts: dict[str, int] = {}
    for row in join_rows:
        label = str(row["match_label"])
        label_counts[label] = label_counts.get(label, 0) + 1
    us_rows = sum(1 for row in tuition_rows if str(row["state"]) in US_STATE_CODES)
    canada_rows = len(tuition_rows) - us_rows
    zero_rows = [row for row in tuition_rows if "zero" in str(row["notes"])]
    now = datetime.now(timezone.utc).date().isoformat()
    lines = [
        "AAMC MSAR tuition parse summary",
        f"Generated: {now}",
        f"Source: {SOURCE_URL}",
        f"PDF: {PDF_FILE}",
        "",
        f"Parsed tuition rows: {len(tuition_rows)}",
        f"U.S. rows: {us_rows}",
        f"Canadian/province rows: {canada_rows}",
        f"Rows with zero-field notes: {len(zero_rows)}",
        "",
        "Master join labels:",
    ]
    for label in sorted(label_counts):
        lines.append(f"- {label}: {label_counts[label]}")
    lines.extend(
        [
            "",
            f"Safe patch candidate rows: {len(patch_rows)}",
            "",
            "Outputs:",
            f"- {TUITION_CSV.relative_to(ROOT)}",
            f"- {JOIN_CANDIDATES_CSV.relative_to(ROOT)}",
            f"- {PATCH_CANDIDATES_CSV.relative_to(ROOT)}",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    streams = decompressed_streams(PDF_PATH)
    tuition_rows = [row.asdict() for row in extract_tuition_rows(streams)]
    master_rows = load_master_rows()
    join_rows = join_candidate_rows(tuition_rows, master_rows)
    patch_rows = patch_candidate_rows(join_rows)

    write_csv(TUITION_CSV, tuition_rows, TUITION_COLUMNS)
    write_csv(JOIN_CANDIDATES_CSV, join_rows, JOIN_COLUMNS)
    write_csv(PATCH_CANDIDATES_CSV, patch_rows, PATCH_COLUMNS)
    write_summary(tuition_rows, join_rows, patch_rows)

    print(f"Parsed tuition rows: {len(tuition_rows)}")
    print(f"Join candidates: {len(join_rows)}")
    print(f"Safe patch candidates: {len(patch_rows)}")
    print(f"Wrote {TUITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {JOIN_CANDIDATES_CSV.relative_to(ROOT)}")
    print(f"Wrote {PATCH_CANDIDATES_CSV.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
