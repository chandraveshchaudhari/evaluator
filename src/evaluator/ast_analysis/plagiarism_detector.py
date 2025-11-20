def _normalize_ast(node: ast.AST) -> str:
def ast_similarity(a: ast.AST, b: ast.AST) -> float:
def compare_sources(src_a: str, src_b: str) -> float:
"""
Plagiarism detection helpers using AST and token similarity.
"""

def ast_similarity(tree1, tree2):
    """Compute AST similarity between two trees."""
    pass

def detect_copy_paste(tree_student, tree_solution):
    """Detect copy-paste similarity between student and solution ASTs."""
    pass

def detect_token_similarity(code1, code2):
    """Detect token-level similarity between two code strings."""
    pass

def detect_structure_similarity(tree1, tree2):
    """Detect structural similarity between two ASTs."""
    pass

# --- The following functions do not fit the new architecture and are commented out ---
# def _normalize_ast(...): ...
# def compare_sources(...): ...

