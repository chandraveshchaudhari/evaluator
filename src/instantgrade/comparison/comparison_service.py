print(">>> USING FINAL CLEAN ComparisonService <<<")

from typing import List, Dict, Optional
import ast


def extract_assertion_line(code: str) -> str:
    for line in code.splitlines():
        if line.strip().startswith("assert"):
            return line.strip()
    return code.strip()


def parse_assertion(code: str):
    """Parse only assert A == B expressions."""
    try:
        node = ast.parse(code)
        stmt = node.body[0]
        if isinstance(stmt, ast.Assert):
            test = stmt.test
            if isinstance(test, ast.Compare) and isinstance(test.ops[0], ast.Eq):
                left = ast.unparse(test.left)
                right = ast.unparse(test.comparators[0])
                return left, right
    except Exception:
        pass
    return None


class ComparisonService:

    # -------------------------------------------------------------
    # Safe eval that NEVER throws traceback
    # -------------------------------------------------------------
    def _safe_eval(self, expr: str, ns: dict):
        try:
            return eval(expr, ns), None
        except Exception as exc:
            return None, str(exc)

    # -------------------------------------------------------------
    # Assertion formatting (clean)
    # -------------------------------------------------------------
    def _format_assertion_error(self, code: str, ae: AssertionError, ns: dict):
        assertion = extract_assertion_line(code)
        parsed = parse_assertion(assertion)

        # ---------- Case 1: assert A == B ----------
        if parsed:
            left_expr, right_expr = parsed

            actual, err1 = self._safe_eval(left_expr, ns)
            expected, err2 = self._safe_eval(right_expr, ns)

            if err1:
                return (
                    "Assertion failed.\n"
                    f"Could not evaluate left expression: {left_expr}\n"
                    f"Error: {err1}"
                )

            if err2:
                return (
                    "Assertion failed.\n"
                    f"Could not evaluate right expression: {right_expr}\n"
                    f"Error: {err2}"
                )

            diff = ""
            if isinstance(actual, list) and isinstance(expected, list):
                diff = f"Difference: expected {len(expected)} items, got {len(actual)} items."

            return (
                "Assertion failed.\n"
                f"Assertion: {assertion}\n"
                f"Expected: {expected}\n"
                f"Actual:   {actual}\n"
                f"{diff}"
            )

        # ---------- Case 2: no == compare ----------
        if ae.args:
            return (
                "Assertion failed.\n"
                f"Assertion: {assertion}\n"
                f"Message: {ae.args[0]}"
            )

        return (
            "Assertion failed.\n"
            f"Assertion: {assertion}"
        )

    # -------------------------------------------------------------
    # General runtime error formatter
    # -------------------------------------------------------------
    def _format_general_error(self, code: str, exc: Exception):
        return (
            "Execution error.\n"
            f"Code: {code.strip()}\n"
            f"Error: {str(exc)}"
        )

    # -------------------------------------------------------------
    # MAIN FUNCTION
    # -------------------------------------------------------------
    def run_assertions(
        self,
        student_namespace: dict,
        assertions: List[str],
        question_name: Optional[str] = None,
        context_code: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> List[Dict]:

        ns = student_namespace
        results = []

        # ---------------------------------------------------------
        # 1. Run context code
        # ---------------------------------------------------------
        if context_code:
            try:
                exec(compile(context_code, "<context>", "exec"), ns)
            except Exception as exc:
                results.append({
                    "question": question_name,
                    "assertion": "[context]",
                    "status": "failed",
                    "error": f"Context setup failed: {str(exc)}",
                    "score": 0,
                })
                return results

        # ---------------------------------------------------------
        # 2. Run each assertion
        # ---------------------------------------------------------
        for code in assertions:

            try:
                exec(compile(code, "<assertion>", "exec"), ns)

                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "passed",
                    "error": None,
                    "score": 1,
                })

            except AssertionError as ae:
                clean = self._format_assertion_error(code, ae, ns)
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "failed",
                    "error": clean,
                    "score": 0,
                })

            except Exception as exc:
                clean = self._format_general_error(code, exc)
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "failed",
                    "error": clean,
                    "score": 0,
                })

        return results
