"""
IO utilities for reading, writing, and managing files and folders.
"""
import json
from pathlib import Path
import pandas as pd
import nbformat
from openpyxl import load_workbook
import nbformat
import ast
from pathlib import Path
from nbformat import validate, ValidationError

import nbformat
from nbformat import validate, ValidationError
import nbformat
from nbformat import validate, ValidationError
from uuid import uuid4

def safe_load_notebook(path):
    """
    Safely read a Jupyter notebook and ensure each cell has an 'id' field.
    Compatible with all nbformat versions (no normalize()).
    Fixes structure in memory only — does not modify the file.
    """
    try:
        nb = nbformat.read(path, as_version=4)

        # Manually ensure IDs exist for all cells
        modified = False
        for cell in nb.cells:
            if "id" not in cell:
                cell["id"] = str(uuid4())
                modified = True

        # Try validating the notebook
        try:
            validate(nb)
        except ValidationError:
            # Upgrade schema if older version
            nb = nbformat.v4.upgrade(nb)
            validate(nb)

        # (Optional) Log in debug mode if any IDs were added
        if modified:
            print(f"[safe_load_notebook] Added missing IDs in memory for {path.name}")

        return nb

    except Exception as e:
        raise RuntimeError(f"Unable to load notebook {path}: {e}")


def normalize_notebook(path=None, inplace: bool = True) -> nbformat.NotebookNode:
    """
    Normalize a Jupyter notebook by ensuring every cell has a unique 'id' field.
    This prevents MissingIDFieldWarning in nbformat >=5.1.4.

    Parameters
    ----------
    path : str | Path
        Path to the notebook (.ipynb).
    inplace : bool
        If True, overwrite the notebook in place; else return the normalized object.

    Returns
    -------
    nb : nbformat.NotebookNode
        The normalized notebook object.
    """
    path = Path(path)
    nb = nbformat.read(path, as_version=4)

    # Add missing IDs if needed
    nbformat.validate(nb)  # may warn, but we fix below
    normalized_nb = nbformat.v4.upgrade(nb)
    nbformat.v4.validate_cell_ids(normalized_nb)

    if inplace:
        nbformat.write(normalized_nb, path)
        return normalized_nb

    return normalized_nb


def load_notebook(path):
    return nbformat.read(path, as_version=4)

def load_excel(path):
    return load_workbook(path, data_only=False)

def load_json(path):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def load_csv(path):
    return pd.read_csv(path)

def load_raw_code(path):
    return Path(path).read_text(encoding="utf8")

import ast
import nbformat
from pathlib import Path


def generate_student_notebook(instructor_path: str | Path, output_path: str | Path):
    """
    Create a student version of an instructor Jupyter notebook by:
      - Replacing all function bodies with 'pass'
      - Removing any code cell that contains assertions
      - Optionally removing inline assert statements (if present)
      - Keeping Markdown cells and overall structure identical

    Parameters
    ----------
    instructor_path : str | Path
        Path to the instructor's notebook (.ipynb)
    output_path : str | Path
        Destination path for the student version (.ipynb)
    """
    instructor_path = Path(instructor_path)
    output_path = Path(output_path)

    if not instructor_path.exists():
        raise FileNotFoundError(f"Notebook not found: {instructor_path}")

    nb = nbformat.read(instructor_path, as_version=4)
    new_cells = []

    for cell in nb.cells:
        # --- Keep markdown cells as is ---
        if cell.cell_type == "markdown":
            new_cells.append(cell)
            continue

        if cell.cell_type != "code":
            # Just in case other cell types appear
            new_cells.append(cell)
            continue

        src = cell.source or ""
        stripped_lines = [l.strip() for l in src.splitlines() if l.strip()]

        # --- NEW: drop any code cell that contains an assert line ---
        if any(line.startswith("assert ") for line in stripped_lines):
            # This is considered a test/assert cell → remove entirely
            continue

        # From here on, we are in a non-assert code cell (e.g., function definitions)
        try:
            tree = ast.parse(src)
            new_body: list[ast.stmt] = []

            for node in tree.body:
                # Replace function implementations with stubs
                if isinstance(node, ast.FunctionDef):
                    node.body = [ast.Pass()]
                    new_body.append(node)

                # Keep top-level imports, assignments, and expressions
                elif isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.Expr)):
                    new_body.append(node)

                # Ignore anything else (for safety), or you can choose to keep it

            # Rebuild the code cell
            new_module = ast.Module(body=new_body, type_ignores=[])
            new_source = ast.unparse(new_module).strip()

            if new_source:
                cell.source = new_source
                new_cells.append(cell)

        except Exception:
            # Fallback: keep non-assert lines only, and still replace functions if desired
            cleaned_lines = []
            for line in src.splitlines():
                stripped = line.strip()
                # drop any inline assert as an extra safeguard
                if stripped.startswith("assert "):
                    continue
                cleaned_lines.append(line)

            new_src = "\n".join(cleaned_lines).strip()
            if new_src:
                cell.source = new_src
                new_cells.append(cell)

    # --- Rebuild notebook ---
    new_nb = nbformat.v4.new_notebook()
    new_nb.cells = new_cells
    new_nb.metadata = nb.metadata

    output_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(new_nb, output_path)
    print(f"✅ Student notebook generated at: {output_path}")
