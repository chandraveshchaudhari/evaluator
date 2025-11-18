"""
Parsing layer.
Extracts function definitions, assertions, and metadata.
"""
from .notebook_parser import extract_code_cells, parse_notebook  # noqa: F401
from .solution_parser import extract_functions_from_py  # noqa: F401

__all__ = ["extract_code_cells", "parse_notebook", "extract_functions_from_py"]
