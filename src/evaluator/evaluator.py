"""Orchestrator for the evaluation pipeline.

This module exposes an `Evaluator` class that coordinates ingestion,
execution, comparison and reporting. The implementation below focuses on
clarity and small, testable steps. Methods are implemented as thin
wrappers around the respective service classes so they can be mocked in
tests or replaced via dependency injection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Any

from evaluator.ingestion.ingestion_service import IngestionService
from evaluator.execution.execution_service import ExecutionService
from evaluator.reporting.reporting_service import ReportingService

import json

class Evaluator:
    def __init__(
        self,
        solution_file_path: str | Path,
        submission_folder_path: str | Path,
        config_json: str | Path | None = None,
    ) -> None:
        """
        Args:
            solution_file_path: Path to the instructor solution file.
            submission_folder_path: Path to the folder containing student submissions.
            ingestion, execution, comparison, reporting: Optional service overrides.
            config_json: Optional path to a JSON configuration file.
        """
        self.solution_file_path = Path(solution_file_path)
        self.submission_folder_path = Path(submission_folder_path)

        self.config = None
        if config_json is not None:
            config_path = Path(config_json)
            if config_path.exists():
                with open(config_path, "r", encoding="utf8") as f:
                    self.config = json.load(f)

        self.submissions = None
        self.executed = None
        self.report = None

    # --- High-level pipelines -------------------------------------------------
    def run(self) -> Any:
        """Run the full pipeline: load -> execute -> compare -> report.

        Returns the generated report object from the reporting service.
        """
        submissions = self.load()
        executed = self.execute_all(submissions)
        report = self.build_report(executed)
        return report

    # --- Sub-parts exposed for granular control -------------------------------
    def load(self) -> List[Path]:
        """Load and return list of submission file paths using ingestion service."""
         
        return IngestionService(self.solution_file_path, self.submission_folder_path)
    
    def execute_all(self, submissions: Iterable[Path]) -> List[Any]:
        """Execute all submissions against the instructor solution.

        Returns a list of executed objects (the execution service is free to
        return domain-specific result objects).
        """
        solution_file = submissions.load_solution()
        executed_results: List[Any] = []
        for sub in submissions.list_submissions():
            executed = ExecutionService().execute(solution_file, sub)
            executed_results.append(executed)
        return executed_results

    def build_report(self, executed_results: Iterable[dict]) -> Any:
        """Delegate to the reporting service to build final outputs."""
        return ReportingService(executed_results)

    def save_all_reports(self, report_obj: Any, output_dir: str | Path) -> Path:
        """Save generated report(s) to disk and return the target folder.

        This delegates to the reporting service when available. The method is
        intentionally small so callers can override or extend behaviour.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        # If reporting service exposes a save_all, use it; otherwise try simple JSON/CSV export
        if hasattr(self.reporting, "save_all"):
            self.reporting.save_all(report_obj, out)
        else:
            # best-effort: attempt to persist via ReportBuilder if available
            try:
                rb = ReportingService()
                rb.build(report_obj).to_csv(out / "report.csv")
            except Exception:
                # swallow -- saving is optional and environment-specific
                pass
        return out

    def summary(self, comparison_results: Iterable[dict]) -> dict:
        """Return a small summary (counts, average score if present).

        This is a convenience method for quick CLI/CI checks.
        """
        rows = list(comparison_results)
        total = len(rows)
        score_sum = 0.0
        scored = 0
        for r in rows:
            s = r.get("score") if isinstance(r, dict) else None
            if isinstance(s, (int, float)):
                score_sum += s
                scored += 1
        avg = (score_sum / scored) if scored else None
        return {"total_submissions": total, "average_score": avg}

    def debug_mode(self, enabled: bool = True) -> None:
        """Toggle debug mode for services that respect it (no-op by default)."""
        if hasattr(self.ingestion, "debug"):
            setattr(self.ingestion, "debug", enabled)
        if hasattr(self.execution, "debug"):
            setattr(self.execution, "debug", enabled)
        if hasattr(self.comparison, "debug"):
            setattr(self.comparison, "debug", enabled)
        if hasattr(self.reporting, "debug"):
            setattr(self.reporting, "debug", enabled)

