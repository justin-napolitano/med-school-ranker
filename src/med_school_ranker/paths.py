from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
RAW_DATA = DATA / "raw"
NORMALIZED_DATA = DATA / "normalized"
MANUAL_DATA = DATA / "manual"

MASTER_CSV = DATA / "school_master.csv"
APPLICANT_PROFILES_CSV = DATA / "applicant_profiles.csv"
PREFERENCES_CSV = DATA / "user_preferences.csv"
SCENARIO_WEIGHTS_CSV = DATA / "scenario_weights.csv"
FINAL_APPLICATION_LIST_CSV = DATA / "final_application_list.csv"
ADMISSIONS_STATS_CSV = NORMALIZED_DATA / "admissions_stats.csv"
ADMISSIONS_SOURCE_QUEUE_CSV = MANUAL_DATA / "admissions_source_queue.csv"
PARTNER_INPUTS_CSV = MANUAL_DATA / "partner_inputs.csv"
RANKINGS_CSV = OUT / "calculated_rankings.csv"
DATA_QUALITY_REPORT_CSV = OUT / "data_quality_report.csv"
SITE_DIR = OUT / "site"
SITE_INDEX_HTML = SITE_DIR / "index.html"
WORKBOOK_XLSX = OUT / "med_school_ranker.xlsx"
UPLOAD_ZIP = ROOT / "med-school-ranker-upload.zip"
