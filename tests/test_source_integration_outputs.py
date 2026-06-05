from __future__ import annotations

import csv

from med_school_ranker.paths import (
    ADMISSIONS_STATS_CONFLICTS_CSV,
    ADMISSIONS_STATS_CSV,
    COST_AND_DEBT_CANDIDATES_CSV,
    COST_AND_DEBT_CSV,
    SOURCE_INTEGRATION_REPORT_CSV,
    SOURCE_REVIEW_QUEUE_CSV,
)


def read_rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def test_phase2a_source_outputs_have_expected_counts():
    assert len(read_rows(COST_AND_DEBT_CSV)) == 151
    assert len(read_rows(COST_AND_DEBT_CANDIDATES_CSV)) == 156
    assert len(read_rows(ADMISSIONS_STATS_CSV)) == 44
    assert len(read_rows(ADMISSIONS_STATS_CONFLICTS_CSV)) == 87

    report = {(row["category"], row["item"]): row for row in read_rows(SOURCE_INTEGRATION_REPORT_CSV)}
    assert report[("cost", "canonical_rows")]["count"] == "151"
    assert report[("admissions_stats", "conflicts")]["count"] == "87"


def test_pr_source_rows_are_not_matched_to_active_us_schools():
    pr_rows = [row for row in read_rows(SOURCE_REVIEW_QUEUE_CSV) if row["source_state"] == "PR"]
    assert pr_rows
    assert {row["review_reason"] for row in pr_rows} == {"no_compatible_active_school"}
    assert all(not row["school_id"] for row in pr_rows)
