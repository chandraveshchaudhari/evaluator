# ======================================

# ⭐ **GITHUB COPILOT INSTRUCTION**

# (Custom Designed for Your Exact Workflow)

# ======================================

**You must always follow this exact workflow when generating code for the evaluator package.**

## 1. The Instructor Notebook is the Single Source of Truth

When generating or handling instructor notebooks:

* The notebook contains, for each question:

  1. A correct function (e.g., `def question_one(...): ...`)
  2. A block of assertions for that function

Example:

```python
def question_one(nums):
    return sum(set(nums))

assert question_one([1,2,2,3]) == 6
assert question_one([]) == 0
```

Copilot must ensure:

* Assertions are *directly beneath* the correct function
* All test logic stays inside the instructor notebook
* No separate test modules are created

## 2. Extract Both Functions and Assertions

When generating code for the evaluator:

* Load the instructor notebook using `nbformat`

* Identify code cells that contain:

  * Function definitions (`def question_...`)
  * Assertions (`assert ...`)

* For each question, build a dictionary like:

```python
tests = {
    "question_one": [
        "assert question_one([1,2,2,3]) == 6",
        "assert question_one([]) == 0",
    ],
    ...
}
```

## 3. Execution of Instructor Tests

Before evaluating students:

1. Import the instructor function definitions into a sandbox execution environment
2. Run **all extracted assertions for all questions**
3. If an instructor function fails any assertion, the evaluator must:

   * Report “Instructor error—fix instructor solution”
   * Stop the evaluation pipeline

This ensures the instructor notebook is fully valid.

## 4. Student Notebook Evaluation

For every student notebook:

* Load the notebook with `nbformat`
* Extract student function definitions (e.g., `def question_one`)
* Maintain a record:

```python
student_meta = {
    "name": "...",
    "roll_number": "...",
}
```

These will be parsed from:

* either a metadata cell
* OR a filename convention
* OR the first markdown cell

Copilot must always implement all three fallback methods.

## 5. Running Assertions on Student Code

For each question:

1. Replace instructor function in sandbox with **student function**
2. Execute each assertion under try/except:

```python
try:
    exec(assertion_text, sandbox)
    result = "PASS"
except Exception as e:
    result = "FAIL"
    error = str(e)
```

3. Save the result regardless of pass/fail
4. Continue testing other questions
5. Never stop execution on failure

All student results should be stored like:

```python
student_results = {
    "question_one": {
        "passed": True,
        "errors": []
    },
    "question_two": {
        "passed": False,
        "errors": ["AssertionError: expected ..."]
    },
    ...
}
```

## 6. Final Report

Copilot must always generate a reporting module that:

* Saves all results in:

  * JSON
  * CSV (for gradebook)
  * Optional HTML summary

* One row per student:

  * Name
  * Roll number
  * Score
  * Per-question status

---

# ======================================

# ⭐ REQUIRED MODULES FOR THE PACKAGE

# ======================================

Copilot must always build the following modules:

```
evaluator/
    ingestion/
        load_instructor_notebook.py
        load_student_notebook.py

    parsing/
        extract_functions.py
        extract_assertions.py

    execution/
        sandbox.py
        run_assertions.py

    reporting/
        report_builder.py
        gradebook_writer.py

    cli/
        main.py
```

The evaluator must always use:

* `nbformat` for reading notebooks
* `exec()` inside a sandbox dictionary for executing code
* Safe exception capture
* Deterministic ordering of test execution

---

# ======================================

# ⭐ SUMMARY FOR COPILOT

# ======================================

**Always do the following when generating code for this repository:**

1. Treat the instructor notebook as the **only** source of correct code and tests
2. Extract functions + assertions
3. Validate the instructor notebook before evaluating students
4. Evaluate each student by:

   * loading their functions
   * running instructor assertions
   * collecting all errors without stopping
5. Produce detailed reports for each student
6. Generate clean, modular code inside the evaluator package

# ======================================

# END OF GITHUB COPILOT INSTRUCTION

# ======================================