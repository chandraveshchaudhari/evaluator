"""
Pandas DataFrame comparison helper.
"""

import pandas as pd

class DataFrameComparator:
    """
    Compare DataFrames for equality with optional tolerance.
    """

    @staticmethod
    def compare(df1: pd.DataFrame, df2: pd.DataFrame):
        try:
            pd.testing.assert_frame_equal(df1, df2)
            return True, None
        except Exception as e:
            return False, str(e)

from __future__ import annotations
from typing import Dict, Any
import pandas as pd


def compare_dataframes(expected: pd.DataFrame, actual: pd.DataFrame, sample_rows: int = 5) -> Dict[str, Any]:
    """Return a dict describing matches/mismatches between two DataFrames.

    Keys: shape_ok, columns_ok, sample_matches (list of bools), details
    """
    details = {}
    shape_ok = expected.shape == actual.shape
    columns_ok = list(expected.columns) == list(actual.columns)

    sample_matches = []
    for i in range(min(sample_rows, len(expected), len(actual))):
        exp_row = expected.iloc[i].to_dict()
        act_row = actual.iloc[i].to_dict()
        sample_matches.append(exp_row == act_row)

    details["expected_shape"] = expected.shape
    details["actual_shape"] = actual.shape
    details["expected_columns"] = list(expected.columns)
    details["actual_columns"] = list(actual.columns)

    return {"shape_ok": shape_ok, "columns_ok": columns_ok, "sample_matches": sample_matches, "details": details}

"""Value comparison utilities."""
from __future__ import annotations
from typing import Any


def compare_values(expected: Any, actual: Any, tolerance: float = 1e-9) -> bool:
    """Compare expected and actual values with optional tolerance for numbers."""
    if expected is None or actual is None:
        return expected is actual

    try:
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(float(expected) - float(actual)) <= tolerance
    except Exception:
        pass

    return expected == actual

"""Compare function behavior between student and solution.

The checker accepts two callables and runs them with provided args/kwargs to
compare results. This module expects the caller to import student functions
into a safe execution environment.
"""
from __future__ import annotations
from typing import Any, Callable, Tuple


def compare_function_outputs(student_fn: Callable[..., Any], solution_fn: Callable[..., Any], *args, tolerance: float = 1e-9, **kwargs) -> Tuple[bool, Any, Any]:
    """Run both functions with args/kwargs and compare outputs.

    Returns (ok, student_result, solution_result).
    """
    s = student_fn(*args, **kwargs)
    r = solution_fn(*args, **kwargs)
    try:
        # numeric comparison
        if isinstance(s, (int, float)) and isinstance(r, (int, float)):
            ok = abs(float(s) - float(r)) <= tolerance
        else:
            ok = s == r
    except Exception:
        ok = False
    return ok, s, r


