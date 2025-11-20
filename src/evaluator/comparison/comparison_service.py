import traceback


class ComparisonService:
    """
    Service for comparing student execution with solution execution and AST analysis.
    """

    def run_assertions(self, student_namespace, assertions):
        """
        Execute each instructor assertion against the student's namespace.

        Parameters
        ----------
        student_namespace : dict
            Variables, functions, and objects extracted from student notebook.
        assertions : list[str]
            Assertion statements from instructor solution (e.g. "assert question_one(2) == 4")

        Returns
        -------
        list[dict] representing comparison results:
        [
            {
                "assertion": "assert question_one(2) == 4",
                "status": "passed" / "failed",
                "error": None or traceback,
                "question": "question_one",
                "score": 1 or 0
            }
        ]
        """

        results = []

        for code in assertions:
            question_name = _extract_question_name(code)

            try:
                # Execute the assertion in the student's namespace
                exec(code, student_namespace)
                results.append({
                    "assertion": code,
                    "question": question_name,
                    "status": "passed",
                    "error": None,
                    "score": 1
                })

            except Exception:
                tb = traceback.format_exc()
                results.append({
                    "assertion": code,
                    "question": question_name,
                    "status": "failed",
                    "error": tb,
                    "score": 0
                })

        return results



    def _extract_question_name(assert_line):
        """
        Extracts question function name from assertion:
            "assert question_one(2) == 4" → "question_one"
        """
        try:
            # simple splitting method
            after_assert = assert_line.replace("assert", "").strip()
            func_name = after_assert.split("(")[0].strip()
            return func_name
        except:
            return "unknown"

    
    def compare(self, executed_result, solution_output, ast_report):
        """Compare executed result, solution output, and AST report."""
        pass

    def compare_python(self, executed_student, executed_solution):
        """Compare Python execution results."""
        pass

    def compare_excel(self, student_wb, solution_wb):
        """Compare Excel workbooks."""
        pass

    def merge_results(self, results_list):
        """Merge a list of comparison results."""
        pass

    def apply_scoring_rules(self, results, rules):
        """Apply scoring rules to comparison results."""
        pass

# --- The following methods do not fit the new architecture and are commented out ---
# class Compare: ...
# from .notebook_compare import compare_notebook
# from .excel_compare import compare_excel
