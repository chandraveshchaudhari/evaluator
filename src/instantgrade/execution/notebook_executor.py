from pathlib import Path
import tempfile
import shutil
import subprocess
import json
import textwrap


class NotebookExecutor:
    """
    Executes a Jupyter notebook in a Docker sandbox and returns a summary.
    No student code is ever executed on the host Python interpreter.
    """

    def __init__(self, timeout: int = 60, docker_image: str = "python:3.11-slim"):
        self.timeout = timeout
        self.docker_image = docker_image

    def _build_runner_script(self) -> str:
        """
        Python script that will run inside the Docker container
        to execute the notebook once and collect global errors.
        """
        return textwrap.dedent(
            """
            import json
            import nbformat
            import traceback
            import builtins
            import os

            errors = []

            # Disable input() so it never blocks
            def dummy_input(prompt=None):
                msg = "[Warning] input() called during global execution — ignored."
                errors.append(msg)
                return ""
            builtins.input = dummy_input

            # Disable os.kill to prevent process killing inside container
            def safe_kill(*args, **kwargs):
                raise RuntimeError("os.kill is disabled in sandbox")
            os.kill = safe_kill

            try:
                nb = nbformat.read("student.ipynb", as_version=4)
            except Exception:
                errors.append("Failed to read notebook:\\n" + traceback.format_exc())
                result = {"success": False, "errors": errors}
                with open("execution_summary.json", "w", encoding="utf-8") as f:
                    json.dump(result, f)
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
                        errors.append("Error in cell:\\n" + traceback.format_exc())
            except Exception:
                errors.append("Unexpected error during execution:\\n" + traceback.format_exc())

            result = {
                "success": len(errors) == 0,
                "errors": errors,
            }

            with open("execution_summary.json", "w", encoding="utf-8") as f:
                json.dump(result, f)
            """
        )

    def run_notebook(self, path: Path) -> dict:
        """
        Execute notebook once in Docker and return a summary dict:

        {
            "success": bool,
            "errors": [str],
            "docker_stdout": "...",
            "docker_stderr": "..."
        }
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Notebook not found: {path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            student_nb = tmp_path / "student.ipynb"
            shutil.copy(path, student_nb)

            runner_py = tmp_path / "runner.py"
            runner_py.write_text(self._build_runner_script(), encoding="utf-8")

            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                f"--memory=1g",
                f"--cpus=1.0",
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
                    timeout=self.timeout,
                )
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "errors": ["Global notebook execution timed out."],
                    "docker_stdout": "",
                    "docker_stderr": "",
                }

            summary_file = tmp_path / "execution_summary.json"
            if summary_file.exists():
                summary = json.loads(summary_file.read_text(encoding="utf-8"))
            else:
                summary = {
                    "success": False,
                    "errors": ["execution_summary.json not produced by container."],
                }

            summary["docker_stdout"] = proc.stdout
            summary["docker_stderr"] = proc.stderr
            return summary
