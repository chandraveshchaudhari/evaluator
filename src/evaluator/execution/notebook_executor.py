"""
Sandbox environment for executing instructor and student code.
"""

"""
Notebook execution utilities for running and extracting results from Jupyter notebooks.
"""


import ast
import nbformat
import nbformat
from nbclient import NotebookClient
from pathlib import Path
import traceback


class NotebookExecutor:
    """
    Utilities for executing Jupyter notebooks and extracting results.
    """

    def __init__(self, timeout=60):
        self.timeout = timeout

    def run_notebook(self, path):
        """
        Execute the notebook at 'path' and return a dict containing:
            {
                "namespace": {var_name: value, ...},
                "errors": [list of errors],
                "traceback": str,
                "success": bool
            }
        """
        path = Path(path)
        nb = nbformat.read(path, as_version=4)

        errors = []
        tb_text = None
        namespace = {}

        try:
            client = NotebookClient(nb, timeout=self.timeout, allow_errors=True, kernel_name="python3")
            executed = client.execute()
        except Exception as e:
            tb_text = traceback.format_exc()
            errors.append(str(e))
            executed = nb  # fallback, unexecuted

        # Extract final namespace by executing all code in memory
        for cell in executed.cells:
            if cell.cell_type != "code":
                continue
            src = cell.get("source", "")
            try:
                exec(src, namespace)
            except Exception as e:
                errors.append(f"In cell: {src[:60]} -> {str(e)}")

        return {
            "namespace": {k: v for k, v in namespace.items() if not k.startswith("__")},
            "errors": errors,
            "traceback": tb_text,
            "success": len(errors) == 0,
        }
