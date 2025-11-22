"""
Handles ingestion of instructor-provided solution notebooks or files.
Extracts correct functions and test definitions.
"""

from pathlib import Path


class SolutionIngestion:
    """
    Reads instructor's notebook and prepares test specification.
    """

    def __init__(self, path: Path):
        self.path = path

    import ast
import nbformat
from pathlib import Path
from collections import defaultdict

class SolutionIngestion:
    """
    Reads instructor's notebook and prepares structured test specification.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def understand_notebook_solution(self):
        """
        Parse the instructor notebook and extract:
        - Metadata (name, roll_number)
        - Question functions (question_one, question_two, etc.)
        - Associated assertion tests
        
        Returns
        -------
        dict
            {
                "metadata": {"name": str, "roll_number": str},
                "questions": {
                    "question_one": {"tests": [list of assertion strings]},
                    ...
                }
            }
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Solution notebook not found: {self.path}")

        # Load notebook
        notebook = nbformat.read(self.path, as_version=4)

        metadata = {}
        question_asserts = defaultdict(lambda: {"tests": []})

        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue

            source = cell.source.strip()
            if not source:
                continue

            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue  # skip malformed cell

            # --- Extract metadata ---
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "name":
                                metadata["name"] = self._extract_constant(node.value)
                            elif target.id == "roll_number":
                                metadata["roll_number"] = self._extract_constant(node.value)

                # --- Extract function definitions ---
                if isinstance(node, ast.FunctionDef) and node.name.startswith("question_"):
                    if node.name not in question_asserts:
                        question_asserts[node.name] = {"tests": []}

            # --- Extract assertions (link them to question functions) ---
            for line in source.split("\n"):
                if line.strip().startswith("assert "):
                    func = self._extract_function_from_assert(line)
                    if func:
                        question_asserts[func]["tests"].append(line.strip())

        return {"type": "notebook",
            "metadata": metadata,
            "questions": dict(question_asserts),
        }

    # ----------------- helper methods -----------------

    def _extract_constant(self, node):
        """Extract constant values from AST nodes safely."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):  # backward compat
            return node.s
        return None

    def _extract_function_from_assert(self, assert_line: str):
        """Extract question function name from an assert line."""
        try:
            line = assert_line.replace("assert", "").strip()
            func_name = line.split("(")[0].strip()
            if func_name.startswith("question_"):
                return func_name
        except Exception:
            pass
        return None


    def extract_cells(self):
        """Return all code cells from instructor notebook."""
        return [c for c in self.notebook.cells if c.cell_type == "code"]



def create_answer_key(excel_file_path, column_name, row_number, number_of_question, worksheet_name = 'Answers'):
  formula_wb = openpyxl.load_workbook(excel_file_path)
  formula_ws = formula_wb[worksheet_name]

  value_wb = openpyxl.load_workbook(excel_file_path, data_only=True)
  value_ws = value_wb[worksheet_name]

  formula_answer_key = create_formula_answers_loop(column_name, row_number, number_of_question, formula_ws)
  value_answer_key = create_answers_loop(column_name, row_number, number_of_question, value_ws)

  return formula_answer_key, value_answer_key


def create_answers_loop(column_name, row_number, number_of_question, worksheet):
  result = dict()
  for i in range(number_of_question):
    cell_address = column_name + str(row_number+i)
    result[cell_address] = check_value(cell_address, worksheet)

  return result


def create_formula_answers_loop(column_name, row_number, number_of_question, worksheet):
  result = dict()
  for i in range(number_of_question):
    cell_address = column_name + str(row_number+i)
    print(cell_address)
    cell_value = check_value(cell_address, worksheet)
    print(cell_value)
    # Check if the cell value is an ArrayFormula object and get its text
    if isinstance(cell_value, openpyxl.worksheet.formula.ArrayFormula):
        cell_value = cell_value.text
    result[cell_address] = str(cell_value).split("(")[0]

  return result

# formula_answer, value_answer = create_answer_key(assignment2_excel_answer_key_path, 'B', 5, 10, "Sheet1")