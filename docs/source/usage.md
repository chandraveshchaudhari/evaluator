# Usage Guide

This guide covers all features and configuration options available in InstantGrade.

## Basic Usage

### Python API

The primary way to use InstantGrade is through the Python API:

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="path/to/solution.ipynb",
    submissions_dir="path/to/submissions/",
    report_dir="path/to/reports/"
)

results = evaluator.run()
```

### Command-Line Interface

InstantGrade also provides a CLI:

```bash
instantgrade evaluate solution.ipynb submissions/ --report-dir reports/
```

## Supported File Types

### Jupyter Notebooks (.ipynb)

```python
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)
evaluator.run()
```

**Features:**
- Cell-by-cell execution and comparison
- Output comparison (text, images, data)
- Variable state tracking
- Error capture and reporting

### Excel Files (.xlsx, .xls)

```python
evaluator = Evaluator(
    solution_path="solution.xlsx",
    submissions_dir="submissions/",
    report_dir="reports/"
)
evaluator.run()
```

**Features:**
- Multi-sheet comparison
- Cell value comparison
- Formula validation
- Formatting preservation

## Configuration Options

### Evaluator Parameters

```python
evaluator = Evaluator(
    solution_path="solution.ipynb",      # Path to reference solution
    submissions_dir="submissions/",       # Directory with submissions
    report_dir="reports/",                # Output directory for reports
    timeout=300,                          # Execution timeout (seconds)
    allow_errors=False,                   # Continue on cell errors
    compare_outputs=True,                 # Compare cell outputs
    compare_variables=True,               # Compare variable states
    ignore_patterns=["*.tmp", "*.log"]   # Files to ignore
)
```

### Timeout Configuration

Control how long each notebook can execute:

```python
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    timeout=600  # 10 minutes
)
```

### Error Handling

Choose how to handle execution errors:

```python
# Stop on first error (default)
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    allow_errors=False
)

# Continue despite errors
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    allow_errors=True
)
```

## Directory Structure

### Recommended Layout

```
project/
├── solutions/
│   ├── assignment1.ipynb
│   └── assignment2.ipynb
├── submissions/
│   ├── assignment1/
│   │   ├── student1.ipynb
│   │   ├── student2.ipynb
│   │   └── student3.ipynb
│   └── assignment2/
│       ├── student1.ipynb
│       └── student2.ipynb
└── reports/
    ├── assignment1/
    │   ├── student1_report.html
    │   ├── student2_report.html
    │   └── student3_report.html
    └── assignment2/
        ├── student1_report.html
        └── student2_report.html
```

### Working with Multiple Assignments

```python
assignments = [
    {
        "solution": "solutions/assignment1.ipynb",
        "submissions": "submissions/assignment1/",
        "reports": "reports/assignment1/"
    },
    {
        "solution": "solutions/assignment2.ipynb",
        "submissions": "submissions/assignment2/",
        "reports": "reports/assignment2/"
    }
]

for assignment in assignments:
    evaluator = Evaluator(
        solution_path=assignment["solution"],
        submissions_dir=assignment["submissions"],
        report_dir=assignment["reports"]
    )
    evaluator.run()
    print(f"Completed: {assignment['solution']}")
```

## Report Format

### HTML Reports

Reports are generated in HTML format with:

- **Summary section**: Overall score and status
- **Cell comparisons**: Side-by-side output comparison
- **Difference highlighting**: Visual indicators for mismatches
- **Error logs**: Detailed error messages
- **Execution metadata**: Timestamps, versions, environment info

### Report Location

Reports are saved with the following naming convention:

```
reports/
├── report_YYYYMMDD_HHMMSS.html
└── student_name_report.html
```

### Accessing Report Data

```python
results = evaluator.run()

for result in results:
    print(f"File: {result.filename}")
    print(f"Score: {result.score}")
    print(f"Status: {result.status}")
    print(f"Report: {result.report_path}")
```

## Advanced Features

### Custom Comparison Logic

You can extend InstantGrade with custom comparison logic:

```python
from instantgrade import Evaluator
from instantgrade.comparison import ComparisonService

class CustomComparison(ComparisonService):
    def compare_outputs(self, expected, actual):
        # Your custom comparison logic
        pass

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    comparison_service=CustomComparison()
)
```

### Filtering Submissions

Process only specific submissions:

```python
import os
from instantgrade import Evaluator

submissions_dir = "submissions/"
filtered_submissions = [
    f for f in os.listdir(submissions_dir)
    if f.startswith("student_") and f.endswith(".ipynb")
]

for submission in filtered_submissions:
    # Process each submission
    pass
```

### Parallel Processing

Process multiple submissions in parallel:

```python
from concurrent.futures import ThreadPoolExecutor
from instantgrade import Evaluator

def evaluate_submission(submission_file):
    evaluator = Evaluator(
        solution_path="solution.ipynb",
        submissions_dir="submissions/",
        report_dir="reports/"
    )
    return evaluator.run()

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(evaluate_submission, submission_files)
```

## CLI Advanced Usage

### Verbose Output

```bash
instantgrade evaluate solution.ipynb submissions/ --verbose
```

### Custom Report Directory

```bash
instantgrade evaluate solution.ipynb submissions/ \
    --report-dir custom_reports/ \
    --timeout 600
```

### Batch Processing

```bash
# Process multiple assignments
for solution in solutions/*.ipynb; do
    name=$(basename "$solution" .ipynb)
    instantgrade evaluate "$solution" \
        "submissions/$name/" \
        --report-dir "reports/$name/"
done
```

## Environment Variables

Configure InstantGrade using environment variables:

```bash
export INSTANTGRADE_TIMEOUT=600
export INSTANTGRADE_REPORT_DIR=reports/
```

```python
import os
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir=os.getenv("INSTANTGRADE_REPORT_DIR", "reports/"),
    timeout=int(os.getenv("INSTANTGRADE_TIMEOUT", "300"))
)
```

## Best Practices

### 1. Version Control Solutions

Keep your solution files in version control:

```bash
git init
git add solutions/
git commit -m "Add assignment solutions"
```

### 2. Test Solutions First

Always test your solution notebooks:

```python
from instantgrade import Evaluator

# Test the solution itself
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="solutions/",  # Use solution as submission
    report_dir="tests/"
)
evaluator.run()
```

### 3. Clear Notebook Outputs

Clear outputs before distributing:

```bash
jupyter nbconvert --clear-output --inplace solution.ipynb
```

### 4. Document Expected Outputs

Add markdown cells explaining what each cell should produce:

```markdown
## Expected Output

This cell should print:
- Mean score: XX.XX
- Median score: XX.XX
```

### 5. Use Meaningful Names

```
submissions/
├── john_doe_assignment1.ipynb
├── jane_smith_assignment1.ipynb
└── bob_jones_assignment1.ipynb
```

### 6. Automate with Scripts

Create reusable grading scripts:

```python
# grade_all.py
from instantgrade import Evaluator
import sys

def grade_assignment(assignment_name):
    evaluator = Evaluator(
        solution_path=f"solutions/{assignment_name}.ipynb",
        submissions_dir=f"submissions/{assignment_name}/",
        report_dir=f"reports/{assignment_name}/"
    )
    results = evaluator.run()
    print(f"Graded {len(results)} submissions")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grade_all.py <assignment_name>")
        sys.exit(1)
    
    grade_assignment(sys.argv[1])
```

## Troubleshooting

### Common Issues

**Issue**: Notebook execution timeout
```python
# Increase timeout
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    timeout=1200  # 20 minutes
)
```

**Issue**: Missing dependencies in student notebooks
```python
# Allow errors to continue evaluation
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    allow_errors=True
)
```

**Issue**: Excel file not opening
```bash
# Install openpyxl
pip install openpyxl
```

## Next Steps

- Explore [Examples](examples.md) for real-world scenarios
- Check [API Reference](api.md) for detailed documentation
- Visit [GitHub](https://github.com/chandraveshchaudhari/instantgrade) for updates
