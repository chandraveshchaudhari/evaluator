def compare_dataframes(expected: pd.DataFrame, actual: pd.DataFrame, sample_rows: int = 5) -> Dict[str, Any]:
def compare_values(expected: Any, actual: Any, tolerance: float = 1e-9) -> bool:
def compare_function_outputs(student_fn: Callable[..., Any], solution_fn: Callable[..., Any], *args, tolerance: float = 1e-9, **kwargs) -> Tuple[bool, Any, Any]:
"""
Notebook comparison helpers for comparing variables, dataframes, and outputs.
"""

def compare_variables(student_vars, solution_vars):
    """Compare variables between student and solution notebooks."""
    pass

def compare_dataframes(df_student, df_solution):
    """Compare pandas DataFrames from student and solution notebooks."""
    pass

def compare_scalars(a, b):
    """Compare scalar values."""
    pass

def compare_lists(l1, l2):
    """Compare lists."""
    pass

def compare_dicts(d1, d2):
    """Compare dictionaries."""
    pass

def compare_exceptions(student_trace):
    """Compare exception traces from student notebook."""
    pass

def compare_plots(p1, p2):
    """Compare plots (optional)."""
    pass

# --- The following classes/functions do not fit the new architecture and are commented out ---
# class DataFrameComparator: ...
# def compare_dataframes(...): ...
# def compare_values(...): ...
# def compare_function_outputs(...): ...
    details["actual_shape"] = actual.shape

    details["expected_columns"] = list(expected.columns)

    details["actual_columns"] = list(actual.columns)
