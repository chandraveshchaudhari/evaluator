from instantgrade.execution.notebook_executor import NotebookExecutor
from instantgrade.comparison.comparison_service import ComparisonService
import copy
import logging

logger = logging.getLogger(__name__)


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
        logger.info(f"  📓 Loading student notebook: {submission_path.name}")

        # 1. Execute student's notebook safely
        executor = NotebookExecutor(timeout=self.timeout)
        try:
            student_execution = executor.run_notebook(submission_path)
            logger.info(f"    ✅ Notebook executed successfully")
        except Exception as e:
            logger.error(f"    ❌ ERROR executing notebook: {str(e)}")
            raise

        base_namespace = student_execution.get("namespace", {})
        logger.info(f"    📊 Namespace variables available: {len(base_namespace)}")

        comparator = ComparisonService()
        all_results = []

        # 2. Iterate over each question defined in the instructor notebook
        total_questions = len(solution.get("questions", {}))
        logger.info(f"    ❓ Total questions to evaluate: {total_questions}")

        for q_idx, (qname, qdata) in enumerate(solution.get("questions", {}).items(), 1):
            context_code = qdata.get("context_code", "")
            assertions = qdata.get("tests", [])
            description = qdata.get("description", "")

            logger.info(f"    [{q_idx}/{total_questions}] 📝 Question: {qname}")
            logger.info(f"        Description: {description[:50]}..." if len(description) > 50 else f"        Description: {description}")
            logger.info(f"        Tests/Assertions: {len(assertions)}")

            if self.debug:
                logger.debug(f"      Context code length: {len(context_code)} chars")

            # Create a shallow copy of namespace so questions do not interfere
            question_namespace = copy.copy(base_namespace)

            # 3. Run context + assertions via ComparisonService
            try:
                q_results = comparator.run_assertions(
                    student_namespace=question_namespace,
                    assertions=assertions,
                    question_name=qname,
                    context_code=context_code,
                )

                # Count passed/failed
                passed = sum(1 for r in q_results if r.get("status") == "passed")
                failed = len(q_results) - passed
                logger.info(f"        Result: ✅ {passed} passed, ❌ {failed} failed")

            except Exception as e:
                logger.error(f"        ❌ ERROR evaluating question {qname}: {str(e)}")
                q_results = [{
                    "question": qname,
                    "assertion": "N/A",
                    "status": "error",
                    "error": str(e),
                    "score": 0,
                }]

            # Attach description for reporting
            for r in q_results:
                r["description"] = description

            all_results.extend(q_results)

        logger.info(f"    ✅ Evaluation complete for {submission_path.name}")

        # 4. Return structured evaluation dict
        return {
            "student_path": submission_path,
            "execution": student_execution,
            "results": all_results,
        }
