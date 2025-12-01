# Quick Start Guide

This guide will help you get started with InstantGrade in just a few minutes.

## Basic Workflow

The typical InstantGrade workflow consists of three steps:

1. **Prepare** - Set up your solution file and student submissions
2. **Evaluate** - Run InstantGrade to compare submissions
3. **Review** - Check the generated HTML reports

## Your First Evaluation

### Step 1: Install InstantGrade

```bash
pip install instantgrade
```

### Step 2: Prepare Your Files

Create a directory structure like this:

```
my_assignment/
├── solution.ipynb          # Reference solution
└── submissions/            # Student submissions
    ├── student1.ipynb
    ├── student2.ipynb
    └── student3.ipynb
```

### Step 3: Create a Simple Solution

Create `solution.ipynb` with some cells:

```python
# Cell 1: Import libraries
import pandas as pd
import numpy as np

# Cell 2: Create data
data = {'name': ['Alice', 'Bob'], 'score': [95, 87]}
df = pd.DataFrame(data)

# Cell 3: Calculate mean
mean_score = df['score'].mean()
print(f"Mean score: {mean_score}")
```

### Step 4: Run Evaluation (Python API)

Create a Python script `grade.py`:

```python
from instantgrade import Evaluator

# Initialize evaluator
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

# Run evaluation
evaluator.run()

print("Grading complete! Check the reports/ directory.")
```

Run it:

```bash
python grade.py
```

### Step 5: Run Evaluation (CLI)

Alternatively, use the command-line interface:

```bash
instantgrade evaluate solution.ipynb submissions/ --report-dir reports/
```

### Step 6: View Results

Open the HTML reports in `reports/` directory:

- Each submission gets its own detailed report
- Reports show cell-by-cell comparisons
- Differences are highlighted
- Scores and metrics are calculated

## Understanding the Output

### Report Structure

Each report contains:

1. **Summary Section**
   - Overall score
   - Execution status
   - Timestamp

2. **Cell Comparison**
   - Side-by-side output comparison
   - Differences highlighted
   - Error messages if any

3. **Detailed Metrics**
   - Cell execution times
   - Output matches/mismatches
   - Variable comparisons

### Example Report Preview

```
=================================
InstantGrade Evaluation Report
=================================

Student: student1.ipynb
Evaluated: 2025-12-01 14:30:00
Status: PASSED
Score: 95/100

Cell 1: ✅ MATCH
  Expected: Mean score: 91.0
  Got:      Mean score: 91.0

Cell 2: ⚠️  MISMATCH
  Expected: [1, 2, 3]
  Got:      [1, 2, 4]
```

## Excel Example

InstantGrade also works with Excel files!

### Excel Workflow

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="solution.xlsx",
    submissions_dir="submissions/",
    report_dir="reports/"
)

evaluator.run()
```

The evaluator will:
- Compare cell values across sheets
- Highlight differences
- Report formula errors
- Generate detailed Excel comparison reports

## Command-Line Interface

### Basic Commands

```bash
# Evaluate notebooks
instantgrade evaluate solution.ipynb submissions/

# Specify report directory
instantgrade evaluate solution.ipynb submissions/ --report-dir custom_reports/

# Get help
instantgrade --help
instantgrade evaluate --help
```

### CLI Options

- `--report-dir`: Custom output directory for reports
- `--verbose`: Show detailed execution logs
- `--timeout`: Set execution timeout (seconds)

## What's Next?

Now that you've completed your first evaluation:

- 📖 Read the [Usage Guide](usage.md) for advanced features
- 💡 Explore [Examples](examples.md) for real-world scenarios
- 🔍 Check the [API Reference](api.md) for detailed documentation
- 🐛 Report issues on [GitHub](https://github.com/chandraveshchaudhari/instantgrade/issues)

## Common Use Cases

### Batch Grading

```python
# Grade multiple assignments
evaluator = Evaluator(
    solution_path="assignment1_solution.ipynb",
    submissions_dir="assignment1_submissions/",
    report_dir="assignment1_reports/"
)
evaluator.run()

evaluator = Evaluator(
    solution_path="assignment2_solution.ipynb",
    submissions_dir="assignment2_submissions/",
    report_dir="assignment2_reports/"
)
evaluator.run()
```

### Custom Comparison

```python
# More control over evaluation
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

# Run with custom settings
results = evaluator.run()

# Access results programmatically
for result in results:
    print(f"{result.filename}: {result.score}/100")
```

## Tips & Best Practices

1. **Organize Files**: Keep solutions and submissions in separate directories
2. **Clear Outputs**: Clear all outputs in solution notebooks before evaluation
3. **Test First**: Run your solution notebook to ensure it executes correctly
4. **Check Reports**: Always review reports for accuracy
5. **Version Control**: Keep solutions in version control (git)
