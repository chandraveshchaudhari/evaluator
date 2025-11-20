"""
Sandbox environment for executing instructor and student code.
"""

"""
Notebook execution utilities for running and extracting results from Jupyter notebooks.
"""


import ast
import nbformat


def extract_namespace_from_notebook(nb):
    """
    Extract variables and functions from executed notebook cells.

    Approach:
        - Identify all code cells
        - Execute them inside a shared python namespace dict
        - Return the final namespace after execution
    """

    namespace = {}

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue

        source = cell.get("source", "")

        try:
            exec(source, namespace)  # safe if notebook is executed already
        except Exception:
            # Ignore cell-level errors (already recorded by ExecutionService)
            pass

    return {k: v for k, v in namespace.items() if not k.startswith("__")}





def run_notebook(path):
    """Run a notebook from the given path."""
    pass

def execute_cell(code, timeout=10):
    """Execute a single code cell with a timeout."""
    pass

def run_with_nbclient(nb_path):
    """Run a notebook using nbclient."""
    pass

def extract_variables(nb):
    """Extract variables from a notebook object."""
    pass

def extract_cell_outputs(nb):
    """Extract outputs from all cells in a notebook object."""
    pass

def extract_exception_traces(nb):
    """Extract exception traces from a notebook object."""
    pass

def sanitize_notebook(nb):
    """Sanitize a notebook object (remove outputs, etc)."""
    pass

