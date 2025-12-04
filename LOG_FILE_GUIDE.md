# 📝 Using Evaluator with Log File - Complete Guide

## Quick Start (Recommended!)

Just add `log_file` parameter to your Evaluator:

```python
from instantgrade import Evaluator

eval = Evaluator(
    "./sample_solutions.ipynb", 
    "./submissions",
    log_file="./report/evaluation_log.txt"  # ← Add this!
)
result = eval.run()
```

That's it! Logs will be saved to `./report/evaluation_log.txt` automatically!

## What Gets Logged

Everything you see in the console also gets saved to the file:

```
======================================================================
🚀 STARTING EVALUATION PIPELINE
======================================================================
Solution file: ./sample_solutions.ipynb
Submissions folder: ./submissions
Total submissions to evaluate: 3

[1/3] 👤 Processing: student1.ipynb
  📓 Loading student notebook: student1.ipynb
    ✅ Notebook executed successfully
    📊 Namespace variables available: 12
    ❓ Total questions to evaluate: 3
    [1/3] 📝 Question: Q1
        Description: Write a function to calculate sum
        Tests/Assertions: 5
        Result: ✅ 5 passed, ❌ 0 failed
    [2/3] 📝 Question: Q2
        Description: Write a loop
        Tests/Assertions: 4
        Result: ✅ 2 passed, ❌ 2 failed
    [3/3] 📝 Question: Q3
        Description: Fibonacci sequence
        Tests/Assertions: 3
        ❌ ERROR evaluating question Q3: TimeoutError: exceeded 60s
    ✅ Evaluation complete for student1.ipynb
  ✅ Successfully executed: student1.ipynb

[2/3] 👤 Processing: student2.ipynb
...
```

## Usage Examples

### Example 1: Basic Usage with Logs (Recommended)
```python
from instantgrade import Evaluator

eval = Evaluator(
    solution_file_path="./sample_solutions.ipynb",
    submission_folder_path="./submissions",
    log_file="./evaluation_log.txt"
)
result = eval.run()

# Now open evaluation_log.txt to see the full log!
```

### Example 2: Logs in Report Folder
```python
eval = Evaluator(
    solution_file_path="./sample_solutions.ipynb",
    submission_folder_path="./submissions",
    log_file="./report/evaluation_log.txt"  # Inside report folder
)
result = eval.run()
```

### Example 3: No Logs (Console Only)
```python
eval = Evaluator(
    solution_file_path="./sample_solutions.ipynb",
    submission_folder_path="./submissions"
    # log_file not provided - console output only
)
result = eval.run()
```

### Example 4: With Timestamp in Filename
```python
from instantgrade.utils.path_utils import filename_safe_timestamp_format

timestamp = filename_safe_timestamp_format()
log_file = f"./report/evaluation_log_{timestamp}.txt"

eval = Evaluator(
    solution_file_path="./sample_solutions.ipynb",
    submission_folder_path="./submissions",
    log_file=log_file
)
result = eval.run()

# Log file: ./report/evaluation_log_20251204_101530.txt
```

## Advantages Over Manual Setup

### Before (Manual):
```python
import logging

logging.basicConfig(
    filename='evaluation_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()

# ❌ Doesn't always work as expected
# ❌ Missing logs from some modules
# ❌ Complex to configure
```

### After (Simple):
```python
eval = Evaluator(
    "./sample_solutions.ipynb", 
    "./submissions",
    log_file="./report/evaluation_log.txt"
)
result = eval.run()

# ✅ Always works!
# ✅ Captures all logs
# ✅ Simple one-liner
```

## Features

### ✅ Automatic Parent Directory Creation
```python
# This works even if ./report/ doesn't exist yet!
eval = Evaluator(
    "./sample_solutions.ipynb",
    "./submissions",
    log_file="./report/logs/evaluation_log.txt"
)
result = eval.run()
# Creates ./report/logs/ automatically
```

### ✅ Dual Output (Console + File)
When you provide `log_file`, logs appear in:
1. **Console** - You see progress in real-time
2. **File** - All logs saved for later review

### ✅ Complete Logging
All logs from:
- Main Evaluator class
- ExecutionService class
- ComparisonService (if it logs)
- Any other component

### ✅ Proper File Handling
- File is properly flushed and closed
- UTF-8 encoding for special characters
- File created fresh each run (old logs replaced)

## Use Cases

### Case 1: Debugging Slow Student Notebooks
```python
eval = Evaluator(
    "./sample_solutions.ipynb",
    "./submissions",
    log_file="./debug_log.txt"
)
result = eval.run()

# Open debug_log.txt
# Find TimeoutError: [3/25] 👤 Processing: Ankita_file.ipynb
# Look at question [2/3] 📝 Question: Q2
# Now you know which file and question is slow!
```

### Case 2: Running Batch Evaluations
```python
# Run multiple evaluations and save logs
for assignment_num in range(1, 6):
    eval = Evaluator(
        f"./assignment{assignment_num}/solution.ipynb",
        f"./assignment{assignment_num}/submissions",
        log_file=f"./logs/assignment{assignment_num}_log.txt"
    )
    result = eval.run()
    print(f"Assignment {assignment_num} completed!")
```

### Case 3: Archive Logs with Timestamps
```python
from pathlib import Path
from instantgrade.utils.path_utils import filename_safe_timestamp_format

timestamp = filename_safe_timestamp_format()
log_dir = Path("./logs") / timestamp
log_dir.mkdir(parents=True, exist_ok=True)

eval = Evaluator(
    "./sample_solutions.ipynb",
    "./submissions",
    log_file=log_dir / "evaluation_log.txt"
)
result = eval.run()

# Logs saved in: ./logs/20251204_101530/evaluation_log.txt
```

## What's in the Log File

### Timestamps
Every line has a timestamp so you can see how long things take:
```
2024-12-04 10:15:32,123 - instantgrade.evaluator - INFO - [1/3] 👤 Processing: student1.ipynb
2024-12-04 10:15:33,456 - instantgrade.execution.execution_service - INFO -   ✅ Notebook executed successfully
2024-12-04 10:15:35,789 - instantgrade.execution.execution_service - INFO -     Result: ✅ 5 passed, ❌ 0 failed
```

### Progress Indicators
- `[X/Y]` shows which file out of total
- `✅` for successes
- `❌` for failures
- `⚠️` for warnings

### Full Details
- Student file names
- Question names and descriptions
- Number of assertions per question
- Pass/fail counts per question
- Error messages with full context

## Finding Issues in Logs

### Find Timeouts
```bash
grep "TimeoutError" evaluation_log.txt
# Shows all questions that timed out
```

### Find Failed Students
```bash
grep "ERROR executing" evaluation_log.txt
# Shows students with notebook execution errors
```

### Find Slow Questions
Look at timestamps and calculate duration between start and end of questions.

### Find Question Failures
```bash
grep "❌" evaluation_log.txt
# Shows all failed assertions
```

## Example Notebook Usage

See `basic_python_flow.ipynb` cell 4 for a working example:

```python
eval = Evaluator(
    "./sample_solutions.ipynb", 
    "./submissions",
    log_file="./report/evaluation_log.txt"
)
result = eval.run()
```

Then check `./report/evaluation_log.txt` for the full log!

## Parameters Reference

```python
Evaluator(
    solution_file_path="./sample_solutions.ipynb",      # ← Required: solution file
    submission_folder_path="./submissions",              # ← Required: submissions folder
    config_json=None,                                    # ← Optional: config file
    log_file="./report/evaluation_log.txt"              # ← Optional: log file path (NEW!)
)
```

### log_file Parameter
- **Type**: `str`, `Path`, or `None`
- **Default**: `None` (no file logging)
- **If provided**: Logs saved to this file
- **Creates**: Parent directories automatically
- **Mode**: Overwrites file each run (fresh logs)

---

**That's it! Simple logging with one parameter!** 🎉
