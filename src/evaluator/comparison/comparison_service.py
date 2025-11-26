import traceback


class ComparisonService:
    """
    Compares student execution results against instructor-defined assertions.
    """

    def run_assertions(
        self,
        student_namespace: dict,
        assertions: list[str],
        question_name: str | None = None,
        context_code: str | None = None,
    ) -> list[dict]:
        """
        Execute instructor assertions in the student's namespace.

        Parameters
        ----------
        student_namespace : dict
            Namespace of the student's executed notebook.
        assertions : list[str]
            Assertion statements to run.
        question_name : str, optional
            Name of the question/function being evaluated.
        context_code : str, optional
            Setup code to run once before assertions (imports, data prep, etc.)

        Returns
        -------
        list[dict]
        """
        results: list[dict] = []

        # 1. Execute setup/context code once
        if context_code:
            try:
                exec(context_code, student_namespace)
            except Exception:
                tb = traceback.format_exc()
                results.append({
                    "question": question_name or "unknown",
                    "assertion": "[context setup]",
                    "status": "failed",
                    "error": tb,
                    "score": 0,
                })
                # If setup fails, we cannot reliably run assertions
                return results

        # 2. Execute each assertion separately
        for code in assertions:
            try:
                exec(code, student_namespace)
                results.append({
                    "question": question_name or "unknown",
                    "assertion": code,
                    "status": "passed",
                    "error": None,
                    "score": 1,
                })
            except Exception:
                tb = traceback.format_exc()
                results.append({
                    "question": question_name or "unknown",
                    "assertion": code,
                    "status": "failed",
                    "error": tb,
                    "score": 0,
                })

        return results
