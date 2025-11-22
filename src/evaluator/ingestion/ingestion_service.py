
# ================= IngestionService (Refactored for new architecture) =================
from collections.abc import Iterable
from pathlib import Path

from evaluator.ingestion.solution_ingestion import SolutionIngestion
from evaluator.utils.path_utils import get_file_extension, list_files_paths
from pathlib import Path
from evaluator.utils.io_utils import load_notebook, load_excel, load_json, load_csv, load_raw_code
from evaluator.ingestion.validation import validate_extension
from evaluator.utils.path_utils import is_notebook, is_excel



class IngestionService:
    """
    Service for loading submissions, solutions, validating files, and extracting metadata.
    """
    def __init__(self, solution_file_path: str | Path = None, submission_folder_path: str | Path = None):
        self.solution_file_path = solution_file_path
        self.submission_folder_path = submission_folder_path
    
    def list_submissions(self, submission_folder_path: str | Path = None) -> Iterable[Path]:
        """List all submission files in the given folder."""
        submission_folder_path = submission_folder_path if submission_folder_path else self.submission_folder_path
        submission_files = []
        for file_path in list_files_paths(submission_folder_path):
            if self.is_submission_file(file_path):
                submission_files.append(file_path)
        return submission_files

    def is_submission_file(self, path):
        """Detect file type by extension."""
        expected_extension = get_file_extension(self.solution_file_path)
        if get_file_extension(path) == expected_extension:
            return True
        return False

    def load_submission(self, path):
        """
        Load a student submission based on file type.

        Handles: .ipynb, .xlsx, .xlsm, .py, .csv, .json
        Returns a structured object (dict or domain object) that can be 
        passed to ExecutionService.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Submission file not found: {path}")

        # Detect file type automatically
        if is_notebook(path):
            validate_extension(path, [".ipynb"])
            return {
                "type": "notebook",
                "path": path,
                "notebook": load_notebook(path)
            }

        if is_excel(path):
            validate_extension(path, [".xlsx", ".xlsm"])
            return {
                "type": "excel",
                "path": path,
                "workbook": load_excel(path)
            }

        if path.suffix == ".py":
            return {
                "type": "python_script",
                "path": path,
                "code": load_raw_code(path)
            }

        if path.suffix == ".csv":
            return {
                "type": "csv",
                "path": path,
                "data": load_csv(path)
            }

        if path.suffix == ".json":
            return {
                "type": "json",
                "path": path,
                "data": load_json(path)
            }

        raise ValueError(f"Unsupported submission format: {path.suffix}")


    def load_solution(self, solution_path=None):
        """
        Load instructor solution file based on file type.

        Supports: .ipynb, .xlsx, .xlsm, .py, .json, .csv
        This returns a structured object ready for execution and comparison.
        """
        solution_path = Path(solution_path) if solution_path else self.solution_file_path

        if not solution_path.exists():
            raise FileNotFoundError(f"Solution file not found: {solution_path}")

        if is_notebook(solution_path):
            validate_extension(solution_path, [".ipynb"])
            
            return SolutionIngestion(solution_path).understand_notebook_solution()

        if is_excel(solution_path):
            validate_extension(solution_path, [".xlsx", ".xlsm"])
            pass

        if solution_path.suffix == ".py":
            return {
                "type": "python_script",
                "path": solution_path,
                "code": load_raw_code(solution_path)
            }

        if solution_path.suffix == ".json":
            return {
                "type": "json",
                "path": solution_path,
                "schema": load_json(solution_path)
            }

        if solution_path.suffix == ".csv":
            return {
                "type": "csv",
                "path": solution_path,
                "data": load_csv(solution_path)
            }

        raise ValueError(f"Unsupported solution format: {solution_path.suffix}")

    def load_answer_key(self, answer_key_path):
        """Load an answer key from the given path."""
        # ...implementation...
        pass

    def validate_file(self, path):
        """Validate a file (extension, structure, etc)."""
        # ...implementation...
        pass

    def validate_folder(self, folder_path):
        """Validate a folder (structure, required files, etc)."""
        # ...implementation...
        pass

    def extract_student_metadata(self, path):
        """Extract student metadata from a submission file path."""
        # ...implementation...
        pass


