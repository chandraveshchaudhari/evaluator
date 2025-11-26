"""
Handles ingestion of instructor-provided solution notebooks or files.
Extracts correct functions and test definitions.
"""

import nbformat
import ast
from pathlib import Path
from collections import OrderedDict
from evaluator.utils.io_utils import safe_load_notebook


class SolutionIngestion:
    """
    Reads instructor's notebook in a fixed 3-cell pattern:
      [markdown: description] → [code: function] → [code: asserts + helper code]
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def understand_notebook_solution(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Solution notebook not found: {self.path}")

        nb = safe_load_notebook(self.path)
        questions = OrderedDict()
        metadata = {}

        i = 0
        while i < len(nb.cells):
            cell = nb.cells[i]

            # Step 1: Markdown → question description
            if cell.cell_type == "markdown" and cell.source.strip().startswith("##"):
                description = cell.source.strip().split("\n", 1)[-1].strip()

                # Step 2: Next cell should define function
                func_name, func_src = None, None
                if i + 1 < len(nb.cells):
                    code_cell = nb.cells[i + 1]
                    if code_cell.cell_type == "code":
                        func_src = code_cell.source.strip()
                        func_name = self._extract_function_name(func_src)

                # Step 3: Next cell (assertions) — link to that function
                assertions = []
                if func_name and i + 2 < len(nb.cells):
                    test_cell = nb.cells[i + 2]
                    if test_cell.cell_type == "code":
                        assert_cell_src = test_cell.source.strip()
                        # Keep full cell code for context (helpers, imports)
                        full_context_code = assert_cell_src
                        # Extract individual assert lines for reporting
                        assert_lines = [
                            line.strip()
                            for line in assert_cell_src.splitlines()
                            if line.strip().startswith("assert ")
                        ]


                if func_name:
                    questions[func_name] = {
                    "description": description,
                    "function": func_src,
                    "context_code": full_context_code, 
                    "tests": assert_lines,
                }


                i += 3
                continue

            # Capture metadata
            if cell.cell_type == "code" and "name" in cell.source and "roll_number" in cell.source:
                try:
                    tree = ast.parse(cell.source)
                    for node in tree.body:
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if target.id == "name":
                                    metadata["name"] = node.value.s
                                elif target.id == "roll_number":
                                    metadata["roll_number"] = node.value.s
                except Exception:
                    pass

            i += 1

        
        return {
            "type": "notebook",
            "metadata": metadata,
            "questions": questions
        }

    # --- Helper ---
    def _extract_function_name(self, code: str) -> str | None:
        """Return function name defined in code cell."""
        try:
            tree = ast.parse(code)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    return node.name
        except Exception:
            pass
        return None

