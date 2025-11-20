"""
Solution loader utilities for instructor-provided solution files.
"""
import nbformat
import ast
from pathlib import Path


def load_solution_notebook(path):
    """
    Load instructor solution notebook, extract:
    - metadata (name, roll_number if present)
    - function definitions (question_one, question_two, ...)
    - assertion tests that verify correctness
    - notebook object

    Returns a structured dict with:
        {
            "type": "notebook_solution",
            "path": Path,
            "notebook": nb_object,
            "question_functions": ["question_one", "question_two"],
            "assertions": ["assert question_one(2)==4", ...],
            "metadata": {"name": "...", "roll_number": "..."}
        }
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Solution notebook does not exist: {path}")

    nb = nbformat.read(path, as_version=4)

    question_functions = []
    assertions = []
    metadata = {}

    # Iterate over notebook code cells
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        
        source = cell.source

        # AST parse the code cell
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Ignore malformed blocks
            continue

        for node in tree.body:
            # -------------------------
            # 1. Extract solution metadata (name, roll_number)
            # -------------------------
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "name":
                            metadata["name"] = _extract_constant_value(node.value)
                        if target.id == "roll_number":
                            metadata["roll_number"] = _extract_constant_value(node.value)

            # -------------------------
            # 2. Extract function definitions: question_one, question_two, ...
            # -------------------------
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("question_"):
                    question_functions.append(node.name)

        # -------------------------
        # 3. Extract assertion tests (exact checks)
        # -------------------------
        # Instead of AST, we capture assertion lines textually.
        for line in source.split("\n"):
            if line.strip().startswith("assert "):
                assertions.append(line.strip())

    return {
        "type": "notebook_solution",
        "path": path,
        "notebook": nb,
        "question_functions": question_functions,
        "assertions": assertions,
        "metadata": metadata,
    }



def _extract_constant_value(node):
    """
    Safely extract a constant string/number from an AST node.
    Supports: 'abc', 123, f-strings (joined), etc.
    """
    try:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Str):  # Py <3.8
            return node.s
        if isinstance(node, ast.JoinedStr):  # f-string
            return "".join(
                part.value if isinstance(part, ast.Constant) else ""
                for part in node.values
            )
    except:
        return None

    return None


def load_solution_excel(path):
    """Load a solution Excel file from the given path."""
    pass

def parse_solution_schema(path):
    """Parse solution schema, metadata, or rubrics from the given path."""
    pass
