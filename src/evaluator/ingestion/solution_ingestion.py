"""
Handles ingestion of instructor-provided solution notebooks or files.
Extracts correct functions and test definitions.
"""

from pathlib import Path
from .file_loader import FileLoader

class SolutionIngestion:
    """
    Reads instructor's notebook and prepares test specification.
    """

    def __init__(self, path: Path):
        self.path = path
        self.notebook = None

    def load(self):
        """Load instructor notebook."""
        self.notebook = FileLoader.load_notebook(self.path)

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

formula_answer, value_answer = create_answer_key(assignment2_excel_answer_key_path, 'B', 5, 10, "Sheet1")