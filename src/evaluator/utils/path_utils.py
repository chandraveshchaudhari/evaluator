"""
Path utilities for file and folder operations.
"""

def list_files_paths(path):
    """List files in the given path."""
    if path.exists() and path.is_dir():
        return [item for item in path.iterdir() if item.is_file()]
    return []

def is_notebook(path):
    """Check if the path is a notebook file."""
    pass

def is_excel(path):
    """Check if the path is an Excel file."""
    pass

def sanitize_filename(name):
    """Sanitize a filename for safe usage."""
    pass

def get_file_extension(path):
    """Get the file extension of the given path."""
    return path.suffix.lower() if hasattr(path, "suffix") else ""

