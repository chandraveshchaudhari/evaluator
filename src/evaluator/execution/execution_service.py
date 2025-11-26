from evaluator.execution.notebook_executor import NotebookExecutor
from evaluator.comparison.comparison_service import ComparisonService
import traceback


class ExecutionService:
    """
    Executes student notebooks and evaluates them against instructor tests.
    """

    def __init__(self, timeout=60):
        self.timeout = timeout

    def execute(self, solution, submission_path):
        """
        Dispatch execution based on solution type.
        """
        if solution["type"] == "notebook":
            return self.execute_notebook(solution, submission_path)
        raise ValueError(f"Unsupported solution type: {solution['type']}")

    def execute_notebook(self, solution, submission_path):
        """
        Execute a student's Jupyter notebook submission and evaluate it
        against the instructor's structured solution specification.
        """
        # 1. Execute student's notebook safely
        executor = NotebookExecutor(timeout=self.timeout)
        student_execution = executor.run_notebook(submission_path)
        student_namespace = student_execution["namespace"]

        comparator = ComparisonService()
        all_results = []

        # 2. Iterate over each question defined in the instructor notebook
        for qname, qdata in solution.get("questions", {}).items():
            context_code = qdata.get("context_code", "")
            assertions = qdata.get("tests", [])

            # Run context/setup code inside student's namespace
            if context_code:
                try:
                    exec(context_code, student_namespace)
                except Exception:
                    err = traceback.format_exc()
                    student_execution["errors"].append(
                        f"[{qname}] Setup failed:\n{err}"
                    )

            # Run each assertion and collect results
            if assertions:
                q_results = comparator.run_assertions(
                    student_namespace=student_namespace,
                    assertions=assertions,
                    question_name=qname,
                )

                # attach description to each result
                desc = qdata.get("description", "")
                for r in q_results:
                    r["description"] = desc
                all_results.extend(q_results)


        # 3. Return structured evaluation
        return {
            "student_path": submission_path,
            "execution": student_execution,
            "results": all_results,
        }
