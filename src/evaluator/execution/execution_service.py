
from pathlib import Path
import traceback
import nbformat
from nbclient import NotebookClient

from evaluator.execution.notebook_executor import extract_namespace_from_notebook
from evaluator.utils.time_utils import now_timestamp



class ExecutionService:
    """
    Service for executing student code in a safe/controlled environment.
    """
    def execute(self, solution, submission):
        """Run the solution and submission (notebook or excel)."""
        pass

    def execute_notebook(self, solution, submission):
        """
        Execute a student's Jupyter notebook submission.

        Parameters
        ----------
        solution : dict
            Loaded solution object (contains functions + assertions).
        submission : dict
            Loaded submission object with:
                submission["type"] == "notebook"
                submission["notebook"] == nbformat.NotebookNode

        Returns
        -------
        dict 
            {
                "type": "notebook_execution",
                "path": Path,
                "namespace": {variables/functions after execution},
                "outputs": notebook (with outputs populated),
                "errors": list of error strings,
                "traceback": traceback text,
                "timestamp": "...",
                "success": True/False
            }
        """

        nb = submission["notebook"]
        path = submission["path"]

        errors = []
        traceback_text = None
        executed_notebook = None

        try:
            client = NotebookClient(
                nb,
                timeout=60,
                allow_errors=True,
                kernel_name="python3",
            )
            executed_notebook = client.execute()

        except Exception as e:
            # Execution failed at notebook level
            tb = traceback.format_exc()
            traceback_text = tb
            errors.append(str(e))

        # Extract namespace (variables + functions)
        namespace = extract_namespace_from_notebook(executed_notebook)

        return {
            "type": "notebook_execution",
            "path": path,
            "namespace": namespace,
            "outputs": executed_notebook,
            "errors": errors,
            "traceback": traceback_text,
            "timestamp": now_timestamp(),
            "success": len(errors) == 0,
        }

    def execute_excel(self, solution, submission):
        """Run an excel solution and submission."""
        pass

    def collect_outputs(self, executed_object):
        """Collect outputs from the executed object."""
        pass

    def handle_errors(self, error):
        """Handle errors during execution."""
        pass

# --- The following methods do not fit the new architecture and are commented out ---
# from .notebook_executor import run_notebook
# from .excel_executor import run_excel
