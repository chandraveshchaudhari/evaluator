import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional
from importlib.resources import files
from instantgrade.utils.logger import setup_logger


class ExecutionServiceDocker:
    """
    Executes each student's notebook inside Docker.

    Workflow:
      1. Ensure Docker image exists (auto-build if missing)
      2. Copy solution.ipynb, student.ipynb, grader.py to temp dir
      3. Run docker container using prebuilt image
      4. Stream logs, enforce per-student timeout
      5. Parse /workspace/results.json
    """

    def __init__(
        self,
        docker_image: str = "instantgrade:latest",
        base_image: str = "python:3.11-slim",
        per_student_timeout: int = 1800,
        memory_limit: str = "1g",
        cpu_limit: str = "1.0",
        pids_limit: int = 256,
        network_mode: str = "none",
        debug: bool = False,
        logger=None,
    ):
        self.docker_image = docker_image
        self.base_image = base_image
        self.per_student_timeout = per_student_timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.pids_limit = pids_limit
        self.network_mode = network_mode
        self.debug = debug
        self.logger = logger or setup_logger(level="normal")

        self.ensure_docker_image_exists()

    # ----------------------------------------------------------------------
    def ensure_docker_image_exists(self):
        """Check if docker image exists locally, build it if missing."""
        try:
            result = subprocess.run(
                ["docker", "images", "-q", self.docker_image],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                self.logger.info(f"[Docker] Found prebuilt image {self.docker_image}")
                return
        except Exception:
            self.logger.warning("[Docker] Could not verify image presence, attempting build...")

        self.logger.info(f"[Docker] Building base image {self.docker_image} from {self.base_image}...")

        dockerfile_content = f"""

        FROM {self.base_image}

        # Install base dependencies
        RUN pip install --no-cache-dir nbformat nbclient pandas openpyxl

        # Copy InstantGrade source code into image
        COPY instantgrade /instantgrade
        ENV PYTHONPATH=/instantgrade:$PYTHONPATH

        # Copy the grader
        COPY grader.py /usr/local/bin/grader.py

        WORKDIR /workspace
        ENTRYPOINT ["python", "/usr/local/bin/grader.py"]
        """


        with tempfile.TemporaryDirectory() as tmpdir:
            dockerfile_path = Path(tmpdir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content, encoding="utf-8")
            grader_source = files("instantgrade.execution.resources").joinpath("grader.py")
            shutil.copy(grader_source, Path(tmpdir) / "grader.py")

            cmd = [
                "docker", "build",
                "-t", self.docker_image,
                "-f", str(dockerfile_path),
                str(Path(".").resolve())  # <-- build context is repo root
            ]

            build_proc = subprocess.run(cmd, capture_output=True, text=True)
            if build_proc.returncode == 0:
                self.logger.info(f"[Docker] Built image {self.docker_image} successfully.")
            else:
                self.logger.error(f"[Docker] Failed to build image: {build_proc.stderr}")
                raise RuntimeError("Docker image build failed.")

    # ----------------------------------------------------------------------
    def execute_student(self, solution_path: Path, submission_path: Path) -> Dict[str, Any]:
        """Run grading for a single student notebook inside Docker."""
        submission_path = Path(submission_path)
        solution_path = Path(solution_path)
        start_time = time.time()
        self.logger.info(f"[Docker] Starting grading for {submission_path.name}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # 1. Copy solution, student, and grader into workspace
            shutil.copy(solution_path, tmpdir_path / "solution.ipynb")
            shutil.copy(submission_path, tmpdir_path / "student.ipynb")
            grader_source = files("instantgrade.execution.resources").joinpath("grader.py")
            shutil.copy(grader_source, tmpdir_path / "grader.py")

            # 2. Build docker run command
            cmd = [
                "docker", "run", "--rm",
                "--network", self.network_mode,
                "--memory", self.memory_limit,
                "--cpus", self.cpu_limit,
                "--pids-limit", str(self.pids_limit),
                "-v", f"{tmpdir_path}:/workspace",
                "-w", "/workspace",
                self.docker_image
            ]

            if self.debug:
                self.logger.debug("Docker command: " + " ".join(cmd))

            # 3. Run docker container and stream logs
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
            except Exception as e:
                elapsed = round(time.time() - start_time, 2)
                msg = f"Failed to start Docker container: {e}"
                return self._make_error_result(submission_path, msg, elapsed)

            stdout_lines = []
            hard_timeout = False

            try:
                while True:
                    elapsed = time.time() - start_time
                    if elapsed > self.per_student_timeout:
                        hard_timeout = True
                        self.logger.warning(
                            f"[Docker] Timeout {elapsed:.1f}s exceeded for {submission_path.name}, killing."
                        )
                        proc.kill()
                        break

                    line = proc.stdout.readline()
                    if not line:
                        if proc.poll() is not None:
                            break
                        time.sleep(0.05)
                        continue

                    line = line.rstrip("\n")
                    stdout_lines.append(line)
                    self.logger.info(f"[{submission_path.name}][docker] {line}")

                proc.wait(timeout=5)
            except Exception as e:
                self.logger.exception(f"[Docker] Error reading logs: {e}")
                proc.kill()
                hard_timeout = True

            elapsed = round(time.time() - start_time, 2)
            full_stdout = "\n".join(stdout_lines)

            if hard_timeout:
                return self._make_error_result(
                    submission_path, "Timeout exceeded", elapsed, stdout=full_stdout
                )

            # 4. Parse results.json
            results_file = tmpdir_path / "results.json"
            if not results_file.exists():
                self.logger.warning(f"[grader] results.json not found in /workspace for {submission_path.name}.")
                return self._make_error_result(
                    submission_path, "Missing results.json", elapsed, stdout=full_stdout
                )

            try:
                graded = json.loads(results_file.read_text(encoding="utf-8"))
            except Exception as e:
                msg = f"Failed to parse results.json: {e}"
                self.logger.exception(msg)
                return self._make_error_result(
                    submission_path, msg, elapsed, stdout=full_stdout
                )

            # 5. Return structured result
            student_meta = graded.get("student", {})
            results = graded.get("results", [])

            return {
                "student_path": submission_path,
                "execution": {
                    "success": True,
                    "elapsed": elapsed,
                    "stdout": full_stdout,
                    "student_meta": student_meta,
                },
                "results": results,
            }

    # ----------------------------------------------------------------------
    def _make_error_result(
        self, submission_path: Path, message: str, elapsed: float, stdout: str = ""
    ) -> Dict[str, Any]:
        """Build consistent error structure."""
        return {
            "student_path": submission_path,
            "execution": {
                "success": False,
                "elapsed": elapsed,
                "stdout": stdout,
                "errors": [message],
                "student_meta": {"name": "Unknown", "roll_number": "Unknown"},
            },
            "results": [],
        }
