# """AST analysis package for evaluator.

# This package contains small, focused utilities for analyzing Python
# source code using the `ast` module. The modules here provide:
# - ASTAnalyzer: convenience wrapper around ast parsing and common queries
# - forbidden and required checks: small predicate helpers
# - plagiarism_detector: simple AST-based similarity helpers
# - complexity_analysis: a lightweight cyclomatic complexity estimator

# The implementations are intentionally minimal and intended to be
# extended by the project as needed.
# """

# from .ast_analyzer import ASTAnalyzer
# from .forbidden_checks import check_forbidden
# from .required_checks import check_required
# from .plagiarism_detector import ast_similarity
# from .complexity_analysis import estimate_cyclomatic_complexity

# __all__ = [
#     "ASTAnalyzer",
#     "check_forbidden",
#     "check_required",
#     "ast_similarity",
#     "estimate_cyclomatic_complexity",
# ]
