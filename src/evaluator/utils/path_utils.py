"""Path helpers."""
from __future__ import annotations
import os


def ensure_dir(path: str) -> None:
    """Ensure that a directory exists for the given path (create parents)."""
    os.makedirs(path, exist_ok=True)

def get_all_excel_filenames(folder_path):
    files = os.listdir(folder_path)
    excel_files = []
    for f in files:
        if f.endswith('.xlsx'):
            excel_files.append(f)
    write_to_file(f"Found {len(excel_files)} excel files to evaluate. \n\n\n\n ")
    return excel_files

