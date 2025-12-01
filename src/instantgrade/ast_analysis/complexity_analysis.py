tool, but it's fast and useful as a first-pass metric.
def estimate_cyclomatic_complexity(tree: ast.AST) -> int:
def complexity_for_sources(sources: Iterable[str]) -> int:
"""
Complexity analysis helpers for static code analysis.
"""

def count_loops(tree):
    """Count the number of loops in the AST tree."""
    pass

def count_nested_loops(tree):
    """Count the number of nested loops in the AST tree."""
    pass

def count_if_statements(tree):
    """Count the number of if statements in the AST tree."""
    pass

def compute_cyclomatic_complexity(tree):
    """Compute cyclomatic complexity of the AST tree."""
    pass

def detect_long_functions(tree):
    """Detect long functions in the AST tree."""
    pass

# --- The following functions do not fit the new architecture and are commented out ---
# def estimate_cyclomatic_complexity(...): ...
# def complexity_for_sources(...): ...
    """
