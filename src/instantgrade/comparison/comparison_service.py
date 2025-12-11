"""
comparison_service_v2.py

Improved ComparisonService for auto-grader.

Returned result item format (per assertion):
{
    "question": <question_name>,
    "assertion": <assertion_code_str>,
    "status": "passed" | "failed",
    "score": 1 or 0,
    "error": <clean multiline string for UI display> or None,
    "debug_traceback": <full traceback string> or None  # included only when debug=True
}
"""

from typing import List, Dict, Optional, Any, Tuple
import ast
import html as html_lib
import traceback
import builtins
import copy


def _extract_assertion_line(code: str) -> str:
    """Return the first line that starts with 'assert' or whole code if none."""
    for line in code.splitlines():
        if line.strip().startswith("assert"):
            return line.strip()
    return code.strip()


def _parse_simple_equality_assertion(code: str) -> Optional[Tuple[str, str]]:
    """
    Parse "assert <left> == <right>" and return (left, right) strings using ast.unparse.
    Returns None when code isn't a simple equality assert.
    """
    try:
        node = ast.parse(code)
        stmt = node.body[0]
        if not isinstance(stmt, ast.Assert):
            return None
        test = stmt.test
        # match Compare node with Eq operator and single comparator
        if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
            left_expr = ast.unparse(test.left)
            right_expr = ast.unparse(test.comparators[0])
            return left_expr, right_expr
    except Exception:
        # any parser error -> fallback to None
        return None
    return None


class ComparisonService:
    def __init__(
        self,
        solution: Optional[Dict[str, Any]] = None,
        inject_solution: bool = True,
        debug: bool = False,
    ):
        """
        :param solution: mapping of symbol name -> python object (instructor solution).
                         These will be injected into the evaluation namespace when missing.
        :param inject_solution: if True, missing names in student namespace will be populated
                                from `solution` before assertions run.
        :param debug: if True, include full tracebacks in result items as `debug_traceback`.
        """
        self.solution = solution or {}
        self.inject_solution = bool(inject_solution)
        self.debug = bool(debug)

    # ----------------------------
    # Evaluation helpers
    # ----------------------------
    def _safe_eval_in_ns(self, expr: str, ns: dict) -> Tuple[Any, Optional[str]]:
        """
        Evaluate an expression in `ns`. Return (value, None) on success,
        or (None, error_message) on failure. We deliberately don't suppress
        exceptions silently; we return the stringified exception for formatting.
        """
        try:
            value = eval(expr, ns)
            return value, None
        except Exception as exc:  # capture any runtime evaluation error
            return None, f"{type(exc).__name__}: {str(exc)}"

    def _format_assertion_failure(self, code: str, ae: AssertionError, ns_for_eval: dict) -> str:
        """
        Produce a human-friendly message for failed assertions.
        If the assertion is of form `assert <left> == <right>`, attempt to evaluate
        and show Expected vs Actual. Otherwise, show assertion + message if present.
        """
        assertion_line = _extract_assertion_line(code)
        parsed = _parse_simple_equality_assertion(assertion_line)

        if parsed:
            left_expr, right_expr = parsed
            left_val, left_err = self._safe_eval_in_ns(left_expr, ns_for_eval)
            right_val, right_err = self._safe_eval_in_ns(right_expr, ns_for_eval)

            if left_err:
                return (
                    "Assertion failed.\n"
                    f"Could not evaluate left expression: {left_expr}\n"
                    f"Error: {left_err}"
                )
            if right_err:
                return (
                    "Assertion failed.\n"
                    f"Could not evaluate right expression: {right_expr}\n"
                    f"Error: {right_err}"
                )

            # build difference information for common containers
            diff = ""
            try:
                if isinstance(left_val, list) and isinstance(right_val, list):
                    diff = f"Difference: expected {len(right_val)} items, got {len(left_val)} items."
                elif isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                    diff = f"Difference: expected {right_val!r}, got {left_val!r}."
                # further heuristics can be added here (dict keys, set symmetric diff, etc.)
            except Exception:
                diff = ""

            return (
                "Assertion failed.\n"
                f"Assertion: {assertion_line}\n"
                f"Expected: {right_val!r}\n"
                f"Actual:   {left_val!r}\n"
                f"{diff}"
            )

        # non-equality assert: try to show provided message in AssertionError, else raw assertion
        if ae.args:
            return (
                "Assertion failed.\n"
                f"Assertion: {assertion_line}\n"
                f"Message: {ae.args[0]}"
            )

        return f"Assertion failed.\nAssertion: {assertion_line}"

    def _format_general_exception(self, code: str, exc: Exception) -> str:
        """Human-friendly wrapper for runtime errors (NameError, TypeError, etc.)."""
        return (
            "Execution error.\n"
            f"Code: {code.strip()}\n"
            f"Error: {type(exc).__name__}: {str(exc)}"
        )

    # ----------------------------
    # Public API
    # ----------------------------
    def run_assertions(
        self,
        student_namespace: Dict[str, Any],
        assertions: List[str],
        question_name: Optional[str] = None,
        context_code: Optional[str] = None,
        timeout: Optional[int] = None,  # timeout reserved for future extension
    ) -> List[Dict]:
        """
        Execute assertions against the student's namespace.

        :param student_namespace: dictionary already populated by running student's file.
        :param assertions: list of assertion strings (e.g. ["assert f(1)==2", ...])
        :param question_name: optional label for the question
        :param context_code: optional helper code executed before assertions (executed once)
        :param timeout: not implemented here (reserved); keep None to avoid complexity
        :return: list of result dicts (one per assertion)
        """
        # Work on a shallow copy to avoid mutating caller's dict
        base_ns = dict(student_namespace or {})

        # Optionally inject instructor solution objects (only when missing)
        if self.inject_solution and self.solution:
            for name, obj in self.solution.items():
                if name not in base_ns:
                    base_ns[name] = obj

        results: List[Dict] = []

        # Execute optional context_code (once). Use base_ns, and capture exceptions cleanly.
        if context_code:
            try:
                exec(compile(context_code, "<context>", "exec"), base_ns)
            except Exception as exc:
                tb = traceback.format_exc()
                results.append({
                    "question": question_name,
                    "assertion": "[context]",
                    "status": "failed",
                    "score": 0,
                    "error": f"Context setup failed: {type(exc).__name__}: {str(exc)}",
                    "debug_traceback": tb if self.debug else None,
                })
                # If context fails we stop running assertions for this question
                return results

        # Run each assertion in an isolated execution namespace derived from base_ns.
        # Isolation prevents one assertion from mutating globals that affect later assertions.
        for code in assertions:
            ns_for_assert = dict(base_ns)  # shallow copy is sufficient for typical functions/values

            try:
                # compile first to surface syntax errors clearly
                compiled = compile(code, "<assertion>", "exec")
                exec(compiled, ns_for_assert)

                # If no exception -> passed
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "passed",
                    "score": 1,
                    "error": None,
                    "debug_traceback": None
                })

            except AssertionError as ae:
                # Format failed assertion with helpful info (expected vs actual if possible)
                clean_msg = self._format_assertion_failure(code, ae, ns_for_assert)
                tb = traceback.format_exc()
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "failed",
                    "score": 0,
                    "error": clean_msg,
                    "debug_traceback": tb if self.debug else None
                })

            except Exception as exc:
                # NameError, TypeError, SyntaxError, etc. - preserve the real exception type/message
                clean_msg = self._format_general_exception(code, exc)
                tb = traceback.format_exc()
                results.append({
                    "question": question_name,
                    "assertion": code,
                    "status": "failed",
                    "score": 0,
                    "error": clean_msg,
                    "debug_traceback": tb if self.debug else None
                })

        return results


# ----------------------------
# Example quick test (not executed automatically when imported)
# ----------------------------
if __name__ == "__main__":
    # Instructor solution (optional)
    solution = {
        "check_number": lambda x: "positive" if x > 0 else ("negative" if x < 0 else "zero")
    }

    # Student namespace: student forgot to define check_number
    student_ns = {"__name__": "__student__"}

    assertions = [
        "assert check_number(10) == 'positive'",
        "assert check_number(-5) == 'negative'",
        "assert check_number(0) == 'zero'"
    ]

    svc = ComparisonService(solution=solution, inject_solution=True, debug=True)
    res = svc.run_assertions(student_namespace=student_ns, assertions=assertions, question_name="check_number")
    from pprint import pprint
    pprint(res)
