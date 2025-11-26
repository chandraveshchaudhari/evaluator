import traceback


class ComparisonService:
    """
    Compares student execution results against instructor-defined assertions.
    """

    def run_assertions(self, student_namespace, assertions, question_name=None):
        """
        Execute each instructor assertion in the student's namespace.

        Parameters
        ----------
        student_namespace : dict
            Namespace of student's executed notebook.
        assertions : list[str]
            Assertion statements to run.
        question_name : str, optional
            The question/function name these assertions belong to.

        Returns
        -------
        list[dict] : results with keys:
            - question
            - assertion
            - status ('passed'/'failed')
            - score (1/0)
            - error (traceback or None)
        """
        results = []

        for code in assertions:
            try:
                exec(code, student_namespace)
                results.append({
                    "question": question_name or "unknown",
                    "assertion": code,
                    "status": "passed",
                    "error": None,
                    "score": 1
                })
            except Exception:
                tb = traceback.format_exc()
                results.append({
                    "question": question_name or "unknown",
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
