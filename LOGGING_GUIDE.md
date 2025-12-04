# 📊 Comprehensive Logging Guide for InstantGrade

## What I Added

I've added comprehensive logging throughout the evaluation pipeline so you can see exactly:
- ✅ Which student file is being evaluated
- ✅ The progress (X out of Y students)
- ✅ Which questions are being checked
- ✅ How many assertions passed/failed for each question
- ✅ Exactly where errors occur (slow code, infinite loops, etc.)

## Logging Output Example

When you run an evaluation, you'll see output like this:

```
======================================================================
🚀 STARTING EVALUATION PIPELINE
======================================================================
Solution file: ./sample_solutions.ipynb
Submissions folder: ./submissions

2024-12-04 10:15:32,123 - instantgrade.evaluator - INFO - 
📂 LOADING SUBMISSIONS...
2024-12-04 10:15:32,456 - instantgrade.evaluator - INFO - ✅ Loaded 3 submissions

2024-12-04 10:15:32,500 - instantgrade.evaluator - INFO - 
⚙️  EXECUTING SUBMISSIONS...
2024-12-04 10:15:32,501 - instantgrade.evaluator - INFO - Total submissions to evaluate: 3

2024-12-04 10:15:32,502 - instantgrade.evaluator - INFO - 
[1/3] 👤 Processing: student1.ipynb

2024-12-04 10:15:32,503 - instantgrade.execution.execution_service - INFO -   📓 Loading student notebook: student1.ipynb
2024-12-04 10:15:33,100 - instantgrade.execution.execution_service - INFO -     ✅ Notebook executed successfully
2024-12-04 10:15:33,105 - instantgrade.execution.execution_service - INFO -     📊 Namespace variables available: 12

2024-12-04 10:15:33,110 - instantgrade.execution.execution_service - INFO -     ❓ Total questions to evaluate: 3
2024-12-04 10:15:33,115 - instantgrade.execution.execution_service - INFO -     [1/3] 📝 Question: Question 1
2024-12-04 10:15:33,120 - instantgrade.execution.execution_service - INFO -         Description: Write a function to calculate sum
2024-12-04 10:15:33,125 - instantgrade.execution.execution_service - INFO -         Tests/Assertions: 5
2024-12-04 10:15:33,200 - instantgrade.execution.execution_service - INFO -         Result: ✅ 5 passed, ❌ 0 failed

2024-12-04 10:15:33,215 - instantgrade.execution.execution_service - INFO -     [2/3] 📝 Question: Question 2
2024-12-04 10:15:33,220 - instantgrade.execution.execution_service - INFO -         Description: Write a loop with conditional logic
2024-12-04 10:15:33,225 - instantgrade.execution.execution_service - INFO -         Tests/Assertions: 4
2024-12-04 10:15:35,500 - instantgrade.execution.execution_service - INFO -         Result: ✅ 2 passed, ❌ 2 failed

2024-12-04 10:15:35,510 - instantgrade.execution.execution_service - INFO -     [3/3] 📝 Question: Question 3
2024-12-04 10:15:35,515 - instantgrade.execution.execution_service - INFO -         Description: Calculate Fibonacci sequence
2024-12-04 10:15:35,520 - instantgrade.execution.execution_service - INFO -         Tests/Assertions: 3
2024-12-04 10:15:40,000 - instantgrade.execution.execution_service - ERROR -         ❌ ERROR evaluating question Question 3: TimeoutError: exceeded 60s (possible infinite loop)

2024-12-04 10:15:40,050 - instantgrade.execution.execution_service - INFO -     ✅ Evaluation complete for student1.ipynb
2024-12-04 10:15:40,100 - instantgrade.evaluator - INFO -   ✅ Successfully executed: student1.ipynb

2024-12-04 10:15:40,150 - instantgrade.evaluator - INFO - 
[2/3] 👤 Processing: student2.ipynb
...
```

## What Each Log Line Tells You

### Student Processing
```
[1/3] 👤 Processing: student1.ipynb
```
- Currently evaluating student 1 out of 3
- File name is `student1.ipynb`

### Notebook Execution
```
📓 Loading student notebook: student1.ipynb
✅ Notebook executed successfully
📊 Namespace variables available: 12
```
- Notebook loaded
- Code ran without errors (if ✅ shown)
- 12 variables are available for testing

### Question Evaluation
```
[1/3] 📝 Question: Question 1
Description: Write a function to calculate sum
Tests/Assertions: 5
Result: ✅ 5 passed, ❌ 0 failed
```
- Question 1 out of 3 being evaluated
- Question description for reference
- 5 test assertions
- All 5 tests passed ✅

### Error Detection
```
[2/3] 📝 Question: Question 2
...
Result: ✅ 2 passed, ❌ 2 failed
```
- Question 2 has 2 failures (student's code doesn't match expected behavior)

```
❌ ERROR evaluating question Question 3: TimeoutError: exceeded 60s
```
- Question 3 has an infinite loop or very slow code
- Times out after 60 seconds
- **This is your debugging clue!** The student's code is likely stuck in a while loop

## How to Debug When You See Errors

### Scenario 1: Timeout Error
```
❌ ERROR evaluating question Question 3: TimeoutError: exceeded 60s (possible infinite loop)
```

**What it means**: The student's code is taking too long
**Action**:
1. Check which question (Question 3)
2. Check which student (in the [X/Y] indicator above)
3. Open that student's notebook
4. Look at their code for question 3
5. Find the while loop or recursive function that might be infinite

### Scenario 2: Failed Assertions
```
Result: ✅ 2 passed, ❌ 2 failed
```

**What it means**: Some assertions passed, some failed
**Action**:
1. The student's logic is partially correct
2. There's a specific case or edge case they're missing
3. Check the description to understand what should be done

### Scenario 3: Execution Error
```
❌ ERROR executing notebook: NameError: name 'x' is not defined
```

**What it means**: The notebook has a Python error
**Action**:
1. Student's code has a bug
2. They forgot to define a variable
3. Or there's a typo in variable name

## Usage in Your Code

### Basic Usage (Auto-logging)
```python
from instantgrade import Evaluator

eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()

# Output will automatically show all the logging above!
```

### Control Logging Level

To see more detailed debug info:
```python
import logging

# Enable DEBUG level logging
logging.getLogger('instantgrade').setLevel(logging.DEBUG)

eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()
```

To see only errors and important info:
```python
import logging

# Show only WARNING and ERROR
logging.getLogger('instantgrade').setLevel(logging.WARNING)

eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()
```

### Redirect Logging to File

```python
import logging

# Log to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log'),
        logging.StreamHandler()
    ]
)

eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()
```

Then check `evaluation.log` for the full output.

## Features of the Logging System

### 1. Hierarchical Progress Display
- Shows overall progress: `[X/Total]`
- Indents logs to show nesting
- Easy to follow the evaluation flow

### 2. Error Highlighting
- ❌ Shows errors with context
- 🚀 Shows start of pipeline
- 🎉 Shows completion
- ✅ Shows successes

### 3. Contextual Information
- Student file name
- Question name and description
- Number of assertions/tests
- Results (passed/failed counts)
- Detailed error messages

### 4. Timing Information
- Timestamps on every line
- Easy to identify which question is slow
- Can pinpoint infinite loops or long-running code

## Files Modified

1. **`src/instantgrade/evaluator.py`**
   - Added logging import
   - Added progress logging to `run()` method
   - Added detailed logging to `execute_all()` method
   - Shows overall pipeline progress

2. **`src/instantgrade/execution/execution_service.py`**
   - Added logging import
   - Enhanced `execute_notebook()` with detailed logging
   - Shows per-question progress
   - Logs assertion results (passed/failed)
   - Captures and logs errors gracefully

## Next Steps

1. **Run an evaluation**: Follow the basic usage example above
2. **Watch the logs**: You'll see exactly what's happening
3. **Identify slow questions**: Timestamps will show which question takes longest
4. **Debug infinite loops**: Look for timeout errors and check that student's code
5. **Track progress**: Use `[X/Y]` indicators to know where you are

## Log Output Capture Options

### Option 1: Live Console (Default)
Just run the code and watch the output in VS Code terminal

### Option 2: Save to File
```python
import logging

logging.basicConfig(
    filename='eval_results.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()

# Open eval_results.log to see full log
```

### Option 3: Jupyter Notebook (Best for Notebooks)
```python
import logging

# For Jupyter notebooks, use the notebook cell to see live output
eval = Evaluator("./sample_solutions.ipynb", "./submissions")
result = eval.run()

# All logs appear in the notebook cell output
```

## Example Output in Jupyter

See the `basic_python_flow.ipynb` notebook for a live example of the logging output!

---

**Now when you run evaluations, you'll know exactly what's happening at every step!** 🎯
