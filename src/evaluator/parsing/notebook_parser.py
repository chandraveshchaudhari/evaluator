"""Notebook parsing utilities using nbformat.

Functions:
- extract_code_cells(notebook_path) -> list[str]
- parse_notebook(notebook_path) -> dict with code cells, errors

"""
from __future__ import annotations
from typing import List, Dict, Any
import nbformat
import ast


def extract_code_cells(notebook_path: str) -> List[str]:
    """Return a list of source strings for code cells in the notebook."""
    nb = nbformat.read(notebook_path, as_version=4)
    code_cells: List[str] = []
    for cell in nb.cells:
        if cell.cell_type == "code":
            code_cells.append(cell.source)
    return code_cells


def parse_notebook(notebook_path: str) -> Dict[str, Any]:
    """Parse a notebook and return structure of code cells and metadata.

    Returns dict with keys: code_cells, metadata
    """
    nb = nbformat.read(notebook_path, as_version=4)
    code_cells = extract_code_cells(notebook_path)
    return {"code_cells": code_cells, "metadata": nb.metadata}

"""
Extract function definitions from notebook cells.
"""

import ast

class FunctionExtractor:
    """
    Extracts function definitions from code cells.
    """

    @staticmethod
    def extract_functions_from_code(source: str):
        """
        Parse Python code and return {function_name: source_code}.
        """
        tree = ast.parse(source)
        functions = {}

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Extract full source of the function
                functions[func_name] = source

        return functions


"""
Extract Python assertions from instructor code cells.
"""

class AssertionExtractor:
    """
    Extracts assertion statements for each question.
    """

    @staticmethod
    def extract_assertions(source: str):
        """
        Return a list of assertion lines from code source.
        """
        lines = source.splitlines()
        return [line.strip() for line in lines if line.strip().startswith("assert ")]


"""
Methods to detect student metadata like name, roll number, batch, etc.
"""

class MetadataParser:
    """
    Extracts metadata from notebooks or filenames.
    """

    @staticmethod
    def from_filename(filename: str):
        """
        Extract roll number, name from filename convention:
        e.g., '12345_JohnDoe_Assignment1.ipynb'
        """
        # TODO: Implement your own naming convention parsing
        return {
            "roll_number": None,
            "name": None
        }

    @staticmethod
    def from_markdown(cells):
        """Extract metadata from markdown cell if present."""
        # TODO: Implement optional markdown-based metadata scanning
        return {}


"""Solution parser: extract functions from instructor solution files using AST.

This module focuses on extracting Python functions from a .py file. It
returns a mapping function_name -> source code snippet. The consumer may then
generate tests or expected outputs from those functions.
"""



def extract_functions_from_py(py_file_path: str) -> Dict[str, str]:
    """Parse the python file and return a dict of function name to source.

    Only top-level function definitions are returned.
    """
    with open(py_file_path, "r", encoding="utf8") as f:
        source = f.read()

    tree = ast.parse(source)
    functions: Dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # ast.get_source_segment introduced in 3.8
            try:
                func_src = ast.get_source_segment(source, node)
            except Exception:
                # fallback: best-effort reconstruct
                func_src = """def %s(...): <source unavailable>""" % node.name
            functions[node.name] = func_src
    return functions

