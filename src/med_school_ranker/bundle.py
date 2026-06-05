from __future__ import annotations

import zipfile
from pathlib import Path

from med_school_ranker.paths import DATA, OUT, ROOT, SITE_DIR, UPLOAD_ZIP, WORKBOOK_XLSX
from med_school_ranker.final_list import build_final_application_list
from med_school_ranker.rankings import build_rankings
from med_school_ranker.site import build_site
from med_school_ranker.source_integration import build_source_integration
from med_school_ranker.validation import has_errors, validate_project
from med_school_ranker.workbook import build_workbook


def is_private_data_path(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    return (
        relative_parts[:3] == ("data", "manual", "private")
        or relative_parts[:2] == ("data", "private")
        or relative_parts[:2] == ("outputs", "private")
    )


def build_upload_zip() -> Path:
    with zipfile.ZipFile(UPLOAD_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DATA.rglob("*.csv")):
            if is_private_data_path(path):
                continue
            archive.write(path, path.relative_to(ROOT))
        for path in sorted(OUT.glob("*.csv")):
            archive.write(path, path.relative_to(ROOT))
        source_diffs = OUT / "source_diffs"
        if source_diffs.exists():
            for path in sorted(source_diffs.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(ROOT))
        if SITE_DIR.exists():
            for path in sorted(SITE_DIR.rglob("*")):
                if path.is_file():
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

    source_outputs = build_source_integration()
    issues = validate_project()
    if has_errors(issues):
        error_count = sum(1 for issue in issues if issue.severity == "error")
        print(f"Validation failed with {error_count} error(s); see outputs/data_quality_report.csv")
        raise SystemExit(1)

    rankings = build_rankings()
    final_list = build_final_application_list()
    workbook = build_workbook()
    site = build_site()
    bundle = build_upload_zip()
    print(f"Wrote {len(source_outputs)} source integration file(s)")
    print(f"Wrote {rankings.relative_to(ROOT)}")
    print(f"Wrote {final_list.relative_to(ROOT)}")
    print(f"Wrote {workbook.relative_to(ROOT)}")
    print(f"Wrote {site.relative_to(ROOT)}")
    print(f"Wrote {bundle.relative_to(ROOT)}")
