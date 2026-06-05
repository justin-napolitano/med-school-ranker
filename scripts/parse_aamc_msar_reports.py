from __future__ import annotations

import csv
import re
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "aamc" / "msar_reports"
SOURCE_DIR = ROOT / "data" / "source_tables"
SUMMARY_DIR = ROOT / "outputs" / "source_diffs"

SOURCE_URL = "https://students-residents.aamc.org/medical-school-admission-requirements/medical-school-admission-requirements-reports-applicants-and-advisors"
SOURCE_NAME = "AAMC MSAR Advisor Reports"

CELL_RE = re.compile(
    r"(?:^|[\r\n])q\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"(-?\d+(?:\.\d+)?)\s+"
    r"re\s+W\*?\s+n(.*?)(?:[\r\n]+Q|[\r\n]+EMC\s*[\r\n]+Q)",
    re.S,
)
BT_RE = re.compile(r"BT(.*?)ET", re.S)
LITERAL_RE = re.compile(r"\(((?:\\.|[^\\)])*)\)")
HEX_RE = re.compile(r"<([0-9A-Fa-f]+)>")
TD_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+Td")

BASE_COLUMNS = [
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
]

STATE_OR_PROVINCE_RE = re.compile(r"^[A-Z]{2,3}$")


@dataclass
class Cell:
    stream_index: int
    x: float
    y: float
    w: float
    h: float
    text: str

    @property
    def top(self) -> float:
        return self.y + self.h

    @property
    def bottom(self) -> float:
        return self.y


@dataclass
class SchoolRow:
    source_row_number: int
    stream_index: int
    row_y: float
    row_bottom: float
    row_top: float
    state: str
    school_name: str
    cells: list[Cell]


@dataclass(frozen=True)
class ReportConfig:
    key: str
    pdf_name: str
    output_name: str
    state_x: float | None
    school_x: float
    parser: str
    columns: tuple[tuple[str, float], ...] = ()
    label_xs: tuple[float, ...] = ()
    value_xs: tuple[float, ...] = ()
    label_map: tuple[tuple[str, str], ...] = ()
    address_x: float | None = None
    notes: str = ""


REPORTS = [
    ReportConfig(
        key="aamc_msar_main_campus_contact",
        pdf_name="01_msar023-msar-medical-school-main-campus-address-and-contact-information.pdf",
        output_name="aamc_msar_main_campus_contact.csv",
        state_x=18.65,
        school_x=46.01,
        parser="contact",
        label_xs=(258.41,),
        value_xs=(300.24,),
        address_x=258.41,
    ),
    ReportConfig(
        key="aamc_msar_mission_statement",
        pdf_name="02_msar007-msar-mission-statement.pdf",
        output_name="aamc_msar_mission_statements.csv",
        state_x=18.61,
        school_x=45.97,
        parser="simple",
        columns=(("mission_statement", 263.07),),
    ),
    ReportConfig(
        key="aamc_msar_gender_sexual_minority_support",
        pdf_name="04_msar016-msar-support-systems-for-gender-and-sexual-minority-students.pdf",
        output_name="aamc_msar_gender_sexual_minority_support.csv",
        state_x=18.65,
        school_x=46.01,
        parser="simple",
        columns=(("support_systems_for_gender_and_sexual_minority_students", 285.29),),
    ),
    ReportConfig(
        key="aamc_msar_admission_policies",
        pdf_name="05_msar018-msar-admission-policies-and-information.pdf",
        output_name="aamc_msar_admission_policies.csv",
        state_x=18.65,
        school_x=46.01,
        parser="simple",
        columns=(("admission_policies_and_information", 229.56),),
    ),
    ReportConfig(
        key="aamc_msar_applications_accepted",
        pdf_name="06_msar012-applications-accepted-information.pdf",
        output_name="aamc_msar_applications_accepted.csv",
        state_x=20.65,
        school_x=48.01,
        parser="label_pairs",
        label_xs=(184.81,),
        value_xs=(295.51,),
        label_map=(
            ("out-of-state applicants", "out_of_state_applicants"),
            ("canadian applicants", "canadian_applicants"),
            ("international applicants", "international_applicants"),
            ("daca status applicants", "daca_status_applicants"),
        ),
    ),
    ReportConfig(
        key="aamc_msar_secondary_application",
        pdf_name="07_msar006-msar-secondary-application.pdf",
        output_name="aamc_msar_secondary_application.csv",
        state_x=18.65,
        school_x=46.01,
        parser="simple",
        columns=(
            ("secondary_application_fee", 223.21),
            ("secondary_application_sent_to", 330.57),
            ("secondary_application_deadline", 430.81),
        ),
    ),
    ReportConfig(
        key="aamc_msar_transfer_policies",
        pdf_name="08_msar013-msar-application-transfer-policies.pdf",
        output_name="aamc_msar_transfer_policies.csv",
        state_x=18.65,
        school_x=46.01,
        parser="label_pairs",
        label_xs=(234.81, 290.09),
        value_xs=(351.29,),
        label_map=(
            ("contact name", "transfer_contact_name"),
            ("phone number", "transfer_phone_number"),
            ("email address", "transfer_email_address"),
            ("website", "transfer_website"),
        ),
    ),
    ReportConfig(
        key="aamc_msar_lor_preferences",
        pdf_name="09_msar011-msar-letter-of-evaluation-preferences.pdf",
        output_name="aamc_msar_lor_preferences_school_index.csv",
        state_x=430.31,
        school_x=46.01,
        parser="lor_index",
        notes="Preference symbols are not plain text in this PDF; this CSV preserves the official school index and flags symbol fields for follow-up decoding.",
    ),
    ReportConfig(
        key="aamc_msar_daca_policies",
        pdf_name="10_msar004-daca-applications-from-daca-status.pdf",
        output_name="aamc_msar_daca_policies.csv",
        state_x=18.61,
        school_x=45.97,
        parser="simple",
        columns=(("daca_policy", 247.01),),
    ),
    ReportConfig(
        key="aamc_msar_mcat_dates",
        pdf_name="11_msar003-msar-latest-and-oldest-mcat-administration-dates-considered.pdf",
        output_name="aamc_msar_mcat_dates.csv",
        state_x=19.24,
        school_x=55.24,
        parser="simple",
        columns=(
            ("latest_mcat_date_considered", 379.61),
            ("oldest_mcat_date_considered", 484.01),
        ),
    ),
    ReportConfig(
        key="aamc_msar_premed_course_requirements",
        pdf_name="12_msar002-msar-premed-course-requirements.pdf",
        output_name="aamc_msar_premed_course_requirements.csv",
        state_x=18.65,
        school_x=46.01,
        parser="course_requirements",
        columns=(
            ("course", 125.21),
            ("course_class", 225.29),
            ("required_or_recommended", 254.09),
            ("additional_info", 322.49),
            ("credit_hours", 498.89),
            ("lab", 527.69),
            ("pass_fail", 556.49),
            ("ap_credit", 610.49),
            ("online_course", 664.49),
            ("community_college", 718.49),
        ),
    ),
    ReportConfig(
        key="aamc_msar_preview_policies",
        pdf_name="13_msar-preview-participation-06-09-25-04152026-sc.pdf",
        output_name="aamc_msar_preview_policies.csv",
        state_x=None,
        school_x=51.36,
        parser="no_state_simple",
        columns=(("preview_policy", 246.41),),
    ),
    ReportConfig(
        key="aamc_msar_community_college_coursework",
        pdf_name="14_msar024-msar-community-college-coursework-information.pdf",
        output_name="aamc_msar_community_college_coursework.csv",
        state_x=15.77,
        school_x=43.13,
        parser="simple",
        columns=(
            ("coursework_upward_transfer", 189.31),
            ("coursework_accelerated", 248.19),
            ("coursework_supplemental", 305.79),
            ("coursework_additional_info", 367.67),
        ),
    ),
    ReportConfig(
        key="aamc_msar_interview_policies",
        pdf_name="15_msar008-msar-interview-procedures.pdf",
        output_name="aamc_msar_interview_policies.csv",
        state_x=18.61,
        school_x=45.97,
        parser="simple",
        columns=(
            ("interview_procedures", 152.09),
            ("interview_invitation_timing", 252.89),
            ("interview_day", 332.09),
            ("regional_interviews", 432.89),
            ("recorded_video_interviews", 512.09),
        ),
    ),
    ReportConfig(
        key="aamc_msar_waitlist_procedures",
        pdf_name="16_msar009-msar-waitlist-procedures-1.pdf",
        output_name="aamc_msar_waitlist_procedures.csv",
        state_x=18.61,
        school_x=45.97,
        parser="simple",
        columns=(
            ("number_on_waitlist", 216.05),
            ("number_accepted_from_waitlist", 307.47),
            ("waitlist_procedures", 370.55),
        ),
    ),
    ReportConfig(
        key="aamc_msar_deposit_information",
        pdf_name="18_msar001-msar-deposit-information-1.pdf",
        output_name="aamc_msar_deposit_information.csv",
        state_x=18.61,
        school_x=47.20,
        parser="deposit",
        columns=(
            ("in_state_deposit", 195.39),
            ("out_state_deposit", 240.00),
            ("deposit_refundable_by", 284.43),
            ("deposit_due", 409.78),
        ),
        notes="Boolean deposit fields are rendered as symbols, not plain text; amount and date fields are parsed.",
    ),
]


def normalize_space(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    return re.sub(r"\s+", " ", value).strip()


def clean_school_name(value: str) -> str:
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


def build_cmap(streams: list[tuple[int, str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for _, stream in streams:
        for block in re.findall(r"beginbfchar(.*?)endbfchar", stream, flags=re.S):
            for source, target in re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", block):
                mapping[source.upper()] = hex_to_unicode(target)
        for block in re.findall(r"beginbfrange(.*?)endbfrange", stream, flags=re.S):
            for start, end, target in re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", block):
                start_int = int(start, 16)
                end_int = int(end, 16)
                target_int = int(target, 16)
                width = len(start)
                for offset, codepoint in enumerate(range(start_int, end_int + 1)):
                    mapping[f"{codepoint:0{width}X}"] = chr(target_int + offset)
    return mapping


def hex_to_unicode(hex_value: str) -> str:
    if len(hex_value) % 4 == 0:
        try:
            return bytes.fromhex(hex_value).decode("utf-16-be")
        except UnicodeDecodeError:
            pass
    try:
        return bytes.fromhex(hex_value).decode("latin-1")
    except ValueError:
        return ""


def decode_hex_pdf_string(hex_value: str, cmap: dict[str, str]) -> str:
    hex_value = re.sub(r"\s+", "", hex_value).upper()
    if not hex_value:
        return ""
    if cmap and len(hex_value) % 4 == 0:
        chunks = [hex_value[index : index + 4] for index in range(0, len(hex_value), 4)]
        decoded = "".join(cmap.get(chunk, "") for chunk in chunks)
        if decoded:
            return decoded
    return hex_to_unicode(hex_value)


def extract_text_and_origin_from_block(block: str, cmap: dict[str, str]) -> tuple[str, float | None, float | None]:
    parts: list[str] = []
    origin_x: float | None = None
    origin_y: float | None = None
    for bt_match in BT_RE.finditer(block):
        bt = bt_match.group(1)
        if origin_x is None:
            td_match = TD_RE.search(bt)
            if td_match:
                origin_x = float(td_match.group(1))
                origin_y = float(td_match.group(2))
        local_parts: list[str] = []
        for token in re.finditer(r"\(((?:\\.|[^\\)])*)\)|<([0-9A-Fa-f]+)>", bt, flags=re.S):
            if token.group(1) is not None:
                local_parts.append(pdf_literal_unescape(token.group(1)))
            else:
                local_parts.append(decode_hex_pdf_string(token.group(2), cmap))
        if local_parts:
            parts.append("".join(local_parts))
    return normalize_space(" ".join(parts)), origin_x, origin_y


def extract_cells(pdf_path: Path) -> list[Cell]:
    streams = decompressed_streams(pdf_path)
    cmap = build_cmap(streams)
    cells: list[Cell] = []
    for stream_index, stream in streams:
        for match in CELL_RE.finditer(stream):
            text, origin_x, _ = extract_text_and_origin_from_block(match.group(5), cmap)
            if not text:
                continue
            x, y, w, h = map(float, match.group(1, 2, 3, 4))
            anchored_x = x
            if origin_x is not None and w > 300 and abs(origin_x - x) > 20:
                anchored_x = origin_x
            cells.append(Cell(stream_index=stream_index, x=anchored_x, y=y, w=w, h=h, text=text))
    return merge_repeated_cells(cells)


def merge_repeated_cells(cells: list[Cell]) -> list[Cell]:
    merged: dict[tuple[int, float, float, float, float], list[str]] = {}
    geometry: dict[tuple[int, float, float, float, float], Cell] = {}
    for cell in cells:
        key = (cell.stream_index, round(cell.x, 3), round(cell.y, 3), round(cell.w, 3), round(cell.h, 3))
        merged.setdefault(key, []).append(cell.text)
        geometry[key] = cell
    output: list[Cell] = []
    for key, texts in merged.items():
        cell = geometry[key]
        output.append(
            Cell(
                stream_index=cell.stream_index,
                x=cell.x,
                y=cell.y,
                w=cell.w,
                h=cell.h,
                text=normalize_space(" ".join(texts)),
            )
        )
    return sorted(output, key=lambda item: (item.stream_index, -item.y, item.x))


def near(left: float, right: float, tolerance: float = 3.0) -> bool:
    return abs(left - right) <= tolerance


def overlaps(a_bottom: float, a_top: float, b_bottom: float, b_top: float, tolerance: float = 0.75) -> bool:
    return min(a_top, b_top) + tolerance >= max(a_bottom, b_bottom)


def overlap_amount(a_bottom: float, a_top: float, b_bottom: float, b_top: float) -> float:
    return max(0.0, min(a_top, b_top) - max(a_bottom, b_bottom))


def cells_at_x(cells: list[Cell], x: float, tolerance: float = 3.0) -> list[Cell]:
    return [cell for cell in cells if near(cell.x, x, tolerance)]


def row_text_for_x(row: SchoolRow, x: float, tolerance: float = 3.0) -> str:
    selected = [
        cell
        for cell in row.cells
        if near(cell.x, x, tolerance) and cell.text not in {row.state, row.school_name}
    ]
    values: list[str] = []
    for cell in sorted(selected, key=lambda item: (-item.y, item.x)):
        if cell.text not in values:
            values.append(cell.text)
    return " | ".join(values)


def school_rows(cells: list[Cell], config: ReportConfig) -> list[SchoolRow]:
    rows: list[SchoolRow] = []
    if config.state_x is None:
        return no_state_rows(cells, config)
    state_cells = [
        cell
        for cell in cells_at_x(cells, config.state_x)
        if STATE_OR_PROVINCE_RE.fullmatch(cell.text) and cell.text not in {"USA", "CAN"}
    ]
    for state_cell in sorted(state_cells, key=lambda item: (item.stream_index, -item.y)):
        same_stream = [cell for cell in cells if cell.stream_index == state_cell.stream_index]
        school_candidates = [
            cell
            for cell in cells_at_x(same_stream, config.school_x)
            if overlaps(state_cell.bottom, state_cell.top, cell.bottom, cell.top, tolerance=2.5)
            and cell.text.lower() not in {"medical school", "school"}
        ]
        if not school_candidates:
            continue
        school_cell = max(
            school_candidates,
            key=lambda item: (
                overlap_amount(state_cell.bottom, state_cell.top, item.bottom, item.top),
                -abs(state_cell.bottom - item.bottom),
                item.h,
            ),
        )
        bottom = min(state_cell.bottom, school_cell.bottom)
        top = max(state_cell.top, school_cell.top)
        row_cells = [
            cell
            for cell in same_stream
            if overlaps(bottom, top, cell.bottom, cell.top, tolerance=1.0)
            and not near(cell.x, 7.2, 1.0)
            and cell.text not in {"State", "Medical School"}
        ]
        rows.append(
            SchoolRow(
                source_row_number=len(rows) + 1,
                stream_index=state_cell.stream_index,
                row_y=bottom,
                row_bottom=bottom,
                row_top=top,
                state=state_cell.text,
                school_name=school_cell.text,
                cells=row_cells,
            )
        )
    return rows


def no_state_rows(cells: list[Cell], config: ReportConfig) -> list[SchoolRow]:
    rows: list[SchoolRow] = []
    school_cells = [
        cell
        for cell in cells_at_x(cells, config.school_x)
        if cell.text.lower() not in {"medical school", "medical school name"}
    ]
    for school_cell in sorted(school_cells, key=lambda item: (item.stream_index, -item.y)):
        same_stream = [cell for cell in cells if cell.stream_index == school_cell.stream_index]
        bottom = school_cell.bottom
        top = school_cell.top
        row_cells = [
            cell
            for cell in same_stream
            if overlaps(bottom, top, cell.bottom, cell.top, tolerance=1.0)
            and not near(cell.x, 7.2, 1.0)
        ]
        if not any(near(cell.x, config.columns[0][1], 3.0) for cell in row_cells):
            continue
        rows.append(
            SchoolRow(
                source_row_number=len(rows) + 1,
                stream_index=school_cell.stream_index,
                row_y=bottom,
                row_bottom=bottom,
                row_top=top,
                state="",
                school_name=school_cell.text,
                cells=row_cells,
            )
        )
    return rows


def base_row(config: ReportConfig, row: SchoolRow) -> dict[str, str | int | float]:
    return {
        "source_key": config.key,
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "pdf_file": f"data/raw/aamc/msar_reports/{config.pdf_name}",
        "source_row_number": row.source_row_number,
        "stream_index": row.stream_index,
        "row_y": f"{row.row_y:.3f}",
        "state": row.state,
        "school_name_raw": row.school_name,
        "school_name_clean": clean_school_name(row.school_name),
    }


def parse_simple(config: ReportConfig, cells: list[Cell]) -> tuple[list[dict[str, str | int | float]], list[str]]:
    rows: list[dict[str, str | int | float]] = []
    for school_row in school_rows(cells, config):
        output = base_row(config, school_row)
        for field, x in config.columns:
            output[field] = row_text_for_x(school_row, x)
        output["notes"] = config.notes
        rows.append(output)
    return rows, BASE_COLUMNS + [field for field, _ in config.columns] + ["notes"]


def normalized_label(value: str) -> str:
    value = normalize_space(value).lower().rstrip(":")
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)
    return value


def parse_label_pairs(config: ReportConfig, cells: list[Cell]) -> tuple[list[dict[str, str | int | float]], list[str]]:
    label_to_field = {label: field for label, field in config.label_map}
    fieldnames = BASE_COLUMNS + list(label_to_field.values()) + ["unmapped_label_value_text", "notes"]
    rows: list[dict[str, str | int | float]] = []
    for school_row in school_rows(cells, config):
        output = base_row(config, school_row)
        for field in label_to_field.values():
            output[field] = ""
        unmapped: list[str] = []
        label_cells = [
            cell
            for cell in school_row.cells
            if any(near(cell.x, label_x, 3.0) for label_x in config.label_xs)
            and cell.text not in {school_row.state, school_row.school_name}
        ]
        for label_cell in sorted(label_cells, key=lambda item: (-item.y, item.x)):
            label = normalized_label(label_cell.text)
            field = label_to_field.get(label)
            values = [
                cell.text
                for cell in school_row.cells
                if any(near(cell.x, value_x, 3.0) for value_x in config.value_xs)
                and overlaps(label_cell.bottom, label_cell.top, cell.bottom, cell.top, tolerance=3.0)
            ]
            value = " | ".join(values)
            if field:
                output[field] = value
            elif label and value:
                unmapped.append(f"{label}: {value}")
        output["unmapped_label_value_text"] = " | ".join(unmapped)
        output["notes"] = config.notes
        rows.append(output)
    return rows, fieldnames


def parse_contact(config: ReportConfig, cells: list[Cell]) -> tuple[list[dict[str, str | int | float]], list[str]]:
    fieldnames = BASE_COLUMNS + ["address_lines", "phone", "fax", "email", "website", "contact_raw", "notes"]
    rows: list[dict[str, str | int | float]] = []
    label_fields = {"phone": "phone", "fax": "fax", "email": "email", "website": "website"}
    for school_row in school_rows(cells, config):
        output = base_row(config, school_row)
        for field in fieldnames:
            output.setdefault(field, "")
        raw_bits: list[str] = []
        address_lines: list[str] = []
        label_cells = [
            cell
            for cell in school_row.cells
            if any(near(cell.x, label_x, 3.0) for label_x in config.label_xs)
            and cell.text not in {school_row.state, school_row.school_name}
        ]
        for cell in sorted(label_cells, key=lambda item: -item.y):
            label = normalized_label(cell.text)
            if label in label_fields:
                values = [
                    value_cell.text
                    for value_cell in school_row.cells
                    if any(near(value_cell.x, value_x, 3.0) for value_x in config.value_xs)
                    and overlaps(cell.bottom, cell.top, value_cell.bottom, value_cell.top, tolerance=3.0)
                ]
                output[label_fields[label]] = " | ".join(values)
                if values:
                    raw_bits.append(f"{label}: {' | '.join(values)}")
            elif config.address_x is not None and near(cell.x, config.address_x, 3.0):
                address_lines.append(cell.text)
        output["address_lines"] = " | ".join(address_lines)
        output["contact_raw"] = " | ".join(address_lines + raw_bits)
        output["notes"] = config.notes
        rows.append(output)
    return rows, fieldnames


def parse_lor_index(config: ReportConfig, cells: list[Cell]) -> tuple[list[dict[str, str | int | float]], list[str]]:
    rows: list[dict[str, str | int | float]] = []
    fieldnames = BASE_COLUMNS + [
        "committee_letter_preference_status",
        "letter_packet_preference_status",
        "individual_letters_preference_status",
        "notes",
    ]
    for school_row in school_rows(cells, config):
        output = base_row(config, school_row)
        output["committee_letter_preference_status"] = ""
        output["letter_packet_preference_status"] = ""
        output["individual_letters_preference_status"] = ""
        output["notes"] = config.notes
        rows.append(output)
    return rows, fieldnames


def parse_course_requirements(config: ReportConfig, cells: list[Cell]) -> tuple[list[dict[str, str | int | float]], list[str]]:
    fieldnames = BASE_COLUMNS + [field for field, _ in config.columns] + ["notes"]
    rows: list[dict[str, str | int | float]] = []
    all_school_rows = school_rows(cells, config)
    course_x = dict(config.columns)["course"]
    course_cells = [
        cell
        for cell in cells_at_x(cells, course_x)
        if cell.text not in {"Course", "Medical School"}
    ]
    for course_cell in sorted(course_cells, key=lambda item: (item.stream_index, -item.y)):
        candidates = [
            row
            for row in all_school_rows
            if row.stream_index == course_cell.stream_index
            and overlaps(row.row_bottom, row.row_top, course_cell.bottom, course_cell.top, tolerance=1.0)
        ]
        if not candidates:
            continue
        school_row = max(candidates, key=lambda item: item.row_top - item.row_bottom)
        bottom = course_cell.bottom
        top = course_cell.top
        output = base_row(config, school_row)
        output["source_row_number"] = len(rows) + 1
        output["row_y"] = f"{bottom:.3f}"
        same_stream = [cell for cell in cells if cell.stream_index == course_cell.stream_index]
        pseudo_row = SchoolRow(
            source_row_number=school_row.source_row_number,
            stream_index=school_row.stream_index,
            row_y=bottom,
            row_bottom=bottom,
            row_top=top,
            state=school_row.state,
            school_name=school_row.school_name,
            cells=[
                cell
                for cell in same_stream
                if overlaps(bottom, top, cell.bottom, cell.top, tolerance=1.0)
            ],
        )
        for field, x in config.columns:
            value = row_text_for_x(pseudo_row, x)
            if field == "lab" and value and value.lower() not in {"yes", "no", "n/a", "not available"}:
                value = ""
            output[field] = value
        output["notes"] = "Lab and other checkbox-style fields may be symbol-rendered in the PDF and should be reviewed before use."
        rows.append(output)
    return rows, fieldnames


def parse_deposit(config: ReportConfig, cells: list[Cell]) -> tuple[list[dict[str, str | int | float]], list[str]]:
    fieldnames = BASE_COLUMNS + [field for field, _ in config.columns] + ["notes"]
    rows: list[dict[str, str | int | float]] = []
    streams = sorted({cell.stream_index for cell in cells})
    state_x = config.state_x or 18.61
    for stream_index in streams:
        stream_cells = [cell for cell in cells if cell.stream_index == stream_index]
        school_cells = [
            cell
            for cell in cells_at_x(stream_cells, config.school_x)
            if cell.text.lower() not in {"medical school", "school"}
        ]
        left_state_cells = [
            cell
            for cell in cells_at_x(stream_cells, state_x)
            if STATE_OR_PROVINCE_RE.fullmatch(cell.text) and cell.text not in {"USA", "CAN"}
        ]
        shifted_state_cells = [
            cell
            for cell in cells_at_x(stream_cells, 489.74)
            if STATE_OR_PROVINCE_RE.fullmatch(cell.text) and cell.text not in {"USA", "CAN"}
        ]
        school_cells = sorted(school_cells, key=lambda item: -item.y)
        shifted_state_cells = sorted(shifted_state_cells, key=lambda item: -item.y)
        first_state = left_state_cells[0].text if left_state_cells else ""
        for index, cell in enumerate(school_cells):
            current_state = first_state if index == 0 else ""
            if index > 0 and index - 1 < len(shifted_state_cells):
                current_state = shifted_state_cells[index - 1].text
            if not current_state:
                continue
            school_row = SchoolRow(
                source_row_number=len(rows) + 1,
                stream_index=stream_index,
                row_y=cell.bottom,
                row_bottom=cell.bottom,
                row_top=cell.top,
                state=current_state,
                school_name=cell.text,
                cells=[
                    candidate
                    for candidate in stream_cells
                    if overlaps(cell.bottom, cell.top, candidate.bottom, candidate.top, tolerance=1.0)
                    and not near(candidate.x, 489.74, 3.0)
                    and not near(candidate.x, 545.41, 3.0)
                ],
            )
            output = base_row(config, school_row)
            for field, x in config.columns:
                output[field] = row_text_for_x(school_row, x)
            output["notes"] = config.notes
            rows.append(output)
    return rows, fieldnames


def parse_report(config: ReportConfig) -> tuple[list[dict[str, str | int | float]], list[str]]:
    cells = extract_cells(RAW_DIR / config.pdf_name)
    if config.parser in {"simple", "no_state_simple"}:
        return parse_simple(config, cells)
    if config.parser == "deposit":
        return parse_deposit(config, cells)
    if config.parser == "label_pairs":
        return parse_label_pairs(config, cells)
    if config.parser == "contact":
        return parse_contact(config, cells)
    if config.parser == "lor_index":
        return parse_lor_index(config, cells)
    if config.parser == "course_requirements":
        return parse_course_requirements(config, cells)
    raise ValueError(f"unsupported parser: {config.parser}")


def write_csv(path: Path, rows: list[dict[str, str | int | float]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(summary_rows: list[dict[str, str | int]]) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    summary_csv = SOURCE_DIR / "aamc_msar_parsed_reports_summary.csv"
    write_csv(summary_csv, summary_rows, ["source_key", "pdf_file", "output_csv", "row_count", "notes"])

    lines = [
        "AAMC MSAR parsed reports summary",
        f"Generated: {datetime.now(timezone.utc).date().isoformat()}",
        f"Source: {SOURCE_URL}",
        "",
    ]
    for row in summary_rows:
        lines.append(f"{row['source_key']}: {row['row_count']} rows -> {row['output_csv']}")
        if row["notes"]:
            lines.append(f"  notes: {row['notes']}")
    (SUMMARY_DIR / "aamc_msar_parsed_reports_summary.txt").write_text("\n".join(lines) + "\n")


def main() -> None:
    summary_rows: list[dict[str, str | int]] = []
    for config in REPORTS:
        rows, fieldnames = parse_report(config)
        output_path = SOURCE_DIR / config.output_name
        write_csv(output_path, rows, fieldnames)
        summary_rows.append(
            {
                "source_key": config.key,
                "pdf_file": f"data/raw/aamc/msar_reports/{config.pdf_name}",
                "output_csv": f"data/source_tables/{config.output_name}",
                "row_count": len(rows),
                "notes": config.notes,
            }
        )
        print(f"{config.key}: {len(rows)} rows -> {output_path.relative_to(ROOT)}")
    write_summary(summary_rows)
    print(f"Wrote {SOURCE_DIR / 'aamc_msar_parsed_reports_summary.csv'}")
    print(f"Wrote {SUMMARY_DIR / 'aamc_msar_parsed_reports_summary.txt'}")


if __name__ == "__main__":
    main()
