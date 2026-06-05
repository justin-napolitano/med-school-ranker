from __future__ import annotations

import zipfile
from pathlib import Path

from med_school_ranker.paths import DATA, OUT, ROOT, UPLOAD_ZIP, WORKBOOK_XLSX
from med_school_ranker.rankings import build_rankings
from med_school_ranker.validation import has_errors, validate_project
from med_school_ranker.workbook import build_workbook


def is_private_data_path(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    return relative_parts[:3] == ("data", "manual", "private") or relative_parts[:2] == ("data", "private")


def build_upload_zip() -> Path:
    with zipfile.ZipFile(UPLOAD_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DATA.rglob("*.csv")):
            if is_private_data_path(path):
                continue
            archive.write(path, path.relative_to(ROOT))
        for path in sorted(OUT.glob("*.csv")):
            archive.write(path, path.relative_to(ROOT))
        archive.write(WORKBOOK_XLSX, WORKBOOK_XLSX.relative_to(ROOT))
        for path in [ROOT / ".gitignore", ROOT / "README.md", ROOT / "pyproject.toml", ROOT / "uv.lock"]:
            if path.exists():
                archive.write(path, path.relative_to(ROOT))
        for folder_name in ["docs", "scripts", "src"]:
            for path in sorted((ROOT / folder_name).rglob("*")):
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                if path.is_file():
                    archive.write(path, path.relative_to(ROOT))
    return UPLOAD_ZIP


def main() -> None:
    issues = validate_project()
    if has_errors(issues):
        error_count = sum(1 for issue in issues if issue.severity == "error")
        print(f"Validation failed with {error_count} error(s); see outputs/data_quality_report.csv")
        raise SystemExit(1)

    rankings = build_rankings()
    workbook = build_workbook()
    bundle = build_upload_zip()
    print(f"Wrote {rankings.relative_to(ROOT)}")
    print(f"Wrote {workbook.relative_to(ROOT)}")
    print(f"Wrote {bundle.relative_to(ROOT)}")
