def validate_folder_structure(folder: str | Path) -> bool:
def validate_file_extension(file: str | Path, allowed: Iterable[str]) -> bool:
def validate_required_columns(df, required_cols: Sequence[str]) -> bool:
def validate_json_schema(data: dict, schema: dict) -> bool:
def safe_open(path: str | Path, mode: str = "r"):

"""
Validation helpers for ingestion layer.
"""

def validate_extension(path, allowed_extensions):
    """Validate file extension against allowed extensions."""
    pass

def validate_required_files(folder, required_files):
    """Validate that required files exist in the folder."""
    pass

def validate_json_schema(data, schema):
    """Validate a JSON object against a schema."""
    pass

def validate_notebook_structure(nb):
    """Validate the structure of a notebook object."""
    pass

# --- The following functions do not fit the new architecture and are commented out ---
# def validate_folder_structure(...): ...
# def validate_file_extension(...): ...
# def validate_required_columns(...): ...
# def safe_open(...): ...
