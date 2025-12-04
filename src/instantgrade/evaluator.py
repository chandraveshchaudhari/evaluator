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
import logging

from instantgrade.ingestion.ingestion_service import IngestionService
from instantgrade.execution.execution_service import ExecutionService
from instantgrade.reporting.reporting_service import ReportingService

import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Evaluator:
    """Orchestrator for the evaluation pipeline.

    The Evaluator class coordinates the entire evaluation workflow by managing
    ingestion, execution, comparison, and reporting services. It provides both
    high-level methods for running the complete pipeline and granular methods
    for controlling individual steps.

    Parameters
    ----------
    solution_file_path : str or Path
        Path to the instructor's solution file (notebook or Excel).
    submission_folder_path : str or Path
        Path to the folder containing student submission files.
    config_json : str or Path, optional
        Path to a JSON configuration file for customizing evaluation behavior.
        Default is None.
    log_file : str or Path, optional
        Path to save evaluation logs. If provided, logs will be saved to this file
        in addition to console output. Default is None (console only).

    Attributes
    ----------
    solution_file_path : Path
        Resolved path to the solution file.
    submission_folder_path : Path
        Resolved path to the submissions folder.
    config : dict or None
        Loaded configuration dictionary if config_json was provided.
    log_file : Path or None
        Path to log file if provided.
    submissions : Any
        Cached submissions loaded by the ingestion service.
    executed : Any
        Cached execution results.
    report : Any
        Cached report object.

    Examples
    --------
    >>> from instantgrade import Evaluator
    >>> evaluator = Evaluator(
    ...     solution_file_path="solution.ipynb",
    ...     submission_folder_path="submissions/",
    ...     log_file="evaluation_log.txt"
    ... )
    >>> report = evaluator.run()

    >>> # Granular control
    >>> submissions = evaluator.load()
    >>> executed = evaluator.execute_all(submissions)
    >>> report = evaluator.build_report(executed)
    """

    def __init__(
        self,
        solution_file_path: str | Path,
        submission_folder_path: str | Path,
        config_json: str | Path | None = None,
        log_file: str | Path | None = None,
    ) -> None:
        self.solution_file_path = Path(solution_file_path)
        self.submission_folder_path = Path(submission_folder_path)
        self.log_file = Path(log_file) if log_file else None

        self.config = None
        if config_json is not None:
            config_path = Path(config_json)
            if config_path.exists():
                with open(config_path, "r", encoding="utf8") as f:
                    self.config = json.load(f)

        self.submissions = None
        self.executed = None
        self.report = None
        
        # Setup logging with file handler if log_file is provided
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration for the evaluator.
        
        If log_file is specified, adds a file handler to save logs to disk.
        Logs will be saved to both console and file simultaneously.
        """
        if self.log_file:
            # Create parent directories if they don't exist
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            file_handler = logging.FileHandler(
                self.log_file,
                mode='w',
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add file handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
            
            logger.info(f"📝 Logging to file: {self.log_file}")

    # --- High-level pipelines -------------------------------------------------
    def run(self) -> Any:
        """Run the full evaluation pipeline.

        Executes the complete workflow: loads submissions, executes them against
        the solution, compares results, and generates a report.

        Returns
        -------
        Any
            The generated report object from the reporting service.

        Examples
        --------
        >>> evaluator = Evaluator("solution.ipynb", "submissions/")
        >>> report = evaluator.run()
        """
        logger.info("=" * 70)
        logger.info("🚀 STARTING EVALUATION PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Solution file: {self.solution_file_path}")
        logger.info(f"Submissions folder: {self.submission_folder_path}")

        submissions = self.load()
        logger.info(f"✅ Loaded {len(submissions)} submissions")

        executed = self.execute_all(submissions)
        logger.info(f"✅ Executed all {len(executed)} submissions")

        report = self.build_report(executed)
        logger.info("✅ Built report")
        logger.info("=" * 70)
        logger.info("🎉 EVALUATION PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)

        return report

    # --- Sub-parts exposed for granular control -------------------------------
    def load(self) -> List[Path]:
        """Load submission files using the ingestion service.

        Returns
        -------
        list of Path
            List of submission file paths found in the submission folder.

        Examples
        --------
        >>> evaluator = Evaluator("solution.ipynb", "submissions/")
        >>> submissions = evaluator.load()
        >>> print(f"Found {len(submissions)} submissions")
        """
        logger.info("\n📂 LOADING SUBMISSIONS...")
        return IngestionService(self.solution_file_path, self.submission_folder_path)

    def execute_all(self, submissions: Iterable[Path]) -> List[Any]:
        """Execute all submissions against the instructor solution.

        Parameters
        ----------
        submissions : Iterable of Path
            Collection of submission file paths to execute.

        Returns
        -------
        list of Any
            List of executed result objects. The execution service determines
            the specific structure of each result object.

        Examples
        --------
        >>> submissions = evaluator.load()
        >>> executed = evaluator.execute_all(submissions)
        >>> print(f"Executed {len(executed)} submissions")
        """
        logger.info("\n⚙️  EXECUTING SUBMISSIONS...")

        solution_file = submissions.load_solution()
        submission_list = list(submissions.list_submissions())
        total_submissions = len(submission_list)

        logger.info(f"Total submissions to evaluate: {total_submissions}")

        executed_results: List[Any] = []

        for idx, sub in enumerate(submission_list, 1):
            # Extract student info from filename
            filename = sub.name
            logger.info(f"\n[{idx}/{total_submissions}] 👤 Processing: {filename}")

            try:
                executed = ExecutionService().execute(solution_file, sub)
                executed_results.append(executed)
                logger.info(f"  ✅ Successfully executed: {filename}")
            except Exception as e:
                logger.error(f"  ❌ ERROR executing {filename}: {str(e)}")
                executed_results.append({
                    "student_path": sub,
                    "error": str(e),
                    "results": []
                })

        return executed_results

    def build_report(self, executed_results: Iterable[dict]) -> Any:
        """Build a report from execution results.

        Delegates to the reporting service to generate final output reports.

        Parameters
        ----------
        executed_results : Iterable of dict
            Collection of execution result dictionaries to include in the report.

        Returns
        -------
        Any
            The report object generated by the reporting service.

        Examples
        --------
        >>> executed = evaluator.execute_all(submissions)
        >>> report = evaluator.build_report(executed)
        """
        return ReportingService(executed_results)

    def save_all_reports(self, report_obj: Any, output_dir: str | Path) -> Path:
        """Save generated reports to disk.

        Persists the report object(s) to the specified output directory. The
        method delegates to the reporting service when available, otherwise
        attempts a best-effort save.

        Parameters
        ----------
        report_obj : Any
            The report object to save, typically from build_report().
        output_dir : str or Path
            Target directory for saving reports. Created if it doesn't exist.

        Returns
        -------
        Path
            The resolved output directory path where reports were saved.

        Examples
        --------
        >>> report = evaluator.run()
        >>> output_path = evaluator.save_all_reports(report, "reports/")
        >>> print(f"Reports saved to {output_path}")
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
        """Generate a summary of comparison results.

        Calculates aggregate statistics such as total submission count and
        average score. This is useful for quick CLI/CI checks.

        Parameters
        ----------
        comparison_results : Iterable of dict
            Collection of comparison result dictionaries, each potentially
            containing a 'score' key.

        Returns
        -------
        dict
            Summary dictionary with keys:
            - 'total_submissions' : int
                Total number of submissions processed.
            - 'average_score' : float or None
                Average score across all submissions with scores, or None
                if no scores were found.

        Examples
        --------
        >>> results = evaluator.run()
        >>> summary = evaluator.summary(results)
        >>> print(f"Average: {summary['average_score']:.1f}")
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
        """Toggle debug mode for evaluation services.

        Enables or disables debug mode for all services that support it
        (ingestion, execution, comparison, reporting). Services without
        debug support are silently skipped.

        Parameters
        ----------
        enabled : bool, default=True
            Whether to enable (True) or disable (False) debug mode.

        Examples
        --------
        >>> evaluator = Evaluator("solution.ipynb", "submissions/")
        >>> evaluator.debug_mode(True)  # Enable detailed logging
        >>> report = evaluator.run()
        """
        if hasattr(self.ingestion, "debug"):
            setattr(self.ingestion, "debug", enabled)
        if hasattr(self.execution, "debug"):
            setattr(self.execution, "debug", enabled)
        if hasattr(self.comparison, "debug"):
            setattr(self.comparison, "debug", enabled)
        if hasattr(self.reporting, "debug"):
            setattr(self.reporting, "debug", enabled)
