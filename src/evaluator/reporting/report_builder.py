
"""
Builds student reports from evaluation results.
"""

import json
import csv
from pathlib import Path

class ReportBuilder:
    """
    Creates CSV, JSON, and optional HTML reports.
    """

    @staticmethod
    def save_json(report, path: Path):
        with open(path, "w") as f:
            json.dump(report, f, indent=4)

    @staticmethod
    def save_csv(report, path: Path):
        with open(path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Passed", "Failed"])
            for q, tests in report.items():
                passed = sum(t["passed"] for t in tests)
                failed = len(tests) - passed
                writer.writerow([q, passed, failed])

import json
import csv
from pathlib import Path

class ReportBuilder:
    """
    Creates CSV, JSON, and optional HTML reports.
    """

    @staticmethod
    def save_json(report, path: Path):
        with open(path, "w") as f:
            json.dump(report, f, indent=4)

    @staticmethod
    def save_csv(report, path: Path):
        with open(path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Passed", "Failed"])
            for q, tests in report.items():
                passed = sum(t["passed"] for t in tests)
                failed = len(tests) - passed
                writer.writerow([q, passed, failed])


from __future__ import annotations
from typing import Dict, Any
import json
import csv
import os


def build_json_report(result: Dict[str, Any], out_path: str) -> str:
    """Write result dict as JSON to out_path and return the path."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return out_path


def build_csv_summary(rows: list[Dict[str, Any]], out_path: str) -> str:
    """Write a list of per-student summary rows (dicts) to a CSV file."""
    if not rows:
        raise ValueError("rows must not be empty")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return out_path

clean_df.to_csv(f"{assignment_number} Metrics.csv", index = False)
