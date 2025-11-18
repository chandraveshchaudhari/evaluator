# Evaluator Package Architecture

## Overview

The `evaluator` package (located at `src/evaluator/`) is a production-grade system for automated evaluation of student submissions across multiple file types: Jupyter Notebooks, Python scripts, and Excel files.

## Directory Structure

```
src/evaluator/
├── __init__.py                    # Package exports
├── ingestion/
│   ├── __init__.py
│   └── file_loader.py             # Detect and load .ipynb, .py, .xlsx, .csv
├── parsing/
│   ├── __init__.py
│   ├── notebook_parser.py         # Extract code cells using nbformat
│   └── solution_parser.py         # Extract functions from solution code using AST
├── execution/
│   ├── __init__.py
│   ├── sandbox_runner.py          # Execute notebooks safely with nbclient + timeout
│   └── output_capture.py          # Capture printed output, results, DataFrames
├── comparison/
│   ├── __init__.py
│   ├── function_checker.py        # Compare function outputs (student vs solution)
│   ├── value_checker.py           # Compare scalar values with tolerance
│   └── df_checker.py              # Compare DataFrames (shape, columns, rows)
├── reporting/
│   ├── __init__.py
│   └── report_builder.py          # Generate JSON and CSV reports
├── cli/
│   ├── __init__.py
│   └── main.py                    # CLI entrypoint (argparse-based)
└── utils/
    ├── __init__.py
    ├── io_utils.py                # File I/O helpers
    ├── logging_utils.py           # Logging setup
    └── path_utils.py              # Path helpers (ensure_dir, etc)
```

## Module Reference

### Ingestion (`ingestion/file_loader.py`)

**Purpose:** Scan folders and load submission files.

**Key Functions:**
- `detect_submission_files(folder_path: str) -> List[Dict]`  
  Scan a folder and return metadata for supported files (.ipynb, .py, .xlsx, .csv).

- `load_file(path: str) -> Dict`  
  Load a single file and return a standardized structure with content and metadata.

**Example:**
```python
from evaluator.ingestion import file_loader

files = file_loader.detect_submission_files("./data/submissions/")
for f in files:
    meta = file_loader.load_file(f["path"])
    print(meta)
```

### Parsing (`parsing/`)

#### `notebook_parser.py`
**Purpose:** Extract code cells and metadata from notebooks using nbformat.

**Key Functions:**
- `extract_code_cells(notebook_path: str) -> List[str]`  
  Return a list of Python code from all code cells in a notebook.

- `parse_notebook(notebook_path: str) -> Dict`  
  Return notebook structure including code_cells and metadata.

#### `solution_parser.py`
**Purpose:** Extract function definitions from instructor solution using AST.

**Key Functions:**
- `extract_functions_from_py(py_file_path: str) -> Dict[str, str]`  
  Parse a .py file and return a mapping `{function_name: source_code}`.

**Example:**
```python
from evaluator.parsing import solution_parser

funcs = solution_parser.extract_functions_from_py("./solution.py")
for name, source in funcs.items():
    print(f"Function {name}:")
    print(source)
```

### Execution (`execution/`)

#### `sandbox_runner.py`
**Purpose:** Execute notebooks safely in an isolated environment.

**Key Functions:**
- `run_notebook(notebook_path: str, timeout: int = 120) -> Dict`  
  Execute a notebook and return status. Returns `{ok: bool, nb: NotebookNode, error: optional str}`.

**Limitations:**
- Timeouts enforce execution time limits but do not prevent:
  - Disk access
  - Network calls
  - System calls

**Deploy in container if full sandboxing required.**

#### `output_capture.py`
**Purpose:** Extract and normalize outputs from executed notebooks.

**Key Functions:**
- `capture_outputs(nb) -> Dict`  
  Scan an executed notebook and return structured outputs: printed text, results, DataFrames.

### Comparison (`comparison/`)

#### `function_checker.py`
**Purpose:** Run student and solution functions with the same inputs and compare outputs.

**Key Functions:**
- `compare_function_outputs(student_fn, solution_fn, *args, tolerance=1e-9, **kwargs) -> (bool, result_s, result_solution)`

#### `value_checker.py`
**Purpose:** Compare scalar values with optional numeric tolerance.

**Key Functions:**
- `compare_values(expected: Any, actual: Any, tolerance=1e-9) -> bool`

#### `df_checker.py`
**Purpose:** Compare DataFrames (shape, columns, sample rows).

**Key Functions:**
- `compare_dataframes(expected: pd.DataFrame, actual: pd.DataFrame, sample_rows=5) -> Dict`  
  Returns `{shape_ok: bool, columns_ok: bool, sample_matches: List[bool], details: Dict}`.

### Reporting (`reporting/report_builder.py`)

**Purpose:** Serialize evaluation results to JSON and CSV.

**Key Functions:**
- `build_json_report(result: Dict, out_path: str) -> str`  
  Write result dict as JSON and return file path.

- `build_csv_summary(rows: List[Dict], out_path: str) -> str`  
  Write per-student rows to CSV and return file path.

**Example:**
```python
from evaluator.reporting import report_builder

summary = [
    {"name": "Alice", "score": 95, "status": "pass"},
    {"name": "Bob", "score": 70, "status": "fail"},
]
report_builder.build_csv_summary(summary, "./reports/summary.csv")
```

### CLI (`cli/main.py`)

**Purpose:** Command-line entry point for batch evaluation.

**Usage:**
```bash
python -m evaluator.cli.main evaluate \
    --submissions ./data/submissions/ \
    --output ./reports/
```

**Current Implementation:** Placeholder that lists files. Will be extended to run full pipeline.

### Utils (`utils/`)

**Small helper modules:**
- `io_utils.py`: `read_text_file(path, encoding="utf8") -> str`
- `logging_utils.py`: `get_logger(name, level) -> logging.Logger`
- `path_utils.py`: `ensure_dir(path) -> None`

## Import Patterns

All modules are designed to be imported directly. Examples:

```python
# Ingestion
from evaluator.ingestion import file_loader

# Parsing
from evaluator.parsing import notebook_parser, solution_parser

# Execution
from evaluator.execution import sandbox_runner, output_capture

# Comparison
from evaluator.comparison import function_checker, value_checker, df_checker

# Reporting
from evaluator.reporting import report_builder

# CLI
from evaluator.cli import main

# Utils
from evaluator.utils import io_utils, logging_utils, path_utils
```

## Dependencies

Required packages (see `requirements.txt`):
- `nbformat` (Jupyter notebook format library)
- `nbclient` (Notebook execution client)
- `pandas` (DataFrame support)
- `openpyxl` (Excel file support)

Optional:
- `xlwings` (Windows-only; enhanced Excel formula extraction)

## Design Principles

1. **Modularity**: Each subpackage has a single responsibility.
2. **Composability**: Modules are independent and can be used together.
3. **Type Hints**: All functions have modern Python 3.10+ type annotations.
4. **Immutability**: Functions are pure where possible; avoid side effects.
5. **Testability**: Small, focused functions with clear contracts.
6. **No Hardcoded Paths**: All paths are passed as arguments.

## Execution Flow (Typical Workflow)

```
1. Ingest: detect_submission_files() → list of file metadata
2. Parse:  parse_notebook() or extract_functions_from_py() → AST/code structure
3. Execute: run_notebook() → executed notebook object
4. Capture: capture_outputs() → normalized results
5. Compare: compare_function_outputs() / compare_values() / compare_dataframes()
6. Report: build_json_report() or build_csv_summary()
```

## Future Extensions

- Add containerized sandbox execution (Docker).
- Extend CLI to support full pipeline.
- Add test case templates.
- Support for other languages (R, Julia).
- Automated rubric scoring.
