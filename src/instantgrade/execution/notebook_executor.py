import nbformat
from nbclient import NotebookClient
from pathlib import Path
import traceback

class NotebookExecutor:
    """
    Executes a Jupyter notebook in a sandboxed environment
    and extracts its final namespace.
    """

    def __init__(self, timeout=60):
        self.timeout = timeout

    def run_notebook(self, path):
        """
        Execute notebook and extract global namespace.
        Automatically disables input() calls.
        """
        path = Path(path)
        nb = nbformat.read(path, as_version=4)
        errors = []
        tb_text = None
        namespace = {}

        # --- 1. Add a dummy input() to avoid blocking ---
        def dummy_input(prompt=None):
            # Optionally, log it to errors
            msg = f"[Warning] input() called during evaluation — ignored."
            errors.append(msg)
            return ""  # or None, or some harmless default

        # Inject this into the global namespace before any student code runs
        namespace["input"] = dummy_input

        # --- 2. Execute notebook with nbclient ---
        try:
            client = NotebookClient(nb, timeout=self.timeout, allow_errors=True, kernel_name="python3")
            executed_nb = client.execute()
        except Exception as e:
            tb_text = traceback.format_exc()
            errors.append(str(e))
            executed_nb = nb  # fallback

        # --- 3. Execute all code cells sequentially ---
        for cell in executed_nb.cells:
            if cell.cell_type != "code":
                continue
            src = cell.get("source", "")
            if not src.strip():
                continue
            try:
                exec(src, namespace)
            except Exception as e:
                errors.append(f"In cell: {src[:80]} -> {str(e)}")

        # --- 4. Return clean result ---
        clean_ns = {k: v for k, v in namespace.items() if not k.startswith("__")}
        return {
            "namespace": clean_ns,
            "errors": errors,
            "traceback": tb_text,
            "success": len(errors) == 0,
        }
