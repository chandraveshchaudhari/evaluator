
from pathlib import Path
import traceback
import nbformat
from nbclient import NotebookClient

from evaluator.comparison.comparison_service import ComparisonService
from evaluator.execution.notebook_executor import NotebookExecutor, extract_namespace_from_notebook
from evaluator.utils.time_utils import now_timestamp



class ExecutionService:
    """
    Service for executing student code in a safe/controlled environment.
    """

    def execute(self, solution, submission_path):
        """
        Run the solution and submission (currently only notebook supported).
        """
        if solution["type"] == "notebook":
            return self.execute_notebook(solution, submission_path)

        raise ValueError(f"Unsupported solution type: {solution['type']}")

    def execute_notebook(self, solution, submission_path):
        """
        Execute a student's Jupyter notebook submission and evaluate correctness.
        """

        # 1. Run student notebook safely
        executor = NotebookExecutor()
        student_execution = executor.run_notebook(submission_path)

        # 2. Compare student namespace with instructor assertions
        comparator = ComparisonService()
        results = comparator.run_assertions(
            student_namespace=student_execution["namespace"],
            assertions=sum(
                [v["tests"] for v in solution["questions"].values()], start=[]
            ),
        )

        # 3. Return combined evaluation report
        return {
            "student_path": submission_path,
            "execution": student_execution,
            "results": results,
        }
