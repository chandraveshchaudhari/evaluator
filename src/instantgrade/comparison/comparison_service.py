import json
import tempfile
import shutil
import subprocess
import textwrap
from pathlib import Path
import traceback


class ComparisonService:
    """
    Compares student execution results against instructor-defined assertions.

    For each question, this service runs the student's notebook,
    the instructor's context code, and the assertions inside an
    isolated Docker container with resource limits.
    """

    def __init__(
        self,
        docker_image: str = "python:3.11-slim",
        mem_limit: str = "1g",
        cpu_limit: str = "1.0",
    ):
        self.docker_image = docker_image
        self.mem_limit = mem_limit
        self.cpu_limit = cpu_limit

    def _build_runner_script(self) -> str:
        """
        Python script that will be executed inside the Docker container.

        It:
        - loads student.ipynb
        - patches input() and os.kill
        - executes all notebook cells into a namespace
        - executes context_code
        - executes each assertion
        - writes a results.json file with per-assertion results
        """
        return textwrap.dedent(
            """
            import json
            import nbformat
            import traceback
            import builtins
            import os
            import sys

            # Load configuration
            with open("config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)

            question_name = cfg.get("question_name") or "unknown"
            context_code = cfg.get("context_code") or ""
            assertions = cfg.get("assertions") or []

            results = []

            # Disable input() so it never blocks
            def dummy_input(prompt=None):
                return ""
            builtins.input = dummy_input

            # Disable os.kill to keep sandbox safer
            def safe_kill(*args, **kwargs):
                raise RuntimeError("os.kill is disabled in sandbox")
            os.kill = safe_kill

            # Helper to append a result
            def add_result(assertion_label, status, error=None):
                results.append(
                    {
                        "question": question_name,
                        "assertion": assertion_label,
                        "status": status,
                        "error": error,
                        "score": 1 if status == "passed" else 0,
                    }
                )

            # 1. Load and execute student notebook
            try:
                nb = nbformat.read("student.ipynb", as_version=4)
            except Exception:
                tb = traceback.format_exc()
                add_result(
                    "[notebook load]",
                    "failed",
                    "Failed to read notebook:\\n" + tb,
                )
                with open("results.json", "w", encoding="utf-8") as f:
                    json.dump(results, f)
                raise SystemExit(0)

            ns = {}
            try:
                for cell in nb.cells:
                    if cell.cell_type != "code":
                        continue
                    src = cell.get("source", "")
                    if not src.strip():
                        continue
                    try:
                        exec(compile(src, "<student_cell>", "exec"), ns)
                    except Exception:
                        tb = traceback.format_exc()
                        add_result(
                            "[notebook execution]",
                            "failed",
                            "Error in student cell:\\n" + tb,
                        )
                        # Continue; we still try context + assertions
            except Exception:
                tb = traceback.format_exc()
                add_result(
                    "[notebook execution]",
                    "failed",
                    "Unexpected error while executing notebook:\\n" + tb,
                )

            # 2. Execute context_code once
            if context_code:
                try:
                    exec(compile(context_code, "<context_code>", "exec"), ns)
                except Exception:
                    tb = traceback.format_exc()
                    add_result(
                        "[context setup]",
                        "failed",
                        "Error in context setup:\\n" + tb,
                    )
                    # If context fails, do not run assertions
                    with open("results.json", "w", encoding="utf-8") as f:
                        json.dump(results, f)
                    raise SystemExit(0)

            # 3. Execute each assertion separately
            for code in assertions:
                try:
                    exec(compile(code, "<assertion>", "exec"), ns)
                    add_result(code, "passed", None)
                except Exception:
                    tb = traceback.format_exc()
                    add_result(code, "failed", tb)

            # 4. Persist results
            with open("results.json", "w", encoding="utf-8") as f:
                json.dump(results, f)
            """
        )

    def run_assertions(
        self,
        submission_path: Path,
        assertions: list[str],
        question_name: str | None = None,
        context_code: str | None = None,
        timeout: int = 60,
    ) -> list[dict]:
        """
        Execute instructor assertions in a Docker sandbox for a single question.

        Parameters
        ----------
        submission_path : Path
            Path to the student's notebook submission.
        assertions : list[str]
            Assertion statements to run.
        question_name : str, optional
            Name of the question/function being evaluated.
        context_code : str, optional
            Setup code to run once before assertions.
        timeout : int
            Max time (seconds) for the container to run.

        Returns
        -------
        list[dict]
            List of assertion result dictionaries.
        """
        submission_path = Path(submission_path)

        if not submission_path.exists():
            return [
                {
                    "question": question_name or "unknown",
                    "assertion": "[submission missing]",
                    "status": "failed",
                    "error": f"Submission file not found: {submission_path}",
                    "score": 0,
                }
            ]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            student_nb = tmp_path / "student.ipynb"
            shutil.copy(submission_path, student_nb)

            # Write config for this question
            config = {
                "question_name": question_name or "unknown",
                "context_code": context_code or "",
                "assertions": assertions or [],
            }
            (tmp_path / "config.json").write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            # Write runner script
            (tmp_path / "runner.py").write_text(
                self._build_runner_script(),
                encoding="utf-8",
            )

            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                f"--memory={self.mem_limit}",
                f"--cpus={self.cpu_limit}",
                "--pids-limit", "256",
                "-v", f"{tmp_path}:/workspace",
                "-w", "/workspace",
                self.docker_image,
                "python", "runner.py",
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
            except subprocess.TimeoutExpired:
                return [
                    {
                        "question": question_name or "unknown",
                        "assertion": "[container timeout]",
                        "status": "failed",
                        "error": "Timeout while executing question container.",
                        "score": 0,
                    }
                ]
            except Exception as e:
                return [
                    {
                        "question": question_name or "unknown",
                        "assertion": "[container error]",
                        "status": "failed",
                        "error": f"Error starting Docker container: {e}",
                        "score": 0,
                    }
                ]

            # Read results.json generated by runner.py
            results_file = tmp_path / "results.json"
            if results_file.exists():
                try:
                    results = json.loads(results_file.read_text(encoding="utf-8"))
                    return results
                except Exception:
                    tb = traceback.format_exc()
                    return [
                        {
                            "question": question_name or "unknown",
                            "assertion": "[results parse]",
                            "status": "failed",
                            "error": f"Failed to parse results.json: {tb}",
                            "score": 0,
                        }
                    ]
            else:
                # No results file: surface Docker logs for debugging
                error_msg = (
                    "results.json not produced by runner. "
                    f"stdout:\\n{proc.stdout}\\n\nstderr:\\n{proc.stderr}"
                )
                return [
                    {
                        "question": question_name or "unknown",
                        "assertion": "[container execution]",
                        "status": "failed",
                        "error": error_msg,
                        "score": 0,
                    }
                ]
