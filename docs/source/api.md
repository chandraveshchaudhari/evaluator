# API Reference

Complete API documentation for InstantGrade.

## Core Classes

```{eval-rst}
.. automodule:: instantgrade
   :members:
   :undoc-members:
   :show-inheritance:
```

## Evaluator

The main class for running evaluations.

```{eval-rst}
.. autoclass:: instantgrade.Evaluator
   :members:
   :special-members: __init__
   :show-inheritance:
```

### Constructor

```python
Evaluator(solution_path, submissions_dir, report_dir, **kwargs)
```

**Parameters:**

- `solution_path` (str): Path to the reference solution file
- `submissions_dir` (str): Directory containing student submissions
- `report_dir` (str): Directory for output reports
- `timeout` (int, optional): Execution timeout in seconds (default: 300)
- `allow_errors` (bool, optional): Continue on errors (default: False)
- `compare_outputs` (bool, optional): Compare cell outputs (default: True)
- `compare_variables` (bool, optional): Compare variable states (default: True)

**Returns:**
- Evaluator instance

### Methods

#### run()

Execute the evaluation process.

```python
results = evaluator.run()
```

**Returns:**
- List of evaluation results

## Ingestion Services

Services for loading solution and submission files.

```{eval-rst}
.. automodule:: instantgrade.ingestion
   :members:
   :undoc-members:
   :show-inheritance:
```

### SolutionIngestion

```{eval-rst}
.. autoclass:: instantgrade.ingestion.SolutionIngestion
   :members:
   :show-inheritance:
```

### IngestionService

```{eval-rst}
.. autoclass:: instantgrade.ingestion.IngestionService
   :members:
   :show-inheritance:
```

## Execution Services

Services for executing notebooks and Excel files.

```{eval-rst}
.. automodule:: instantgrade.execution
   :members:
   :undoc-members:
   :show-inheritance:
```

### NotebookExecutor

```{eval-rst}
.. autoclass:: instantgrade.execution.NotebookExecutor
   :members:
   :show-inheritance:
```

## Comparison Services

Services for comparing outputs and generating scores.

```{eval-rst}
.. automodule:: instantgrade.comparison
   :members:
   :undoc-members:
   :show-inheritance:
```

### ComparisonService

```{eval-rst}
.. autoclass:: instantgrade.comparison.ComparisonService
   :members:
   :show-inheritance:
```

## Reporting Services

Services for generating HTML reports.

```{eval-rst}
.. automodule:: instantgrade.reporting
   :members:
   :undoc-members:
   :show-inheritance:
```

### ReportingService

```{eval-rst}
.. autoclass:: instantgrade.reporting.ReportingService
   :members:
   :show-inheritance:
```

## Utility Functions

Helper functions and utilities.

```{eval-rst}
.. automodule:: instantgrade.utils
   :members:
   :undoc-members:
   :show-inheritance:
```

### Path Utilities

```{eval-rst}
.. automodule:: instantgrade.utils.path_utils
   :members:
   :show-inheritance:
```

### I/O Utilities

```{eval-rst}
.. automodule:: instantgrade.utils.io_utils
   :members:
   :show-inheritance:
```

## Command-Line Interface

The CLI module for terminal usage.

```{eval-rst}
.. automodule:: instantgrade.cli.main
   :members:
   :undoc-members:
   :show-inheritance:
```

## Data Models

### EvaluationResult

Result object returned by the evaluator.

**Attributes:**

- `filename` (str): Name of the evaluated submission
- `score` (float): Score out of 100
- `status` (str): Evaluation status ('PASSED', 'FAILED', 'ERROR')
- `report_path` (str): Path to the generated HTML report
- `execution_time` (float): Time taken to execute (seconds)
- `error_message` (str, optional): Error message if evaluation failed

**Example:**

```python
results = evaluator.run()
for result in results:
    print(f"{result.filename}: {result.score}/100")
    print(f"Status: {result.status}")
    print(f"Report: {result.report_path}")
```

## Exceptions

### EvaluationError

Raised when evaluation fails.

```python
class EvaluationError(Exception):
    """Raised when evaluation process fails."""
    pass
```

### ExecutionError

Raised when notebook execution fails.

```python
class ExecutionError(Exception):
    """Raised when notebook execution fails."""
    pass
```

### IngestionError

Raised when file ingestion fails.

```python
class IngestionError(Exception):
    """Raised when file loading fails."""
    pass
```

## Constants

```python
# Default timeout for notebook execution (seconds)
DEFAULT_TIMEOUT = 300

# Supported file extensions
SUPPORTED_NOTEBOOK_EXTENSIONS = ['.ipynb']
SUPPORTED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']

# Report template
DEFAULT_REPORT_TEMPLATE = 'default.html'
```

## Type Hints

InstantGrade uses type hints throughout the codebase:

```python
from typing import List, Dict, Optional, Union
from pathlib import Path

def evaluate_submission(
    solution_path: Union[str, Path],
    submission_path: Union[str, Path],
    timeout: Optional[int] = None
) -> Dict[str, any]:
    """Evaluate a single submission."""
    pass
```

## Usage Examples

### Basic Usage

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

results = evaluator.run()
```

### With Type Hints

```python
from instantgrade import Evaluator
from typing import List

def grade_assignments(
    solution: str,
    submissions: str,
    output: str
) -> List[dict]:
    evaluator: Evaluator = Evaluator(
        solution_path=solution,
        submissions_dir=submissions,
        report_dir=output
    )
    return evaluator.run()
```

### Error Handling

```python
from instantgrade import Evaluator, EvaluationError

try:
    evaluator = Evaluator(
        solution_path="solution.ipynb",
        submissions_dir="submissions/",
        report_dir="reports/"
    )
    results = evaluator.run()
except EvaluationError as e:
    print(f"Evaluation failed: {e}")
```

## Advanced API Usage

### Custom Comparison

```python
from instantgrade import Evaluator
from instantgrade.comparison import ComparisonService

class CustomComparison(ComparisonService):
    def compare_outputs(self, expected, actual):
        # Custom logic here
        return super().compare_outputs(expected, actual)

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    comparison_service=CustomComparison()
)
```

### Custom Reporting

```python
from instantgrade import Evaluator
from instantgrade.reporting import ReportingService

class CustomReporting(ReportingService):
    def generate_report(self, comparison_result):
        # Custom report generation
        pass

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    reporting_service=CustomReporting()
)
```

## See Also

- [Usage Guide](usage.md) - Practical usage examples
- [Examples](examples.md) - Real-world scenarios
- [GitHub Repository](https://github.com/chandraveshchaudhari/instantgrade) - Source code
