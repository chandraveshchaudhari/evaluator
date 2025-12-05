"""
grader.py — Runs inside Docker to grade one student notebook.

Responsibilities:
  1. Load instructor solution notebook directly (SolutionIngestion)
  2. Load and execute student notebook (NotebookExecutor)
  3. Compare outputs question-by-question (ComparisonService)
  4. Save compact results.json to /workspace/
"""

import json
import traceback
from pathlib import Path
from instantgrade.ingestion.solution_ingestion import SolutionIngestion
from instantgrade.execution.notebook_executor import NotebookExecutor
from instantgrade.comparison.comparison_service import ComparisonService


def main():
    print("[grader] Starting grading...")

    solution_path = Path("/workspace/solution.ipynb")
    student_path = Path("/workspace/student.ipynb")
    results_path = Path("/workspace/results.json")

    # 1. Load instructor solution
    print(f"[grader] Loading solution: {solution_path}")
    solution_service = SolutionIngestion(solution_path)
    sol = solution_service.understand_notebook_solution()
    questions = sol.get("questions", {})
    metadata = sol.get("metadata", {})

    # 2. Execute student notebook safely
    print(f"[grader] Executing student notebook: {student_path}")
    executor = NotebookExecutor(timeout=60)
    exec_result = executor.run_notebook(student_path)

    namespace = exec_result.get("namespace", {})
    errors = exec_result.get("errors", [])
    tb_text = exec_result.get("traceback")

    # 3. Validate mandatory metadata
    student_name = str(namespace.get("name", "")).strip()
    student_roll = str(namespace.get("roll_number", "")).strip()
    default_name = metadata.get("name")
    default_roll = metadata.get("roll_number")

    if not student_name or not student_roll or \
       student_name == default_name or student_roll == default_roll:
        print("[grader] Missing or default name/roll_number — skipping grading.")
        result_dict = {
            "student": {
                "name": student_name or "Unknown",
                "roll_number": student_roll or "Unknown",
            },
            "results": [],
            "note": "Grading skipped due to missing name or roll number."
        }
        results_path.write_text(json.dumps(result_dict, indent=2))
        print(f"[grader] Results written: {results_path}")
        return

    # 4. Run comparisons for each question
    comparator = ComparisonService()
    all_results = []

    for qname, qdata in questions.items():
        print(f"[grader] Running question: {qname}")
        context_code = qdata.get("context_code", "")
        assertions = qdata.get("tests", [])
        desc = qdata.get("description", "")

        try:
            q_results = comparator.run_assertions(
                student_namespace=namespace.copy(),
                assertions=assertions,
                question_name=qname,
                context_code=context_code,
            )
            for r in q_results:
                r["description"] = desc
            all_results.extend(q_results)
        except Exception:
            tb = traceback.format_exc()
            print(f"[grader] Fatal error in {qname}:\n{tb}")
            all_results.append({
                "question": qname,
                "assertion": "[internal grader failure]",
                "status": "failed",
                "error": tb,
                "score": 0
            })

    # 5. Write results.json
    output = {
        "student": {"name": student_name, "roll_number": student_roll},
        "results": all_results,
        "notebook_errors": errors,
        "traceback": tb_text,
    }

    try:
        results_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"[grader] Results written to {results_path}")
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[grader] Fatal error while writing results.json:\n{tb}")
        results_path.write_text(
            json.dumps({"student": {}, "error": str(e), "traceback": tb}, indent=2),
            encoding="utf-8"
        )


if __name__ == "__main__":
    main()
