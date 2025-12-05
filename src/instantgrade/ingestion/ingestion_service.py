# ================= IngestionService (Refactored for new architecture) =================
"""Service for ingesting and loading solution and submission files.

This module provides the IngestionService class which handles file loading,
validation, and metadata extraction for various file types including Jupyter
notebooks, Excel files, Python scripts, CSV, and JSON files.
"""

from collections.abc import Iterable
from pathlib import Path

from instantgrade.ingestion.solution_ingestion import SolutionIngestion
from instantgrade.utils.path_utils import get_file_extension, list_files_paths
from pathlib import Path
from instantgrade.utils.io_utils import (
    load_excel,
    load_json,
    load_csv,
    load_raw_code,
    safe_load_notebook,
)
from instantgrade.utils.path_utils import is_notebook, is_excel


class IngestionService:
    """Service for loading solutions, submissions, and validating files.

    The IngestionService handles the loading of instructor solution files and
    student submission files. It supports multiple file formats and provides
    validation and metadata extraction capabilities.

    Parameters
    ----------
    solution_file_path : str or Path, optional
        Path to the instructor's solution file.
    submission_folder_path : str or Path, optional
        Path to the folder containing student submissions.

    Attributes
    ----------
    solution_file_path : str or Path
        Stored path to the solution file.
    submission_folder_path : str or Path
        Stored path to the submissions folder.

    Examples
    --------
    >>> service = IngestionService(
    ...     solution_file_path="solution.ipynb",
    ...     submission_folder_path="submissions/"
    ... )
    >>> solution = service.load_solution()
    >>> submissions = service.list_submissions()
    """

    def __init__(
        self, solution_file_path: str | Path = None, submission_folder_path: str | Path = None
    ):
        self.solution_file_path = solution_file_path
        self.submission_folder_path = submission_folder_path

    def list_submissions(self, submission_folder_path: str | Path = None) -> Iterable[Path]:
        """List all submission files in the given folder.

        Scans the submission folder and returns paths to files that match
        the expected file type based on the solution file extension.

        Parameters
        ----------
        submission_folder_path : str or Path, optional
            Path to the submissions folder. If None, uses the instance's
            submission_folder_path attribute.

        Returns
        -------
        Iterable of Path
            Collection of Path objects for valid submission files.

        Examples
        --------
        >>> service = IngestionService("solution.ipynb", "submissions/")
        >>> submissions = service.list_submissions()
        >>> print(f"Found {len(list(submissions))} submissions")
        """
        submission_folder_path = (
            submission_folder_path if submission_folder_path else self.submission_folder_path
        )
        submission_files = []
        for file_path in list_files_paths(submission_folder_path):
            if self.is_submission_file(file_path):
                submission_files.append(file_path)
        return submission_files

    def is_submission_file(self, path):
        """Check if a file is a valid submission.

        Validates that the file extension matches the expected type based on
        the solution file.

        Parameters
        ----------
        path : str or Path
            Path to the file to check.

        Returns
        -------
        bool
            True if the file is a valid submission, False otherwise.

        Examples
        --------
        >>> service = IngestionService("solution.ipynb", "submissions/")
        >>> is_valid = service.is_submission_file("student1.ipynb")
        """
        expected_extension = get_file_extension(self.solution_file_path)
        if get_file_extension(path) == expected_extension:
            return True
        return False

    def load_submission(self, path):
        """Load a student submission file.

        Loads and parses a student submission based on its file type. Supports
        Jupyter notebooks, Excel files, Python scripts, CSV, and JSON files.

        Parameters
        ----------
        path : str or Path
            Path to the submission file to load.

        Returns
        -------
        dict
            Dictionary containing submission metadata and loaded content. Keys vary
            by file type but always include 'type' and 'path'. Additional keys:
            - For notebooks: 'notebook' (nbformat NotebookNode)
            - For Excel: 'workbook' (openpyxl Workbook)
            - For Python: 'code' (str)
            - For CSV: 'data' (pandas DataFrame)
            - For JSON: 'data' (dict)

        Raises
        ------
        FileNotFoundError
            If the submission file does not exist.
        ValueError
            If the file type is not supported.

        Examples
        --------
        >>> service = IngestionService()
        >>> submission = service.load_submission("student1.ipynb")
        >>> print(submission['type'])  # 'notebook'
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Submission file not found: {path}")

        # Detect file type automatically
        if is_notebook(path):
            return {"type": "notebook", "path": path, "notebook": safe_load_notebook(path)}

        if is_excel(path):
            return {"type": "excel", "path": path, "workbook": load_excel(path)}

        if path.suffix == ".py":
            return {"type": "python_script", "path": path, "code": load_raw_code(path)}

        if path.suffix == ".csv":
            return {"type": "csv", "path": path, "data": load_csv(path)}

        if path.suffix == ".json":
            return {"type": "json", "path": path, "data": load_json(path)}

        raise ValueError(f"Unsupported submission format: {path.suffix}")

    def load_solution(self, solution_path=None):
        """Load an instructor solution file.

        Loads and parses an instructor's solution file based on its type.
        Supports Jupyter notebooks, Excel files, Python scripts, CSV, and JSON.

        Parameters
        ----------
        solution_path : str or Path, optional
            Path to the solution file. If None, uses the instance's
            solution_file_path attribute.

        Returns
        -------
        dict
            Dictionary containing solution metadata and loaded content. Structure
            varies by file type but includes 'type' and 'path' keys.

        Raises
        ------
        FileNotFoundError
            If the solution file does not exist.
        ValueError
            If the file type is not supported.

        Examples
        --------
        >>> service = IngestionService("solution.ipynb", "submissions/")
        >>> solution = service.load_solution()
        >>> print(solution.keys())
        """
        solution_path = Path(solution_path) if solution_path else self.solution_file_path

        if not solution_path.exists():
            raise FileNotFoundError(f"Solution file not found: {solution_path}")

        if is_notebook(solution_path):
            return SolutionIngestion(solution_path).understand_notebook_solution()

        if is_excel(solution_path):
            pass

        if solution_path.suffix == ".py":
            return {
                "type": "python_script",
                "path": solution_path,
                "code": load_raw_code(solution_path),
            }

        if solution_path.suffix == ".json":
            return {"type": "json", "path": solution_path, "schema": load_json(solution_path)}

        if solution_path.suffix == ".csv":
            return {"type": "csv", "path": solution_path, "data": load_csv(solution_path)}

        raise ValueError(f"Unsupported solution format: {solution_path.suffix}")



