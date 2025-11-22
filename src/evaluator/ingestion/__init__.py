
"""
Ingestion layer.
Responsible for loading instructor and student submissions from
various file formats (Jupyter, Excel, Python scripts, future languages).
"""

from .file_loader import load_notebook, load_excel, load_json, load_csv, load_raw_code

__all__ = ["load_notebook", "load_excel", "load_json", "load_csv", "load_raw_code"]