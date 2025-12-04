import traceback
import subprocess
import tempfile
import textwrap
from pathlib import Path
import inspect
import sys


class ComparisonService:
    """Safe sandbox for running student assertions with optional setup context."""

    def __init__(self, timeout=3, memory_limit_mb=512, cpu_time_sec=5, debug=False):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.cpu_time_sec = cpu_time_sec
        self.debug = debug

    # -------------------------------------------------------------------------
    def run_assertions(self, student_namespace, assertions, question_name=None,
                       context_code=None, timeout=None):
        """
        Run assertions with optional setup context safely in an isolated process.
        """
        timeout = timeout or self.timeout
        results = []

        # --- Step 1: Execute context/setup code (if any) ---
        if context_code:
            ctx_status, ctx_err = self._safe_exec_isolated(
                code=context_code,
                namespace=student_namespace,
                timeout=timeout,
                label="context setup"
            )

            results.append({
                "question": question_name,
                "assertion": "[context setup]",
                "status": ctx_status,
                "error": ctx_err,
                "score": 1 if ctx_status == "passed" else 0,
            })

            # if setup failed, skip assertions to prevent cascading errors
            if ctx_status == "failed":
                return results

        # --- Step 2: Execute assertions ---
        for code in assertions:
            status, err = self._safe_exec_isolated(
                code=code,
                namespace=student_namespace,
                timeout=timeout,
                label="assertion"
            )
            results.append({
                "question": question_name,
                "assertion": code,
                "status": status,
                "error": err,
                "score": 1 if status == "passed" else 0,
            })

        return results

    # -------------------------------------------------------------------------
    def _safe_exec_isolated(self, code: str, namespace: dict, timeout: int, label="assertion"):
        """
        Execute arbitrary code safely in an isolated subprocess with limits.
        """
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
                tmp.write("import sys, resource, signal, pandas as pd, numpy as np\n")

                # --- Apply resource limits (Linux/macOS only) ---
                tmp.write(textwrap.dedent(f"""
                try:
                    # Limit virtual memory
                    resource.setrlimit(resource.RLIMIT_AS,
                        ({self.memory_limit_mb * 1024 * 1024}, {self.memory_limit_mb * 1024 * 1024}))
                    # Limit CPU seconds
                    resource.setrlimit(resource.RLIMIT_CPU,
                        ({self.cpu_time_sec}, {self.cpu_time_sec}))
                except Exception:
                    pass
                \n"""))

                # --- Override input() to block waiting ---
                tmp.write(textwrap.dedent("""
                __builtins__.input = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("input() not allowed"))
                \n"""))

                # --- Restore student's namespace safely ---
                for k, v in namespace.items():
                    if k.startswith("__"):
                        continue
                    try:
                        if isinstance(v, (int, float, str, bool, list, dict, tuple, set, type(None))):
                            tmp.write(f"{k} = {repr(v)}\n")
                        elif inspect.isfunction(v):
                            src = self._get_function_source(v)
                            if src:
                                tmp.write(f"\n{textwrap.dedent(src)}\n")
                        elif 'pandas' in sys.modules and 'DataFrame' in str(type(v)):
                            shape = getattr(v, 'shape', (0, 0))
                            tmp.write(f"{k} = pd.DataFrame(np.zeros({shape}))\n")
                    except Exception:
                        continue

                tmp.write("\n" + textwrap.dedent(code) + "\n")
                tmp_path = tmp.name

            # --- Run code inside sandbox ---
            proc = subprocess.run(
                ["python3", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if proc.returncode == 0:
                return "passed", None
            else:
                err = proc.stderr.strip() or proc.stdout.strip() or f"{label} failed"
                return "failed", err

        except subprocess.TimeoutExpired:
            return "failed", f"TimeoutError: exceeded {timeout}s ({label} - possible infinite loop or input())"
        except Exception:
            return "failed", traceback.format_exc()
        finally:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)

    # -------------------------------------------------------------------------
    def _get_function_source(self, func):
        """Extract clean function source safely."""
        try:
            src = inspect.getsource(func)
            return textwrap.dedent(src)
        except Exception:
            return None
