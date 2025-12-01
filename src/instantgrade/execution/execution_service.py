from instantgrade.execution.notebook_executor import NotebookExecutor
from instantgrade.comparison.comparison_service import ComparisonService
import copy


class ExecutionService:
    """
    Executes student notebooks and evaluates them against instructor tests.
    """

    def __init__(self, timeout: int = 60, debug: bool = False):
        self.timeout = timeout
        self.debug = debug

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
        base_namespace = student_execution.get("namespace", {})

        comparator = ComparisonService()
        all_results = []

        # 2. Iterate over each question defined in the instructor notebook
        for qname, qdata in solution.get("questions", {}).items():
            context_code = qdata.get("context_code", "")
            assertions = qdata.get("tests", [])
            description = qdata.get("description", "")

            if self.debug:
                print(f"\n[ExecutionService] Evaluating question: {qname}")
                print(f"  context_code length: {len(context_code)} chars")
                print(f"  assertions: {len(assertions)}")

            # Create a shallow copy of namespace so questions do not interfere
            question_namespace = copy.copy(base_namespace)

            # 3. Run context + assertions via ComparisonService
            q_results = comparator.run_assertions(
                student_namespace=question_namespace,
                assertions=assertions,
                question_name=qname,
                context_code=context_code,
            )

            # Attach description for reporting
            for r in q_results:
                r["description"] = description

            all_results.extend(q_results)

        # 4. Return structured evaluation dict
        return {
            "student_path": submission_path,
            "execution": student_execution,
            "results": all_results,
        }
