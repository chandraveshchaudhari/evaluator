"""Top-level evaluator package exports.

Expose the high-level modules so users can import subpackages like:

from evaluator.ingestion import file_loader

"""
# from .ingestion import file_loader  # noqa: F401
# from .parsing import notebook_parser, solution_parser  # noqa: F401
# from .execution import notebook_executor, sandbox_runner  # noqa: F401
# from .comparison import function_checker, notebook_compare, value_checker  # noqa: F401
# from .reporting import report_builder  # noqa: F401
# from .cli import main as cli  # noqa: F401
from .evaluator import Evaluator


# __all__ = [
#     "file_loader",
#     "sandbox_runner",
#     "notebook_executor",
#     "function_checker",
#     "value_checker",
#     "notebook_compare",
#     "report_builder",
#     "cli",
#     "Evaluator",  
# ]
__all__ = ["Evaluator"]
