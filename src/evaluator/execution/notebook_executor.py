"""
Sandbox environment for executing instructor and student code.
"""

class ExecutionSandbox:
    """
    Provides a safe environment for running dynamically loaded code.
    """

    def __init__(self):
        self.env = {}  # Execution namespace

    def load_function(self, func_source: str):
        """Exec function source into the sandbox namespace."""
        exec(func_source, self.env)

    def run_assertion(self, assertion: str):
        """Run a single assertion inside sandbox."""
        exec(assertion, self.env)  # wrapped by try/except in the runner




"""Capture outputs from executed notebooks.

Normalize printed output, execution results and extract plain-text DataFrame
representations where possible.
"""
from __future__ import annotations
from typing import Dict, Any, List


def capture_outputs(nb) -> Dict[str, Any]:
    """Scan executed notebook object and return structured outputs.

    Returns keys: printed (str), results (list), dataframes (list of dicts)
    """
    printed: List[str] = []
    results: List[Dict[str, Any]] = []
    dataframes: List[Dict[str, Any]] = []

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "stream":
                printed.append(out.get("text", ""))
            elif out.get("output_type") in ("execute_result", "display_data"):
                data = out.get("data", {})
                text = data.get("text/plain") or out.get("text") or None
                results.append({"text": text, "data_keys": list(data.keys())})
                # crude heuristic: if dataframe printed, include small preview
                if text and "DataFrame" in text:
                    dataframes.append({"preview": text.splitlines()[:10]})

    return {"printed": "\n".join(printed), "results": results, "dataframes": dataframes}

"""Execute notebooks safely using nbclient.

This module provides a thin wrapper around nbclient.NotebookClient to execute
notebooks with a timeout. True sandboxing (blocking syscalls and network)
should be enforced externally (containerization). This wrapper documents the
limitations and enforces timeouts.
"""
from __future__ import annotations
from typing import Dict, Any
import nbformat
from nbclient import NotebookClient


class NotebookExecutionError(Exception):
    """Raised when notebook execution fails."""


def run_notebook(notebook_path: str, timeout: int = 120) -> Dict[str, Any]:
    """Execute a notebook and return execution metadata and the executed nb.

    Returns dict: {"ok": bool, "nb": nbformat.NotebookNode, "error": optional str}
    """
    nb = nbformat.read(notebook_path, as_version=4)
    try:
        client = NotebookClient(nb, timeout=timeout, kernel_name="python3")
        client.execute()
    except Exception as e:
        return {"ok": False, "nb": nb, "error": str(e)}
    return {"ok": True, "nb": nb}


"""
Sandbox environment for executing instructor and student code.
"""

class ExecutionSandbox:
    """
    Provides a safe environment for running dynamically loaded code.
    """

    def __init__(self):
        self.env = {}  # Execution namespace

    def load_function(self, func_source: str):
        """Exec function source into the sandbox namespace."""
        exec(func_source, self.env)

    def run_assertion(self, assertion: str):
        """Run a single assertion inside sandbox."""
        exec(assertion, self.env)  # wrapped by try/except in the runner


"""
Runs extracted test cases against student functions.
"""

import traceback

class AssertionRunner:
    """
    Executes assertions and collects errors without stopping.
    """

    @staticmethod
    def run_assertions(assertions, sandbox):
        results = []

        for test in assertions:
            try:
                sandbox.run_assertion(test)
                results.append({"assertion": test, "passed": True, "error": None})
            except Exception as e:
                results.append({
                    "assertion": test,
                    "passed": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        return results


"""
Main evaluator orchestrator.
Coordinates ingestion, parsing, execution, and reporting.
"""

class EvaluatorCore:
    """
    High-level pipeline orchestrator.
    """

    def __init__(self, instructor_spec, student_spec):
        self.instructor_spec = instructor_spec
        self.student_spec = student_spec

    def evaluate(self):
        """
        Run full evaluation for one student.
        Returns dictionary of results:
        { question_name: { passed, failed, errors } }
        """
        results = {}

        for qname, spec in self.instructor_spec.items():
            sandbox = spec["sandbox"]
            assertions = spec["assertions"]

            student_func = self.student_spec.get(qname)

            if student_func:
                sandbox.load_function(student_func)

            assertion_results = spec["runner"].run_assertions(assertions, sandbox)
            results[qname] = assertion_results

        return results


