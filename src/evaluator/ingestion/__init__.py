
"""
Ingestion layer.
Responsible for loading instructor and student submissions from
various file formats (Jupyter, Excel, Python scripts, future languages).
"""

from .file_loader import detect_submission_files, load_file  # noqa: F401

__all__ = ["detect_submission_files", "load_file"]
