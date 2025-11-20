detect usage of disallowed constructs (for example, `exec`, `eval`, or
to be extended as needed.
def check_forbidden(tree: ast.AST, forbidden_names: set[str] | None = None) -> List[str]:
"""
Forbidden code checks for static analysis.
"""

def find_forbidden_imports(tree, forbidden_libs):
    """Find forbidden imports in the AST tree."""
    pass

def detect_dangerous_code(tree):
    """Detect dangerous code patterns in the AST tree."""
    pass

# --- The following functions do not fit the new architecture and are commented out ---
# def check_forbidden(...): ...
    """Return a list of human-readable messages for forbidden usage.
