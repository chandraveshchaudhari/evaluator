"""
Evaluator — The orchestrator for the entire grading pipeline.

Responsibilities:
  1. Ingest instructor solution
  2. Discover student submissions
  3. Delegate grading to the appropriate execution backend
     (Docker or local)
  4. Collect, consolidate, and report results
"""

import time
from pathlib import Path
from typing import List, Dict, Any

from instantgrade.ingestion.solution_ingestion import SolutionIngestion
from instantgrade.reporting.reporting_service import ReportingService
from instantgrade.utils.logger import setup_logger
from instantgrade.execution.execution_service_docker import ExecutionServiceDocker
from instantgrade.execution.notebook_executor import NotebookExecutor


class Evaluator:
    """
    The main orchestrator class responsible for grading workflows.

    Parameters
    ----------
    solution_file_path : str or Path
        Path to instructor's reference solution notebook.
    submission_folder_path : str or Path
        Folder containing all student notebooks.
    use_docker : bool, optional
        Whether to use Docker-based isolated grading (default=True).
    parallel_workers : int, optional
        Number of parallel workers for future extensions (default=1).
    log_path : str, optional
        Path to directory for saving logs.
    log_level : str, optional
        Logging verbosity ("debug", "normal", "silent").
    """

    def __init__(
        self,
        solution_file_path: str | Path,
        submission_folder_path: str | Path,
        use_docker: bool = True,
        parallel_workers: int = 1,
        log_path: str | Path = "./logs",
        log_level: str = "normal",
    ):
        self.solution_path = Path(solution_file_path)
        self.submission_path = Path(submission_folder_path)
        self.use_docker = use_docker
        self.parallel_workers = parallel_workers
        self.log_path = Path(log_path)
        self.log_path.mkdir(exist_ok=True, parents=True)
        self.logger = setup_logger(level=log_level)
        self.report = None
        self.executed = []

    # ------------------------------------------------------------------
    def run(self) -> ReportingService:
        """Run the full evaluation pipeline."""
        self.logger.info("Starting evaluation pipeline...")

        start_time = time.time()
        # 1. Load solution
        self.logger.info("Loading instructor solution...")
        solution_service = SolutionIngestion(self.solution_path)
        self.solution = solution_service.understand_notebook_solution()
        self.logger.info(f"Loaded {len(self.solution['questions'])} questions.")

        # 2. Discover student submissions
        all_submissions = sorted(
            [f for f in self.submission_path.glob("*.ipynb") if f.is_file()]
        )
        if not all_submissions:
            raise FileNotFoundError(f"No student notebooks found in {self.submission_path}")

        self.logger.info(f"Discovered {len(all_submissions)} submissions to grade.")

        # 3. Execute grading
        executed = self.execute_all(all_submissions)
        self.executed = executed
        self.logger.info("Execution phase completed successfully.")

        # 4. Build report
        self.report = ReportingService(executed, logger=self.logger)
        self.logger.info("Report generation complete.")

        elapsed = round(time.time() - start_time, 2)
        self.logger.info(f"Total evaluation completed in {elapsed}s.")

        return self.report

    # ------------------------------------------------------------------
    def execute_all(self, submission_paths: List[Path]) -> List[Dict[str, Any]]:
        """Run grading across all students sequentially or in future parallel mode."""
        if self.use_docker:
            self.logger.info("Starting Docker-based evaluation pipeline...")
            execution_service = ExecutionServiceDocker(logger=self.logger)
        else:
            self.logger.info("Starting Local evaluation pipeline...")
            execution_service = NotebookExecutor(timeout=120)

        results = []

        for idx, sub in enumerate(submission_paths, start=1):
            self.logger.info(f"[{idx}/{len(submission_paths)}] Grading: {sub.name}")

            try:
                if self.use_docker:
                    result = execution_service.execute_student(self.solution_path, sub)
                else:
                    result = self._grade_local_student(execution_service, sub)
                results.append(result)
            except Exception as e:
                self.logger.exception(f"Fatal error grading {sub.name}: {e}")
                results.append({
                    "student_path": sub,
                    "execution": {
                        "success": False,
                        "errors": [str(e)],
                        "student_meta": {"name": "Unknown", "roll_number": "Unknown"},
                    },
                    "results": [],
                })

        return results

    # ------------------------------------------------------------------
    def _grade_local_student(self, executor: NotebookExecutor, submission_path: Path) -> Dict[str, Any]:
        """Simplified fallback for local grading without Docker."""
        self.logger.info(f"[Local] Grading {submission_path.name}")

        exec_result = executor.run_notebook(submission_path)
        ns = exec_result.get("namespace", {})
        name = ns.get("name", "Unknown")
        roll = ns.get("roll_number", "Unknown")

        return {
            "student_path": submission_path,
            "execution": {
                "success": True,
                "errors": [],
                "student_meta": {"name": name, "roll_number": roll},
            },
            "results": [],
        }

    # ------------------------------------------------------------------
    def to_html(self, path: str | Path):
        """Generate HTML report for the graded results."""
        if self.report is None:
            raise RuntimeError("No report available. Run Evaluator.run() first.")
        path = Path(path)
        self.report.to_html(path)
        self.logger.info(f"HTML report generated at: {path}")
        return str(path)

    # ------------------------------------------------------------------
    def summary(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate quick text summary statistics from graded results."""
        total = len(all_results)
        passed = sum(
            1 for r in all_results if r.get("execution", {}).get("success", False)
        )
        return {"total": total, "passed": passed, "failed": total - passed}
