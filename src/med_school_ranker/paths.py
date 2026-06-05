from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "outputs"

MASTER_CSV = DATA / "school_master.csv"
PREFERENCES_CSV = DATA / "user_preferences.csv"
SCENARIO_WEIGHTS_CSV = DATA / "scenario_weights.csv"
RANKINGS_CSV = OUT / "calculated_rankings.csv"
WORKBOOK_XLSX = OUT / "med_school_ranker.xlsx"
UPLOAD_ZIP = ROOT / "med-school-ranker-upload.zip"
