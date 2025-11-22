import traceback


class ComparisonService:
    """
    Service for comparing student execution with instructor solution.
    """

    def run_assertions(self, student_namespace, assertions):
        """
        Execute each instructor assertion against the student's namespace.
        Returns a list of dictionaries summarizing test results.
        """
        results = []

        for code in assertions:
            question_name = self._extract_question_name(code)

            try:
                exec(code, student_namespace)
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "passed",
                    "error": None,
                    "score": 1
                })
            except Exception:
                tb = traceback.format_exc()
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "failed",
                    "error": tb,
                    "score": 0
                })

        return results

    def _extract_question_name(self, assert_line):
        """
        Extracts the question function name from assertion:
            "assert question_one(2) == 4" → "question_one"
        """
        try:
            line = assert_line.replace("assert", "").strip()
            return line.split("(")[0].strip()
        except Exception:
            return "unknown"

    def compare(self, executed_result=None, solution_output=None, ast_report=None):
        """
        Placeholder for deeper comparisons (e.g., AST or value comparisons).
        Currently returns the executed_result as is.
        """
        return executed_result
