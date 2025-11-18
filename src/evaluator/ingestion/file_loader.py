"""
Generic file loading utilities.
Supports notebooks, Excel, and extensible to other formats.
"""

from pathlib import Path
import nbformat
import pandas as pd

class FileLoader:
    """
    Loads raw assignment files from disk.

    Future support: Python scripts, R scripts, CSV-based code, SQL, JSON.
    """

    @staticmethod
    def load_notebook(path: Path):
        """Load a Jupyter notebook and return nbformat NotebookNode."""
        with open(path, "r", encoding="utf-8") as f:
            return nbformat.read(f, as_version=4)

    @staticmethod
    def load_excel(path: Path):
        """Load Excel file into pandas DataFrame dictionary."""
        return pd.read_excel(path, sheet_name=None)

    @staticmethod
    def load_raw_file(path: Path):
        """Generic raw file loader for future formats."""
        return Path(path).read_text(encoding="utf-8")

from __future__ import annotations
from typing import List, Dict, Any
import os
import json
import openpyxl


SUPPORTED_EXTENSIONS = {"ipynb", "xlsx", "csv"}


class FileLoadError(Exception):
    """Raised when a file cannot be loaded or validated."""


def _validate_filename(name: str) -> bool:
    """Validate filename conventions: only letters, numbers, -, _ and . allowed.

    Returns True if valid, False otherwise.
    """
    # simple validation; tune regex if needed
    import re

    return bool(re.match(r"^[\w\-. ]+$", name))


def detect_submission_files(folder_path: str) -> List[Dict[str, Any]]:
    """Scan a folder and return metadata for supported submission files.

    Returns a list of dicts with keys: path, name, ext, valid_name
    """
    if not os.path.isdir(folder_path):
        raise FileLoadError(f"Not a directory: {folder_path}")

    results: List[Dict[str, Any]] = []
    for name in os.listdir(folder_path):
        path = os.path.join(folder_path, name)
        if not os.path.isfile(path):
            continue
        _, ext = os.path.splitext(name)
        ext = ext.lstrip(".").lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue
        results.append({"path": path, "name": name, "ext": ext, "valid_name": _validate_filename(name)})

    return results


def load_file(path: str) -> Dict[str, Any]:
    """Load a file and return a standardized structure with content and metadata.

    For large files we return just a path + metadata. For small text files we
    include content. The caller can decide how to parse the content.
    """
    if not os.path.exists(path):
        raise FileLoadError(f"File not found: {path}")

    name = os.path.basename(path)
    _, ext = os.path.splitext(name)
    ext = ext.lstrip(".").lower()
    metadata = {"path": path, "name": name, "ext": ext}

    if ext in ("py", "csv", "ipynb"):
        # safe to load as text
        with open(path, "r", encoding="utf8") as f:
            content = f.read()
        metadata["content"] = content
    else:
        metadata["content"] = None

    return metadata
