from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
RAW_DATA = DATA / "raw"
REFERENCE_DATA = DATA / "reference"
NORMALIZED_DATA = DATA / "normalized"
MANUAL_DATA = DATA / "manual"

MASTER_CSV = DATA / "school_master.csv"
APPLICANT_PROFILES_CSV = DATA / "applicant_profiles.csv"
PREFERENCES_CSV = DATA / "user_preferences.csv"
SCENARIO_WEIGHTS_CSV = DATA / "scenario_weights.csv"
FINAL_APPLICATION_LIST_CSV = DATA / "final_application_list.csv"
AAMC_MCAT_GPA_GRID_CSV = REFERENCE_DATA / "aamc_mcat_gpa_acceptance_grid.csv"
ADMISSIONS_STATS_CSV = NORMALIZED_DATA / "admissions_stats.csv"
COST_AND_DEBT_CSV = NORMALIZED_DATA / "cost_and_debt.csv"
ADMISSIONS_POLICIES_CSV = NORMALIZED_DATA / "admissions_policies.csv"
LETTER_REQUIREMENTS_CSV = NORMALIZED_DATA / "letter_requirements.csv"
ADMISSIONS_SOURCE_QUEUE_CSV = MANUAL_DATA / "admissions_source_queue.csv"
PARTNER_INPUTS_CSV = MANUAL_DATA / "partner_inputs.csv"
SOURCE_MATCH_OVERRIDES_CSV = MANUAL_DATA / "source_match_overrides.csv"
SOURCE_REVIEW_QUEUE_CSV = MANUAL_DATA / "source_review_queue.csv"
RANKINGS_CSV = OUT / "calculated_rankings.csv"
DATA_QUALITY_REPORT_CSV = OUT / "data_quality_report.csv"
SOURCE_INTEGRATION_REPORT_CSV = OUT / "source_integration_report.csv"
SOURCE_MATCH_REVIEW_CSV = OUT / "source_match_review.csv"
ADMISSIONS_STATS_CANDIDATES_CSV = OUT / "admissions_stats_candidates.csv"
ADMISSIONS_STATS_CONFLICTS_CSV = OUT / "admissions_stats_conflicts.csv"
COST_AND_DEBT_CANDIDATES_CSV = OUT / "cost_and_debt_candidates.csv"
COST_AND_DEBT_REVIEW_CSV = OUT / "cost_and_debt_review.csv"
SITE_DIR = OUT / "site"
SITE_INDEX_HTML = SITE_DIR / "index.html"
WORKBOOK_XLSX = OUT / "med_school_ranker.xlsx"
UPLOAD_ZIP = ROOT / "med-school-ranker-upload.zip"
