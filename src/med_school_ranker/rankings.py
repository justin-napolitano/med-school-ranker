from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from med_school_ranker.paths import (
    AAMC_MCAT_GPA_GRID_CSV,
    ADMISSIONS_POLICIES_CSV,
    ADMISSIONS_STATS_CSV,
    APPLICANT_PROFILES_CSV,
    COST_AND_DEBT_CSV,
    MASTER_CSV,
    OUT,
    PARTNER_INPUTS_CSV,
    PREFERENCES_CSV,
    PRIVATE_APPLICANT_PROFILES_CSV,
    PRIVATE_OUT,
    PRIVATE_RANKINGS_CSV,
    RANKINGS_CSV,
    ROOT,
    SCENARIO_WEIGHTS_CSV,
)


TRUTHY = {"1", "true", "t", "yes", "y"}
FALSEY = {"0", "false", "f", "no", "n"}

STATE_NAMES_TO_ABBREV = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "district of columbia": "DC",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
}
STATE_ABBREVS = set(STATE_NAMES_TO_ABBREV.values())

MCAT_BANDS = [
    ("Less than 486", None, 485.0),
    ("486-489", 486.0, 489.0),
    ("490-493", 490.0, 493.0),
    ("494-497", 494.0, 497.0),
    ("498-501", 498.0, 501.0),
    ("502-505", 502.0, 505.0),
    ("506-509", 506.0, 509.0),
    ("510-513", 510.0, 513.0),
    ("514-517", 514.0, 517.0),
    ("Greater than 517", 518.0, None),
]
GPA_BANDS = [
    ("Greater than 3.79", 3.790001, None),
    ("3.60-3.79", 3.60, 3.79),
    ("3.40-3.59", 3.40, 3.59),
    ("3.20-3.39", 3.20, 3.39),
    ("3.00-3.19", 3.00, 3.19),
    ("2.80-2.99", 2.80, 2.99),
    ("2.60-2.79", 2.60, 2.79),
    ("2.40-2.59", 2.40, 2.59),
    ("2.20-2.39", 2.20, 2.39),
    ("2.00-2.19", 2.00, 2.19),
    ("Less than 2.00", None, 1.999),
]

MCAT_SOURCE_FIELDS = [
    "published_mcat_average",
    "mcat_mean_enrolled",
    "mcat_median_matriculated",
    "mcat_median_accepted",
    "median_mcat",
]
GPA_SOURCE_FIELDS = [
    "published_gpa_average",
    "overall_gpa_mean_enrolled",
    "overall_gpa_median_matriculated",
    "overall_gpa_median_accepted",
    "median_gpa",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def is_falsey(value: str | None) -> bool:
    return str(value or "").strip().lower() in FALSEY


def state_abbrev(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    upper = text.upper()
    if upper in STATE_ABBREVS:
        return upper
    return STATE_NAMES_TO_ABBREV.get(text.lower(), "")


def clamp(value: float, lower: float = 1.0, upper: float = 10.0) -> float:
    return max(lower, min(upper, value))


def mcat_fit_score(applicant_mcat: float | None, school_mcat: float | None) -> float | None:
    if applicant_mcat is None or school_mcat is None:
        return None
    return clamp(7 + (applicant_mcat - school_mcat) / 2)


def gpa_fit_score(applicant_gpa: float | None, school_gpa: float | None) -> float | None:
    if applicant_gpa is None or school_gpa is None:
        return None
    return clamp(7 + (applicant_gpa - school_gpa) / 0.08)


def band_for_value(value: float | None, bands: list[tuple[str, float | None, float | None]]) -> str:
    if value is None:
        return ""
    for label, lower, upper in bands:
        if lower is not None and value < lower:
            continue
        if upper is not None and value > upper:
            continue
        return label
    return ""


def mcat_band(value: float | None) -> str:
    if value is None:
        return ""
    return band_for_value(float(int(value + 0.5)), MCAT_BANDS)


def gpa_band(value: float | None) -> str:
    if value is None:
        return ""
    return band_for_value(round(value, 2), GPA_BANDS)


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def fmt_trimmed(value: float | None, digits: int = 2) -> str:
    if value is None:
        return ""
    text = f"{value:.{digits}f}"
    if "." not in text:
        return text
    return text.rstrip("0").rstrip(".")


def load_weights(path: Path, group_key: str) -> dict[str, list[tuple[str, float]]]:
    grouped: dict[str, list[tuple[str, float]]] = {}
    for row in read_csv(path):
        group = row[group_key].strip()
        column = row["column_name"].strip()
        weight = parse_number(row.get("weight")) or 0
        if group and column and weight > 0:
            grouped.setdefault(group, []).append((column, weight))
    return grouped


def first_by_school(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id and school_id not in output:
            output[school_id] = row
    return output


def group_policies(rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id:
            grouped.setdefault(school_id, []).append(row)
    return grouped


def partner_keyed(rows: Iterable[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    keyed: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        profile_id = row.get("applicant_profile_id", "").strip()
        school_id = row.get("school_id", "").strip()
        if profile_id and school_id:
            keyed[(profile_id, school_id)] = row
    return keyed


def selected_value(row: dict[str, str], fields: Iterable[str]) -> float | None:
    for field in fields:
        value = parse_number(row.get(field))
        if value is not None:
            return value
    return None


def profile_context(profile: dict[str, str], grid_rows: Iterable[dict[str, str]]) -> dict[str, str]:
    applicant_mcat = parse_number(profile.get("mcat_total"))
    applicant_gpa = parse_number(profile.get("overall_gpa"))
    applicant_mcat_band = mcat_band(applicant_mcat)
    applicant_gpa_band = gpa_band(applicant_gpa)
    rate = ""
    rate_band = ""
    if applicant_mcat_band and applicant_gpa_band:
        for row in grid_rows:
            if row.get("mcat_band") == applicant_mcat_band and row.get("gpa_band") == applicant_gpa_band:
                rate = row.get("acceptance_rate", "")
                rate_band = row.get("acceptance_rate_band", "")
                break
    return {
        "profile_aamc_mcat_band": applicant_mcat_band,
        "profile_aamc_gpa_band": applicant_gpa_band,
        "profile_aamc_acceptance_rate": rate,
        "profile_aamc_acceptance_rate_band": rate_band,
    }


def oos_policy_score(
    school: dict[str, str],
    applicant_state: str,
    policy_rows: Iterable[dict[str, str]],
) -> tuple[float | None, str]:
    school_state = state_abbrev(school.get("state_abbrev") or school.get("state"))
    if not applicant_state:
        return None, "missing applicant state for OOS fit"
    if school_state and school_state == applicant_state:
        return 10.0, ""

    explicit_accepts = school.get("accepts_oos", "").strip()
    if is_truthy(explicit_accepts):
        return 6.0, ""
    if is_falsey(explicit_accepts):
        return 1.0, ""

    policy_text = " ".join(
        row.get("policy_value", "")
        for row in policy_rows
        if row.get("policy_field") == "out_of_state_applicants"
    ).strip()
    lowered = policy_text.lower()
    if any(marker in lowered for marker in ["does not accept", "not accepted", "not considered", "only in-state"]):
        return 1.0, ""
    if policy_text:
        return 6.0, "OOS policy text present but not normalized"
    return 4.0, "missing OOS policy"


def cost_basis_for_profile(
    school: dict[str, str],
    cost_row: dict[str, str],
    applicant_state: str,
) -> float | None:
    school_state = state_abbrev(school.get("state_abbrev") or school.get("state"))
    same_state = bool(applicant_state and school_state and applicant_state == school_state)
    if same_state:
        for field in ["estimated_coa_in_state", "in_state_tuition_fees_insurance"]:
            value = parse_number(cost_row.get(field))
            if value is not None:
                return value
    for field in ["estimated_coa_out_state", "out_state_tuition_fees_insurance"]:
        value = parse_number(cost_row.get(field))
        if value is not None:
            return value
    return None


def adjusted_cost_basis(cost_basis: float | None, cost_row: dict[str, str]) -> float | None:
    if cost_basis is None:
        return None
    scholarship = parse_number(cost_row.get("expected_scholarship"))
    if scholarship is None:
        return cost_basis
    return max(0.0, cost_basis - scholarship)


def percentile_cost_scores(rows: list[dict[str, str]]) -> None:
    values = sorted(
        parse_number(row.get("cost_basis_adjusted"))
        for row in rows
        if parse_number(row.get("cost_basis_adjusted")) is not None
    )
    values = [value for value in values if value is not None]
    if not values:
        return
    min_value = values[0]
    max_value = values[-1]
    if min_value == max_value:
        for row in rows:
            if parse_number(row.get("cost_basis_adjusted")) is not None:
                row["attendance_cost_score"] = "10.0"
                row["debt_burden_score"] = "10.0"
        return
    for row in rows:
        value = parse_number(row.get("cost_basis_adjusted"))
        if value is None:
            continue
        percentile = (value - min_value) / (max_value - min_value)
        score = 10 - 9 * percentile
        row["attendance_cost_score"] = fmt(score, 1)
        row["debt_burden_score"] = fmt(score, 1)


def weighted_score(values: dict[str, str], weights: Iterable[tuple[str, float]]) -> tuple[float | None, float]:
    numerator = 0.0
    denominator = 0.0
    possible = 0.0
    for column, weight in weights:
        possible += weight
        value = parse_number(values.get(column))
        if value is None:
            continue
        numerator += value * weight
        denominator += weight
    if denominator == 0:
        return None, 0.0
    return numerator / denominator, denominator / possible if possible else 0.0


def rank_values(rows: list[dict[str, str]], score_column: str, rank_column: str) -> None:
    scored = [
        (idx, parse_number(row.get(score_column)))
        for idx, row in enumerate(rows)
        if not is_truthy(row.get("excluded_from_rank")) and parse_number(row.get(score_column)) is not None
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    rank = 0
    previous_score: float | None = None
    for position, (idx, score) in enumerate(scored, start=1):
        if previous_score is None or score != previous_score:
            rank = position
            previous_score = score
        rows[idx][rank_column] = str(rank)


def admissions_fit_tier(admissions_score: float | None) -> str:
    if admissions_score is None:
        return "Unscored"
    if admissions_score < 4:
        return "Very High Risk"
    if admissions_score < 5.5:
        return "Reach"
    if admissions_score < 7.5:
        return "Target"
    return "Likely"


def application_bucket(admissions_tier: str, attendance_score: float | None) -> str:
    if admissions_tier == "Unscored":
        return "Unscored"
    if admissions_tier in {"Very High Risk", "Reach"} and attendance_score is not None and attendance_score >= 8:
        return "Dream"
    if admissions_tier == "Very High Risk":
        return "Reach"
    return admissions_tier


def research_funnel(rank: float | None) -> str:
    if rank is None:
        return ""
    if rank <= 35:
        return "25-35 application pool"
    if rank <= 40:
        return "40 researched schools"
    if rank <= 75:
        return "75 serious candidates"
    return "full universe"


def component_label(column: str) -> str:
    label = column
    for prefix in ["admissions_", "attendance_"]:
        if label.startswith(prefix):
            label = label[len(prefix) :]
    return label.replace("_score", "").replace("_", " ").title()


def driver_fields(values: dict[str, str], columns: Iterable[str]) -> tuple[str, str]:
    scored = []
    for column in columns:
        value = parse_number(values.get(column))
        if value is not None:
            scored.append((column, value))
    positives = [f"{component_label(column)} {fmt_trimmed(value, 1)}" for column, value in sorted(scored, key=lambda item: item[1], reverse=True)[:3] if value >= 7]
    negatives = [f"{component_label(column)} {fmt_trimmed(value, 1)}" for column, value in sorted(scored, key=lambda item: item[1])[:3] if value <= 5]
    return "; ".join(positives), "; ".join(negatives)


def score_projection_for_profile(
    profile: dict[str, str],
    profile_source: str,
    master_rows: list[dict[str, str]],
    stats_by_school: dict[str, dict[str, str]],
    cost_by_school: dict[str, dict[str, str]],
    policies_by_school: dict[str, list[dict[str, str]]],
    partner_by_profile_school: dict[tuple[str, str], dict[str, str]],
    grid_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    applicant_profile_id = profile.get("applicant_profile_id", "").strip()
    applicant_mcat = parse_number(profile.get("mcat_total"))
    applicant_gpa = parse_number(profile.get("overall_gpa"))
    applicant_state = state_abbrev(profile.get("state_of_residence"))
    profile_bands = profile_context(profile, grid_rows)

    output_rows: list[dict[str, str]] = []
    for school in master_rows:
        school_id = school.get("school_id", "").strip()
        stats = stats_by_school.get(school_id, {})
        cost = cost_by_school.get(school_id, {})
        partner = partner_by_profile_school.get((applicant_profile_id, school_id), {})
        policies = policies_by_school.get(school_id, [])
        values = dict(school)
        values.update(
            {
                "applicant_profile_id": applicant_profile_id,
                "profile_name": profile.get("profile_name", "").strip(),
                "profile_source": profile_source,
                "applicant_state_abbrev": applicant_state,
                **profile_bands,
                "published_mcat_average": stats.get("published_mcat_average", ""),
                "published_gpa_average": stats.get("published_gpa_average", ""),
                "published_mcat_band": stats.get("published_mcat_band", ""),
                "published_gpa_band": stats.get("published_gpa_band", ""),
                "stats_data_quality_rank": stats.get("data_quality_rank", ""),
                "stats_data_quality_band": stats.get("data_quality_band", ""),
                "stats_data_confidence": stats.get("data_confidence", ""),
                "stats_source_name": stats.get("source_name", ""),
                "stats_source_url": stats.get("source_url", ""),
                "cost_data_confidence": cost.get("data_confidence", ""),
                "hard_no_flag": partner.get("hard_no_flag", ""),
                "hard_no_reason": partner.get("hard_no_reason", ""),
                "excluded_from_rank": "",
                "missing_score_inputs": "",
                "score_warnings": "",
                "top_positive_drivers": "",
                "top_negative_drivers": "",
            }
        )

        mcat_source = selected_value(stats, MCAT_SOURCE_FIELDS) or selected_value(school, ["median_mcat"])
        gpa_source = selected_value(stats, GPA_SOURCE_FIELDS) or selected_value(school, ["median_gpa"])
        values["school_mcat_for_fit"] = fmt_trimmed(mcat_source, 1)
        values["school_gpa_for_fit"] = fmt_trimmed(gpa_source, 2)

        warnings: list[str] = []
        if applicant_mcat is None:
            warnings.append("missing applicant MCAT")
        if applicant_gpa is None:
            warnings.append("missing applicant GPA")
        if mcat_source is None:
            warnings.append("missing school MCAT")
        if gpa_source is None:
            warnings.append("missing school GPA")

        mcat_score = mcat_fit_score(applicant_mcat, mcat_source)
        gpa_score = gpa_fit_score(applicant_gpa, gpa_source)
        if mcat_score is not None:
            values["admissions_mcat_fit_score"] = fmt(mcat_score, 1)
        if gpa_score is not None:
            values["admissions_gpa_fit_score"] = fmt(gpa_score, 1)

        oos_score, oos_warning = oos_policy_score(school, applicant_state, policies)
        if oos_score is not None:
            values["admissions_oos_friendliness_score"] = fmt(oos_score, 1)
        if oos_warning:
            warnings.append(oos_warning)

        cost_basis = cost_basis_for_profile(school, cost, applicant_state)
        adjusted_basis = adjusted_cost_basis(cost_basis, cost)
        values["cost_basis"] = fmt_trimmed(cost_basis, 0)
        values["cost_basis_adjusted"] = fmt_trimmed(adjusted_basis, 0)
        if cost_basis is None:
            warnings.append("missing cost basis")

        partner_score_map = {
            "could_live_here_4_years_score": "four_year_happiness_score",
            "location_fit_score": "attendance_location_score",
            "culture_fit_score": "attendance_culture_score",
            "regret_index_score": "regret_index_score",
        }
        for source_field, target_field in partner_score_map.items():
            if partner.get(source_field, "").strip():
                values[target_field] = partner[source_field]

        if stats.get("data_quality_band") == "low":
            warnings.append("low stats data quality")
        if is_truthy(partner.get("hard_no_flag")) or is_truthy(school.get("manual_exclusion_flag")):
            values["excluded_from_rank"] = "TRUE"
        elif is_falsey(partner.get("hard_no_flag")):
            values["excluded_from_rank"] = "FALSE"

        values["score_warnings"] = "; ".join(dict.fromkeys(warnings))
        output_rows.append(values)

    percentile_cost_scores(output_rows)
    return output_rows


def build_rankings_rows(
    profile_rows: list[dict[str, str]],
    profile_source: str = "public_template",
) -> list[dict[str, str]]:
    master_rows = read_csv(MASTER_CSV)
    stats_by_school = first_by_school(read_csv(ADMISSIONS_STATS_CSV))
    cost_by_school = first_by_school(read_csv(COST_AND_DEBT_CSV))
    policies_by_school = group_policies(read_csv(ADMISSIONS_POLICIES_CSV))
    partner_by_profile_school = partner_keyed(read_csv(PARTNER_INPUTS_CSV))
    preference_weights = load_weights(PREFERENCES_CSV, "score_group")
    scenario_weights = load_weights(SCENARIO_WEIGHTS_CSV, "scenario")
    grid_rows = read_csv(AAMC_MCAT_GPA_GRID_CSV)

    profiles = [row for row in profile_rows if row.get("applicant_profile_id", "").strip()]
    default_profiles = [row for row in profiles if is_truthy(row.get("is_default_profile"))]
    profiles = default_profiles or profiles

    component_columns = [
        column
        for group in ["Admissions Score", "Attendance Score"]
        for column, _ in preference_weights.get(group, [])
    ]
    scoring_columns = {
        column
        for weights in preference_weights.values()
        for column, _ in weights
        if column not in {"admissions_score", "attendance_score", "overall_school_value", "data_completeness_score"}
    }
    scoring_columns.update(
        column
        for weights in scenario_weights.values()
        for column, _ in weights
        if column not in {"admissions_score", "attendance_score", "overall_school_value", "data_completeness_score"}
    )

    output_rows: list[dict[str, str]] = []
    for profile in profiles:
        profile_output = score_projection_for_profile(
            profile,
            profile_source,
            master_rows,
            stats_by_school,
            cost_by_school,
            policies_by_school,
            partner_by_profile_school,
            grid_rows,
        )
        for values in profile_output:
            admissions_score, admissions_coverage = weighted_score(values, preference_weights.get("Admissions Score", []))
            attendance_score, attendance_coverage = weighted_score(values, preference_weights.get("Attendance Score", []))
            values["admissions_score"] = fmt(admissions_score)
            values["attendance_score"] = fmt(attendance_score)
            values["admissions_data_coverage"] = fmt(admissions_coverage * 100, 0)
            values["attendance_data_coverage"] = fmt(attendance_coverage * 100, 0)

            overall_score, overall_coverage = weighted_score(values, preference_weights.get("Overall School Value", []))
            values["overall_school_value"] = fmt(overall_score)
            values["overall_data_coverage"] = fmt(overall_coverage * 100, 0)

            populated = sum(1 for column in scoring_columns if parse_number(values.get(column)) is not None)
            completeness = (populated / len(scoring_columns) * 10) if scoring_columns else None
            values["data_completeness_score"] = fmt(completeness)
            tier = admissions_fit_tier(admissions_score)
            values["admissions_fit_tier"] = tier
            values["application_bucket"] = application_bucket(tier, attendance_score)
            values["dynamic_tier"] = values["application_bucket"]

            missing_inputs = [
                column
                for column in component_columns
                if parse_number(values.get(column)) is None
            ]
            values["missing_score_inputs"] = "; ".join(missing_inputs)
            positive, negative = driver_fields(values, component_columns)
            values["top_positive_drivers"] = positive
            values["top_negative_drivers"] = negative

            for scenario, weights in scenario_weights.items():
                scenario_score, scenario_coverage = weighted_score(values, weights)
                key = scenario.lower().replace(" ", "_")
                values[f"{key}_score"] = fmt(scenario_score)
                values[f"{key}_coverage"] = fmt(scenario_coverage * 100, 0)

        rank_values(profile_output, "overall_school_value", "overall_rank")
        for scenario in scenario_weights:
            key = scenario.lower().replace(" ", "_")
            rank_values(profile_output, f"{key}_score", f"{key}_rank")

        for row in profile_output:
            row["suggested_funnel_bucket"] = research_funnel(parse_number(row.get("overall_rank")))
        output_rows.extend(profile_output)

    output_rows.sort(
        key=lambda row: (
            row.get("applicant_profile_id", ""),
            parse_number(row.get("overall_rank")) is None,
            parse_number(row.get("overall_rank")) or 999999,
            row.get("school_name", ""),
        )
    )
    return output_rows


def ranking_headers(rows: list[dict[str, str]], scenario_weights: dict[str, list[tuple[str, float]]]) -> list[str]:
    computed_headers = [
        "applicant_profile_id",
        "profile_name",
        "profile_source",
        "overall_rank",
        "school_id",
        "school_name",
        "degree_type",
        "city",
        "state",
        "state_abbrev",
        "applicant_state_abbrev",
        "admissions_fit_tier",
        "application_bucket",
        "dynamic_tier",
        "suggested_funnel_bucket",
        "overall_school_value",
        "admissions_score",
        "attendance_score",
        "admissions_mcat_fit_score",
        "admissions_gpa_fit_score",
        "admissions_oos_friendliness_score",
        "attendance_cost_score",
        "four_year_happiness_score",
        "regret_index_score",
        "data_completeness_score",
        "admissions_data_coverage",
        "attendance_data_coverage",
        "overall_data_coverage",
        "profile_aamc_mcat_band",
        "profile_aamc_gpa_band",
        "profile_aamc_acceptance_rate",
        "profile_aamc_acceptance_rate_band",
        "school_mcat_for_fit",
        "school_gpa_for_fit",
        "published_mcat_average",
        "published_gpa_average",
        "published_mcat_band",
        "published_gpa_band",
        "stats_data_quality_rank",
        "stats_data_quality_band",
        "stats_data_confidence",
        "stats_source_name",
        "stats_source_url",
        "cost_basis",
        "cost_basis_adjusted",
        "cost_data_confidence",
        "debt_burden_score",
        "excluded_from_rank",
        "hard_no_flag",
        "hard_no_reason",
        "missing_score_inputs",
        "score_warnings",
        "top_positive_drivers",
        "top_negative_drivers",
    ]
    scenario_headers: list[str] = []
    for scenario in scenario_weights:
        key = scenario.lower().replace(" ", "_")
        scenario_headers.extend([f"{key}_rank", f"{key}_score", f"{key}_coverage"])

    passthrough_headers = [
        "application_unit_type",
        "parent_school_name",
        "campus_name",
        "accreditation_status",
        "manual_exclusion_flag",
        "exclusion_reason",
        "research_stage",
        "data_confidence",
        "source_name",
        "source_url",
        "last_verified_date",
        "notes",
    ]
    base_headers = computed_headers + scenario_headers + passthrough_headers
    extras = sorted({key for row in rows for key in row} - set(base_headers))
    return base_headers + [header for header in extras if header.endswith("_score")]


def build_rankings(
    output_path: Path | None = None,
    profile_path: Path | None = None,
    profile_source: str = "public_template",
) -> Path:
    output_path = output_path or RANKINGS_CSV
    profile_path = profile_path or APPLICANT_PROFILES_CSV
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build_rankings_rows(read_csv(profile_path), profile_source=profile_source)
    scenario_weights = load_weights(SCENARIO_WEIGHTS_CSV, "scenario")
    write_csv(output_path, ranking_headers(rows, scenario_weights), rows)
    return output_path


def build_private_rankings() -> Path:
    if not PRIVATE_APPLICANT_PROFILES_CSV.exists():
        raise SystemExit(f"Missing private profile file: {PRIVATE_APPLICANT_PROFILES_CSV.relative_to(ROOT)}")
    PRIVATE_OUT.mkdir(parents=True, exist_ok=True)
    return build_rankings(PRIVATE_RANKINGS_CSV, PRIVATE_APPLICANT_PROFILES_CSV, profile_source="private_local")


def main() -> None:
    output = build_rankings()
    print(f"Wrote {output.relative_to(ROOT)} with {len(read_csv(output))} rows")


def main_private() -> None:
    output = build_private_rankings()
    print(f"Wrote {output.relative_to(ROOT)} with {len(read_csv(output))} private rows")
