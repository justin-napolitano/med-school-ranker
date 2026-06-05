from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from med_school_ranker.paths import (
    AAMC_MCAT_GPA_GRID_CSV,
    ADMISSIONS_POLICIES_CSV,
    ADMISSIONS_SOURCE_QUEUE_CSV,
    ADMISSIONS_STATS_CSV,
    APPLICANT_PROFILES_CSV,
    COST_AND_DEBT_CSV,
    DATA,
    DATA_QUALITY_REPORT_CSV,
    FINAL_APPLICATION_LIST_CSV,
    LETTER_REQUIREMENTS_CSV,
    MANUAL_DATA,
    MASTER_CSV,
    NORMALIZED_DATA,
    OUT,
    PARTNER_INPUTS_CSV,
    PREFERENCES_CSV,
    RAW_DATA,
    REFERENCE_DATA,
    ROOT,
    SCENARIO_WEIGHTS_CSV,
    SCHOOL_DOSSIERS_CSV,
    SCHOOL_VISIBILITY_CSV,
    SOURCE_MATCH_OVERRIDES_CSV,
    SOURCE_REVIEW_QUEUE_CSV,
)
from med_school_ranker.source_integration import (
    ADMISSIONS_POLICIES_COLUMNS,
    AAMC_MCAT_GPA_GRID_COLUMNS,
    COST_AND_DEBT_COLUMNS,
    LETTER_REQUIREMENTS_COLUMNS,
    SOURCE_REVIEW_QUEUE_COLUMNS,
)


REPORT_COLUMNS = [
    "severity",
    "file",
    "row_id",
    "field",
    "message",
    "suggested_fix",
]

APPLICANT_PROFILE_COLUMNS = [
    "applicant_profile_id",
    "profile_name",
    "is_default_profile",
    "mcat_total",
    "overall_gpa",
    "science_gpa",
    "state_of_residence",
    "preferred_setting",
    "urban_preference_score",
    "rural_tolerance_score",
    "specialty_interest",
    "target_application_count",
    "cost_weight_level",
    "hidden_curriculum_weight_level",
    "specialty_weight_level",
    "notes",
]

ADMISSIONS_STATS_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "stats_cohort_year",
    "metric_population",
    "metric_type",
    "mcat_median_accepted",
    "mcat_median_matriculated",
    "mcat_mean_enrolled",
    "mcat_10th_percentile",
    "mcat_25th_percentile",
    "mcat_75th_percentile",
    "mcat_90th_percentile",
    "overall_gpa_median_accepted",
    "overall_gpa_median_matriculated",
    "overall_gpa_mean_enrolled",
    "science_gpa_mean_enrolled",
    "published_source_count",
    "published_mcat_average",
    "published_gpa_average",
    "published_mcat_spread",
    "published_gpa_spread",
    "published_mcat_band",
    "published_gpa_band",
    "aamc_acceptance_rate",
    "aamc_acceptance_rate_band",
    "data_quality_rank",
    "data_quality_band",
    "source_name",
    "source_url",
    "source_snapshot_path",
    "source_publication_date",
    "source_last_checked",
    "data_confidence",
    "notes",
]

ADMISSIONS_SOURCE_QUEUE_COLUMNS = [
    "school_id",
    "school_name",
    "degree_type",
    "candidate_source_url",
    "source_status",
    "extraction_status",
    "review_status",
    "last_checked",
    "notes",
]

PARTNER_INPUT_COLUMNS = [
    "applicant_profile_id",
    "school_id",
    "school_name",
    "could_live_here_4_years_score",
    "location_fit_score",
    "culture_fit_score",
    "regret_index_score",
    "hard_no_flag",
    "hard_no_reason",
    "partner_notes",
]

SCHOOL_VISIBILITY_COLUMNS = [
    "school_id",
    "school_name",
    "visibility_state",
    "visibility_reason",
    "hidden_at",
    "updated_at",
    "source",
    "notes",
]

SCHOOL_DOSSIER_COLUMNS = [
    "school_id",
    "school_name",
    "research_status",
    "interest_level",
    "four_year_happiness",
    "location_fit",
    "culture_fit",
    "regret_index",
    "hard_no_flag",
    "hard_no_reason",
    "application_decision_status",
    "notes",
    "updated_at",
    "source",
]

SOURCE_MATCH_OVERRIDES_COLUMNS = [
    "override_id",
    "source_table",
    "source_row_number",
    "source_school_name",
    "source_state",
    "source_degree_type",
    "override_action",
    "school_id",
    "school_name",
    "match_status",
    "reviewed_by",
    "reviewed_date",
    "review_notes",
]

REQUIRED_COLUMNS = {
    "data/school_master.csv": [
        "school_id",
        "school_name",
        "degree_type",
        "active_in_universe",
        "manual_exclusion_flag",
        "exclusion_reason",
    ],
    "data/user_preferences.csv": ["score_group", "column_name", "weight"],
    "data/scenario_weights.csv": ["scenario", "column_name", "weight"],
    "data/applicant_profiles.csv": APPLICANT_PROFILE_COLUMNS,
    "data/reference/aamc_mcat_gpa_acceptance_grid.csv": AAMC_MCAT_GPA_GRID_COLUMNS,
    "data/normalized/admissions_stats.csv": ADMISSIONS_STATS_COLUMNS,
    "data/normalized/cost_and_debt.csv": COST_AND_DEBT_COLUMNS,
    "data/normalized/admissions_policies.csv": ADMISSIONS_POLICIES_COLUMNS,
    "data/normalized/letter_requirements.csv": LETTER_REQUIREMENTS_COLUMNS,
    "data/manual/admissions_source_queue.csv": ADMISSIONS_SOURCE_QUEUE_COLUMNS,
    "data/manual/partner_inputs.csv": PARTNER_INPUT_COLUMNS,
    "data/manual/school_visibility.csv": SCHOOL_VISIBILITY_COLUMNS,
    "data/manual/school_dossiers.csv": SCHOOL_DOSSIER_COLUMNS,
    "data/manual/source_match_overrides.csv": SOURCE_MATCH_OVERRIDES_COLUMNS,
    "data/manual/source_review_queue.csv": SOURCE_REVIEW_QUEUE_COLUMNS,
    "data/final_application_list.csv": ["school_id", "school_name", "why_kept", "why_cut"],
}

MCAT_COLUMNS = [
    "mcat_total",
    "mcat_median_accepted",
    "mcat_median_matriculated",
    "mcat_mean_enrolled",
    "mcat_10th_percentile",
    "mcat_25th_percentile",
    "mcat_75th_percentile",
    "mcat_90th_percentile",
    "published_mcat_average",
]

GPA_COLUMNS = [
    "overall_gpa",
    "science_gpa",
    "overall_gpa_median_accepted",
    "overall_gpa_median_matriculated",
    "overall_gpa_mean_enrolled",
    "science_gpa_mean_enrolled",
    "published_gpa_average",
]

SOURCE_METADATA_COLUMNS = [
    "source_name",
    "source_url",
    "source_last_checked",
    "data_confidence",
]

COST_FIELDS = [
    "in_state_tuition_fees_insurance",
    "out_state_tuition_fees_insurance",
    "estimated_coa_in_state",
    "estimated_coa_out_state",
    "expected_scholarship",
    "application_fee",
    "secondary_fee",
    "deposit_amount",
    "average_grad_indebtedness",
]

ALLOWED_OVERRIDE_ACTIONS = {"accept_match", "reject_match", "force_no_match", "ignore_source_row"}
ALLOWED_VISIBILITY_STATES = {"", "visible", "hidden"}
ALLOWED_RESEARCH_STATUSES = {
    "",
    "not_started",
    "skimmed",
    "needs_deep_research",
    "researched",
    "ready_to_decide",
    "excluded",
    "applied",
}
ALLOWED_INTEREST_LEVELS = {"", "high", "medium", "low", "none"}
ALLOWED_DECISION_STATUSES = {
    "",
    "considering",
    "applying",
    "applied",
    "interview",
    "accepted",
    "waitlisted",
    "rejected",
    "withdrawn",
    "not_applying",
}

GENERATED_SCORING_COLUMNS = {
    "admissions_score",
    "attendance_score",
    "overall_school_value",
    "data_completeness_score",
}

SOURCE_MATCH_SCORE_COLUMNS = {"match_score", "second_match_score", "best_match_score"}

TRUTHY = {"1", "true", "t", "yes", "y"}


@dataclass(frozen=True)
class DataIssue:
    severity: str
    file: str
    row_id: str
    field: str
    message: str
    suggested_fix: str

    def to_row(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "file": self.file,
            "row_id": self.row_id,
            "field": self.field,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
        }


def ensure_data_layer_dirs(root: Path = ROOT) -> None:
    for path in [
        root / RAW_DATA.relative_to(ROOT),
        root / REFERENCE_DATA.relative_to(ROOT),
        root / NORMALIZED_DATA.relative_to(ROOT),
        root / MANUAL_DATA.relative_to(ROOT),
        root / "data/manual/private",
        root / OUT.relative_to(ROOT),
    ]:
        path.mkdir(parents=True, exist_ok=True)


def relative_file(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUTHY


def row_label(row: dict[str, str], fallback: str) -> str:
    for field in ["school_id", "applicant_profile_id", "scenario", "score_group"]:
        value = row.get(field, "").strip()
        if value:
            return value
    return fallback


def add_issue(
    issues: list[DataIssue],
    severity: str,
    file: str,
    row_id: str,
    field: str,
    message: str,
    suggested_fix: str,
) -> None:
    issues.append(DataIssue(severity, file, row_id, field, message, suggested_fix))


def missing_required_columns(
    root: Path,
    loaded: dict[str, tuple[list[str], list[dict[str, str]]]],
    issues: list[DataIssue],
) -> None:
    for label, columns in REQUIRED_COLUMNS.items():
        path = root / label
        if not path.exists():
            add_issue(
                issues,
                "error",
                label,
                "",
                "",
                "Missing required CSV file.",
                "Create the file with the required Phase 1 template columns.",
            )
            loaded[label] = ([], [])
            continue

        headers, rows = read_csv(path)
        loaded[label] = (headers, rows)
        missing = [column for column in columns if column not in headers]
        if missing:
            add_issue(
                issues,
                "error",
                label,
                "",
                ",".join(missing),
                f"Missing required column(s): {', '.join(missing)}.",
                "Add the missing column(s) without changing existing columns.",
            )


def validate_duplicate_school_ids(
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    seen: dict[str, int] = {}
    for row_number, row in enumerate(rows, start=2):
        school_id = row.get("school_id", "").strip()
        if not school_id:
            continue
        if school_id in seen:
            add_issue(
                issues,
                "error",
                "data/school_master.csv",
                school_id,
                "school_id",
                f"Duplicate school_id also appears on row {seen[school_id]}.",
                "Keep one stable school_id per application unit.",
            )
        else:
            seen[school_id] = row_number


def score_columns(headers: Iterable[str]) -> list[str]:
    return [
        header
        for header in headers
        if (header.endswith("_score") and header not in SOURCE_MATCH_SCORE_COLUMNS)
        or header == "Could I realistically see myself living here for 4 years? (1-10)"
    ]


def validate_score_ranges(
    label: str,
    headers: list[str],
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        for field in score_columns(headers):
            value = row.get(field, "").strip()
            if not value:
                continue
            number = parse_number(value)
            if number is None or not 1 <= number <= 10:
                add_issue(
                    issues,
                    "error",
                    label,
                    row_label(row, f"row {row_number}"),
                    field,
                    "Score must be a number from 1 to 10.",
                    "Blank unknown scores or replace with a 1-10 value.",
                )


def validate_exclusion_reasons(
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        if is_truthy(row.get("manual_exclusion_flag")) and not row.get("exclusion_reason", "").strip():
            add_issue(
                issues,
                "error",
                "data/school_master.csv",
                row_label(row, f"row {row_number}"),
                "exclusion_reason",
                "manual_exclusion_flag is true without an exclusion_reason.",
                "Add a clear exclusion_reason or set manual_exclusion_flag to FALSE.",
            )


def validate_scenario_references(
    master_headers: list[str],
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    known_columns = set(master_headers) | GENERATED_SCORING_COLUMNS
    for row_number, row in enumerate(rows, start=2):
        column = row.get("column_name", "").strip()
        if not column:
            continue
        if column not in known_columns:
            add_issue(
                issues,
                "error",
                "data/scenario_weights.csv",
                row_label(row, f"row {row_number}"),
                "column_name",
                f"Scenario weight references unknown column '{column}'.",
                "Use a column from school_master.csv or a generated scoring column.",
            )


def validate_numeric_range(
    label: str,
    rows: Iterable[dict[str, str]],
    fields: Iterable[str],
    lower: float,
    upper: float,
    description: str,
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        for field in fields:
            value = row.get(field, "").strip()
            if not value:
                continue
            number = parse_number(value)
            if number is None or not lower <= number <= upper:
                add_issue(
                    issues,
                    "error",
                    label,
                    row_label(row, f"row {row_number}"),
                    field,
                    f"{description} must be between {lower:g} and {upper:g}.",
                    "Blank unknown values or replace with a source-verified value in range.",
                )


def validate_source_metadata(
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    metric_fields = [
        field
        for field in ADMISSIONS_STATS_COLUMNS
        if field.startswith("mcat_") or "gpa_" in field
    ]
    for row_number, row in enumerate(rows, start=2):
        if not any(row.get(field, "").strip() for field in metric_fields):
            continue
        for field in SOURCE_METADATA_COLUMNS:
            if not row.get(field, "").strip():
                add_issue(
                    issues,
                    "warning",
                    "data/normalized/admissions_stats.csv",
                    row_label(row, f"row {row_number}"),
                    field,
                    "Admissions stat row has values without complete source metadata.",
                    "Add source name, URL, last checked date, and confidence before relying on the metric.",
                )


def validate_source_metadata_for_file(
    label: str,
    rows: Iterable[dict[str, str]],
    value_fields: Iterable[str],
    issues: list[DataIssue],
) -> None:
    fields = list(value_fields)
    for row_number, row in enumerate(rows, start=2):
        if not any(row.get(field, "").strip() for field in fields):
            continue
        for field in SOURCE_METADATA_COLUMNS:
            if not row.get(field, "").strip():
                add_issue(
                    issues,
                    "warning",
                    label,
                    row_label(row, f"row {row_number}"),
                    field,
                    "Source-backed row has values without complete source metadata.",
                    "Add source name, URL, last checked date, and confidence before relying on the row.",
                )


def validate_school_references(
    label: str,
    rows: Iterable[dict[str, str]],
    known_school_ids: set[str],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        school_id = row.get("school_id", "").strip()
        if school_id and school_id not in known_school_ids:
            add_issue(
                issues,
                "error",
                label,
                row_label(row, f"row {row_number}"),
                "school_id",
                "Row references a school_id that does not exist in school_master.csv.",
                "Fix the school_id or add a transparent source match override.",
            )


def validate_nonnegative_numbers(
    label: str,
    rows: Iterable[dict[str, str]],
    fields: Iterable[str],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        for field in fields:
            value = row.get(field, "").strip()
            if not value:
                continue
            number = parse_number(value)
            if number is None or number < 0:
                add_issue(
                    issues,
                    "error",
                    label,
                    row_label(row, f"row {row_number}"),
                    field,
                    "Cost/debt field must be a nonnegative number.",
                    "Blank unknown values or replace with a source-verified nonnegative number.",
                )


def validate_allowed_values(
    label: str,
    rows: Iterable[dict[str, str]],
    field: str,
    allowed_values: set[str],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        value = row.get(field, "").strip()
        if value not in allowed_values:
            add_issue(
                issues,
                "error",
                label,
                row_label(row, f"row {row_number}"),
                field,
                f"Unexpected value '{value}'.",
                f"Use one of: {', '.join(sorted(value for value in allowed_values if value))}, or leave blank.",
            )


def validate_source_match_overrides(
    rows: Iterable[dict[str, str]],
    known_school_ids: set[str],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        action = row.get("override_action", "").strip()
        if not action:
            continue
        if action not in ALLOWED_OVERRIDE_ACTIONS:
            add_issue(
                issues,
                "error",
                "data/manual/source_match_overrides.csv",
                row_label(row, f"row {row_number}"),
                "override_action",
                f"Unknown override_action '{action}'.",
                "Use accept_match, reject_match, force_no_match, or ignore_source_row.",
            )
        if action == "accept_match":
            school_id = row.get("school_id", "").strip()
            if not school_id or school_id not in known_school_ids:
                add_issue(
                    issues,
                    "error",
                    "data/manual/source_match_overrides.csv",
                    row_label(row, f"row {row_number}"),
                    "school_id",
                    "accept_match override must reference a valid school_id.",
                    "Use a school_id from school_master.csv.",
                )


def validate_blank_source_queue_urls(
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        if not row.get("candidate_source_url", "").strip():
            add_issue(
                issues,
                "warning",
                "data/manual/admissions_source_queue.csv",
                row_label(row, f"row {row_number}"),
                "candidate_source_url",
                "Admissions source queue URL is blank.",
                "Add a public admissions profile URL when reviewed.",
            )


def referenced_scoring_columns(
    master_headers: list[str],
    preference_rows: Iterable[dict[str, str]],
    scenario_rows: Iterable[dict[str, str]],
) -> list[str]:
    columns: list[str] = []
    for row in list(preference_rows) + list(scenario_rows):
        column = row.get("column_name", "").strip()
        if column in master_headers and column.endswith("_score") and column not in columns:
            columns.append(column)
    return columns


def validate_ranking_coverage(
    master_headers: list[str],
    master_rows: Iterable[dict[str, str]],
    preference_rows: Iterable[dict[str, str]],
    scenario_rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    columns = referenced_scoring_columns(master_headers, preference_rows, scenario_rows)
    if not columns:
        add_issue(
            issues,
            "warning",
            "data/user_preferences.csv",
            "",
            "column_name",
            "No direct school_master score columns are referenced by ranking weights.",
            "Confirm preference and scenario weights reference available scoring inputs.",
        )
        return

    for row_number, row in enumerate(master_rows, start=2):
        if not is_truthy(row.get("active_in_universe")):
            continue
        populated = sum(1 for column in columns if parse_number(row.get(column)) is not None)
        coverage = populated / len(columns)
        if coverage < 0.25:
            add_issue(
                issues,
                "warning",
                "data/school_master.csv",
                row_label(row, f"row {row_number}"),
                "ranking_coverage",
                "Low ranking coverage for weighted score inputs.",
                "Research and enter 1-10 score inputs, or keep this warning until later data phases.",
            )


def validate_final_application_rationale(
    rows: Iterable[dict[str, str]],
    issues: list[DataIssue],
) -> None:
    for row_number, row in enumerate(rows, start=2):
        if row.get("school_id", "").strip() and not (
            row.get("why_kept", "").strip() or row.get("why_cut", "").strip()
        ):
            add_issue(
                issues,
                "warning",
                "data/final_application_list.csv",
                row_label(row, f"row {row_number}"),
                "why_kept",
                "Final application list row has no rationale.",
                "Fill why_kept or why_cut before treating the final list as reviewed.",
            )


def write_report(path: Path, issues: Iterable[DataIssue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(issue.to_row() for issue in issues)


def validate_project(root: Path = ROOT, report_path: Path | None = None) -> list[DataIssue]:
    root = Path(root)
    ensure_data_layer_dirs(root)
    issues: list[DataIssue] = []
    loaded: dict[str, tuple[list[str], list[dict[str, str]]]] = {}

    missing_required_columns(root, loaded, issues)

    master_headers, master_rows = loaded.get("data/school_master.csv", ([], []))
    preference_headers, preference_rows = loaded.get("data/user_preferences.csv", ([], []))
    scenario_headers, scenario_rows = loaded.get("data/scenario_weights.csv", ([], []))
    applicant_headers, applicant_rows = loaded.get("data/applicant_profiles.csv", ([], []))
    stats_headers, stats_rows = loaded.get("data/normalized/admissions_stats.csv", ([], []))
    cost_headers, cost_rows = loaded.get("data/normalized/cost_and_debt.csv", ([], []))
    policy_headers, policy_rows = loaded.get("data/normalized/admissions_policies.csv", ([], []))
    letter_headers, letter_rows = loaded.get("data/normalized/letter_requirements.csv", ([], []))
    source_queue_headers, source_queue_rows = loaded.get("data/manual/admissions_source_queue.csv", ([], []))
    partner_headers, partner_rows = loaded.get("data/manual/partner_inputs.csv", ([], []))
    visibility_headers, visibility_rows = loaded.get("data/manual/school_visibility.csv", ([], []))
    dossier_headers, dossier_rows = loaded.get("data/manual/school_dossiers.csv", ([], []))
    _, source_override_rows = loaded.get("data/manual/source_match_overrides.csv", ([], []))
    _, source_review_rows = loaded.get("data/manual/source_review_queue.csv", ([], []))
    _, final_rows = loaded.get("data/final_application_list.csv", ([], []))
    known_school_ids = {row.get("school_id", "").strip() for row in master_rows if row.get("school_id", "").strip()}

    validate_duplicate_school_ids(master_rows, issues)
    for label, headers, rows in [
        ("data/school_master.csv", master_headers, master_rows),
        ("data/applicant_profiles.csv", applicant_headers, applicant_rows),
        ("data/normalized/admissions_stats.csv", stats_headers, stats_rows),
        ("data/normalized/cost_and_debt.csv", cost_headers, cost_rows),
        ("data/manual/partner_inputs.csv", partner_headers, partner_rows),
        ("data/manual/school_dossiers.csv", dossier_headers, dossier_rows),
    ]:
        validate_score_ranges(label, headers, rows, issues)

    validate_exclusion_reasons(master_rows, issues)
    validate_scenario_references(master_headers, scenario_rows, issues)
    validate_numeric_range(
        "data/applicant_profiles.csv",
        applicant_rows,
        ["mcat_total"],
        472,
        528,
        "Applicant profile MCAT",
        issues,
    )
    validate_numeric_range(
        "data/applicant_profiles.csv",
        applicant_rows,
        ["overall_gpa", "science_gpa"],
        0,
        4.0,
        "Applicant profile GPA",
        issues,
    )
    validate_numeric_range(
        "data/normalized/admissions_stats.csv",
        stats_rows,
        [field for field in MCAT_COLUMNS if field != "mcat_total"],
        472,
        528,
        "Admissions stats MCAT",
        issues,
    )
    validate_numeric_range(
        "data/normalized/admissions_stats.csv",
        stats_rows,
        [field for field in GPA_COLUMNS if field not in {"overall_gpa", "science_gpa"}],
        0,
        4.0,
        "Admissions stats GPA",
        issues,
    )
    validate_source_metadata(stats_rows, issues)
    validate_source_metadata_for_file(
        "data/normalized/cost_and_debt.csv",
        cost_rows,
        [
            "in_state_tuition_fees_insurance",
            "out_state_tuition_fees_insurance",
            "estimated_coa_in_state",
            "estimated_coa_out_state",
        ],
        issues,
    )
    validate_source_metadata_for_file(
        "data/normalized/admissions_policies.csv",
        policy_rows,
        ["policy_value"],
        issues,
    )
    validate_source_metadata_for_file(
        "data/normalized/letter_requirements.csv",
        letter_rows,
        ["requirement_url"],
        issues,
    )
    validate_nonnegative_numbers("data/normalized/cost_and_debt.csv", cost_rows, COST_FIELDS, issues)
    validate_numeric_range(
        "data/manual/school_dossiers.csv",
        dossier_rows,
        ["four_year_happiness", "location_fit", "culture_fit", "regret_index"],
        1,
        10,
        "Dossier score",
        issues,
    )
    validate_allowed_values(
        "data/manual/school_visibility.csv",
        visibility_rows,
        "visibility_state",
        ALLOWED_VISIBILITY_STATES,
        issues,
    )
    validate_allowed_values(
        "data/manual/school_dossiers.csv",
        dossier_rows,
        "research_status",
        ALLOWED_RESEARCH_STATUSES,
        issues,
    )
    validate_allowed_values(
        "data/manual/school_dossiers.csv",
        dossier_rows,
        "interest_level",
        ALLOWED_INTEREST_LEVELS,
        issues,
    )
    validate_allowed_values(
        "data/manual/school_dossiers.csv",
        dossier_rows,
        "application_decision_status",
        ALLOWED_DECISION_STATUSES,
        issues,
    )
    for label, rows in [
        ("data/normalized/admissions_stats.csv", stats_rows),
        ("data/normalized/cost_and_debt.csv", cost_rows),
        ("data/normalized/admissions_policies.csv", policy_rows),
        ("data/normalized/letter_requirements.csv", letter_rows),
        ("data/manual/partner_inputs.csv", partner_rows),
        ("data/manual/school_visibility.csv", visibility_rows),
        ("data/manual/school_dossiers.csv", dossier_rows),
        ("data/manual/source_review_queue.csv", source_review_rows),
    ]:
        validate_school_references(label, rows, known_school_ids, issues)
    validate_source_match_overrides(source_override_rows, known_school_ids, issues)
    validate_blank_source_queue_urls(source_queue_rows, issues)
    validate_ranking_coverage(master_headers, master_rows, preference_rows, scenario_rows, issues)
    validate_final_application_rationale(final_rows, issues)

    write_report(report_path or (root / DATA_QUALITY_REPORT_CSV.relative_to(ROOT)), issues)
    return issues


def has_errors(issues: Iterable[DataIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


def main() -> None:
    issues = validate_project()
    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    print(
        f"Wrote {DATA_QUALITY_REPORT_CSV.relative_to(ROOT)} with "
        f"{error_count} error(s) and {warning_count} warning(s)"
    )
    if error_count:
        raise SystemExit(1)
