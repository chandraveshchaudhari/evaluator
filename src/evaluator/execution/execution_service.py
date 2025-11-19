from .notebook_executor import run_notebook
from .excel_executor import run_excel

class ExecutionService:
    def execute(self, solution_file, submission_file):
        if submission_file.suffix == ".ipynb":
            return run_notebook(solution_file, submission_file)
        if submission_file.suffix in (".xlsx", ".xlsm"):
            return run_excel(solution_file, submission_file)
        raise ValueError("Unsupported file type")
