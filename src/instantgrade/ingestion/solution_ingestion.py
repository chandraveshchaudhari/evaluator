import nbformat
import ast
from pathlib import Path
from collections import OrderedDict
from instantgrade.utils.io_utils import safe_load_notebook
import json


class SolutionIngestion:
    """
    Reads instructor's notebook in a fixed 3-cell pattern:
      [markdown: description] → [code: function] → [code: asserts + helper code]

    Produces a structured JSON representation compatible with Docker grader.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    # ----------------------------------------------------------------------
    def understand_notebook_solution(self) -> dict:
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

                # Step 3: Next cell → context + asserts
                context_code = ""
                assert_lines = []

                if func_name and i + 2 < len(nb.cells):
                    test_cell = nb.cells[i + 2]
                    if test_cell.cell_type == "code":
                        assert_cell_src = test_cell.source
                        setup_lines = []
                        for line in assert_cell_src.splitlines():
                            stripped = line.strip()
                            if stripped.startswith("assert "):
                                assert_lines.append(stripped)
                            else:
                                setup_lines.append(line)
                        context_code = "\n".join(setup_lines)

                if func_name:
                    questions[func_name] = {
                        "description": description,
                        "function": func_src,
                        "context_code": context_code,
                        "tests": assert_lines,
                    }

                i += 3
                continue

            # Step 4: Metadata cell (extract name / roll_number)
            if cell.cell_type == "code" and ("name" in cell.source and "roll_number" in cell.source):
                try:
                    tree = ast.parse(cell.source)
                    for node in tree.body:
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name) and target.id == "name":
                                    metadata["name"] = node.value.s
                                elif isinstance(target, ast.Name) and target.id == "roll_number":
                                    metadata["roll_number"] = node.value.s
                except Exception:
                    pass

            i += 1

        # Step 5: Build final dict
        solution_dict = {
            "type": "notebook",
            "metadata": metadata,
            "default_name": metadata.get("name"),
            "default_roll_number": metadata.get("roll_number"),
            "questions": questions,
        }

        return solution_dict

    # ----------------------------------------------------------------------
    def export_solution_json(self, output_path: str | Path):
        """
        Export the parsed instructor notebook into a JSON file
        that can be passed to the Docker grader.
        """
        parsed = self.understand_notebook_solution()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf8") as f:
            json.dump(parsed, f, indent=2)
        return output_path

    # ----------------------------------------------------------------------
    def _extract_function_name(self, code: str) -> str | None:
        """Return the first function name defined in a code cell."""
        try:
            tree = ast.parse(code)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    return node.name
        except Exception:
            pass
        return None
