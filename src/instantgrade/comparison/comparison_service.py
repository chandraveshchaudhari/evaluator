import traceback
import subprocess
import tempfile
import textwrap
from pathlib import Path
import inspect
import sys


class ComparisonService:
    """Service for comparing student submissions against expected assertions.

    Executes assertion code in an isolated subprocess sandbox with:
    - Timeouts (infinite loop protection)
    - Memory limit (prevents system freeze)
    - Optional CPU time restriction
    """

    def __init__(self, timeout=3, memory_limit_mb=512, cpu_time_sec=5, debug=False):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.cpu_time_sec = cpu_time_sec
        self.debug = debug

    # -------------------------------------------------------------------------
    def run_assertions(self, student_namespace, assertions, question_name=None, timeout=None):
        """Run assertions safely with isolation and resource limits."""
        timeout = timeout or self.timeout
        results = []

        for code in assertions:
            status, err = self._safe_exec_isolated(code, student_namespace, timeout)
            results.append(
                {
                    "question": question_name,
                    "assertion": code,
                    "status": status,
                    "error": err,
                    "score": 1 if status == "passed" else 0,
                }
            )

        return results

    # -------------------------------------------------------------------------
    def _safe_exec_isolated(self, code: str, namespace: dict, timeout: int):
        """Execute assertion inside isolated subprocess with memory + CPU limit."""
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
                tmp.write("import sys, resource, signal, pandas as pd, numpy as np\n")

                # Apply sandbox resource limits
                tmp.write(
                    textwrap.dedent(
                        f"""
                # --- Resource limits (active on UNIX) ---
                try:
                    resource.setrlimit(resource.RLIMIT_AS, ({self.memory_limit_mb * 1024 * 1024}, {self.memory_limit_mb * 1024 * 1024}))
                    resource.setrlimit(resource.RLIMIT_CPU, ({self.cpu_time_sec}, {self.cpu_time_sec}))
                except Exception:
                    pass
                \n
                """
                    )
                )

                # Recreate student's namespace
                for k, v in namespace.items():
                    if k.startswith("__"):
                        continue
                    try:
                        if isinstance(
                            v, (int, float, str, bool, list, dict, tuple, set, type(None))
                        ):
                            tmp.write(f"{k} = {repr(v)}\n")
                        elif inspect.isfunction(v):
                            src = self._get_function_source(v)
                            if src:
                                tmp.write(f"\n{textwrap.dedent(src)}\n")
                        elif "pandas" in sys.modules and "DataFrame" in str(type(v)):
                            # create placeholder DataFrame (shape only)
                            shape = getattr(v, "shape", (0, 0))
                            tmp.write(f"{k} = pd.DataFrame(np.zeros({shape}))\n")
                    except Exception:
                        continue

                # Add assertion
                tmp.write("\n" + textwrap.dedent(code) + "\n")
                tmp_path = tmp.name

            # Execute in subprocess (isolated)
            proc = subprocess.run(
                ["python3", tmp_path], capture_output=True, text=True, timeout=timeout
            )

            if proc.returncode == 0:
                return "passed", None
            else:
                err = proc.stderr.strip() or proc.stdout.strip() or "Assertion failed"
                return "failed", err

        except subprocess.TimeoutExpired:
            return (
                "failed",
                f"TimeoutError: exceeded {timeout}s (possible infinite loop or blocking input())",
            )
        except Exception:
            return "failed", traceback.format_exc()
        finally:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)

    # -------------------------------------------------------------------------
    def _get_function_source(self, func):
        """Safely extract function source code for re-execution."""
        try:
            import inspect

            src = inspect.getsource(func)
            return textwrap.dedent(src)
        except Exception:
            return None
