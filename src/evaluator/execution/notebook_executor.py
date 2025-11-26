"""
Notebook execution utilities for running and extracting results from Jupyter notebooks.
"""



import nbformat
from nbclient import NotebookClient
from pathlib import Path
import traceback


class NotebookExecutor:
    """
    Executes a Jupyter notebook in a sandboxed environment
    and extracts its namespace.
    """

    def __init__(self, timeout=60):
        self.timeout = timeout

    def run_notebook(self, path):
        """
        Execute notebook and extract global namespace.
        """
        path = Path(path)
        nb = nbformat.read(path, as_version=4)

        namespace = {}
        errors = []
        tb_text = None

        try:
            client = NotebookClient(
                nb,
                timeout=self.timeout,
                allow_errors=True,
                kernel_name="python3",
            )
            executed = client.execute()
        except Exception as e:
            tb_text = traceback.format_exc()
            errors.append(str(e))
            executed = nb  # fallback (unexecuted)

        # Extract variables by re-running all code cells in memory
        for cell in executed.cells:
            if cell.cell_type != "code":
                continue
            src = cell.get("source", "")
            try:
                exec(src, namespace)
            except Exception as e:
                errors.append(f"In cell: {src[:80]} -> {str(e)}")

        # Clean up builtins for safety
        clean_ns = {k: v for k, v in namespace.items() if not k.startswith("__")}

        return {
            "namespace": clean_ns,
            "errors": errors,
            "traceback": tb_text,
            "success": len(errors) == 0,
        }
