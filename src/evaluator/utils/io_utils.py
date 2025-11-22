"""
IO utilities for reading, writing, and managing files and folders.
"""
import json
from pathlib import Path
import pandas as pd
import nbformat
from openpyxl import load_workbook

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



def read_file(path):
  """Read a file from the given path."""
  pass

def write_file(path, data):
  """Write data to a file at the given path."""
  pass

def safe_json_dump(path, data):
  """Safely dump JSON data to a file."""
  pass

def create_folder(path):
  """Create a folder at the given path if it does not exist."""
  pass

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

