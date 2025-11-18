"""Command-line interface for running evaluations.

Usage example:
  python -m evaluator.cli.main evaluate --submissions ./data/submissions --output ./reports

This CLI is intentionally lightweight and uses argparse to avoid extra deps.
"""
from __future__ import annotations
from typing import Optional
import argparse
import sys
import os

import json


def _evaluate_folder(submissions: str, output: str, **kwargs) -> int:
    from evaluator.pipeline import evaluate_submissions
    import pandas as pd
    import json
    from datetime import datetime

    print(f"Evaluating submissions in: {submissions}")

    # Parse Excel answer keys if provided
    excel_answer_key = None
    excel_value_key = None
    excel_args = None
    if kwargs.get("excel_answer_key") and kwargs.get("excel_value_key"):
        with open(kwargs["excel_answer_key"], "r", encoding="utf8") as f:
            excel_answer_key = json.load(f)
        with open(kwargs["excel_value_key"], "r", encoding="utf8") as f:
            excel_value_key = json.load(f)
        excel_args = kwargs.get("excel_args")

    # Create timestamped report directory
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = os.path.join("data", "reports", now)
    os.makedirs(report_dir, exist_ok=True)

    df = evaluate_submissions(
        kwargs.get("solution"),
        submissions,
        excel_answer_key=excel_answer_key,
        excel_value_key=excel_value_key,
        excel_args=excel_args,
        report_dir=report_dir
    )

    print(f"Processed {len(df)} items. Reports in: {report_dir}")
    display_cols = [
        "filename", "name", "roll_number", "marks", "ok", "error", "duration", "test_results", "result", "value_sum", "formula_sum", "error_sum", "details"
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    print(df[display_cols].to_string(index=False))
    print(f"Wrote log and CSV to: {report_dir}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="evaluator")
    sub = parser.add_subparsers(dest="cmd")

    eval_p = sub.add_parser("evaluate", help="Evaluate submissions in a folder")
    eval_p.add_argument("--submissions", required=True, help="Folder containing student submissions")
    eval_p.add_argument("--solution", required=True, help="Path to instructor solution notebook (.ipynb)")
    eval_p.add_argument("--output", required=False, help="(Unused, kept for compatibility)")
    eval_p.add_argument("--excel-answer-key", required=False, help="Path to Excel formula answer key (JSON)")
    eval_p.add_argument("--excel-value-key", required=False, help="Path to Excel value answer key (JSON)")
    eval_p.add_argument("--excel-args", required=False, help="JSON string for Excel evaluation args (column_name, row_number, number_of_question, worksheet_name, student_name_cell, student_roll_no_cell)")

    args = parser.parse_args(argv)
    if args.cmd == "evaluate":
        excel_args = None
        if getattr(args, "excel_args", None):
            try:
                excel_args = json.loads(args.excel_args)
            except Exception:
                print("Could not parse --excel-args as JSON.")
        return _evaluate_folder(
            args.submissions,
            args.output,
            solution=args.solution,
            excel_answer_key=args.excel_answer_key,
            excel_value_key=args.excel_value_key,
            excel_args=excel_args
        )
    parser.print_help()
    return 2

"""
Command-line interface for the evaluator.
"""

import click
from pathlib import Path

@click.group()
def cli():
    pass

@cli.command()
@click.option("--instructor", help="Path to instructor notebook.", required=True)
@click.option("--submissions", help="Folder of student submissions.", required=True)
def evaluate(instructor, submissions):
    """Run evaluation on all submissions."""
    # TODO: Implement orchestrator
    click.echo("Running evaluator...")

if __name__ == "__main__":
    cli()


