# Examples

This page provides real-world examples and use cases for InstantGrade.

## Example 1: Basic Data Analysis Assignment

### Scenario
Students need to analyze a dataset and produce specific outputs.

### Solution Notebook

```python
# Cell 1: Import libraries
import pandas as pd
import numpy as np

# Cell 2: Load data
df = pd.read_csv('data.csv')

# Cell 3: Calculate statistics
mean_value = df['score'].mean()
median_value = df['score'].median()
print(f"Mean: {mean_value:.2f}")
print(f"Median: {median_value:.2f}")

# Cell 4: Create visualization
import matplotlib.pyplot as plt
plt.hist(df['score'], bins=10)
plt.title('Score Distribution')
plt.show()
```

### Grading Script

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="data_analysis_solution.ipynb",
    submissions_dir="submissions/data_analysis/",
    report_dir="reports/data_analysis/"
)

results = evaluator.run()

# Print summary
for result in results:
    print(f"{result.filename}: {result.score}/100")
```

## Example 2: Excel Spreadsheet Evaluation

### Scenario
Students complete financial calculations in Excel.

### Directory Structure

```
financial_assignment/
├── solution.xlsx
├── submissions/
│   ├── student1.xlsx
│   ├── student2.xlsx
│   └── student3.xlsx
└── reports/
```

### Grading Code

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="financial_assignment/solution.xlsx",
    submissions_dir="financial_assignment/submissions/",
    report_dir="financial_assignment/reports/"
)

evaluator.run()
print("Excel grading complete!")
```

## Example 3: Multi-Assignment Grading

### Scenario
Grade multiple assignments in one script.

```python
from instantgrade import Evaluator

assignments = [
    ("assignment1", "Data Cleaning"),
    ("assignment2", "Statistical Analysis"),
    ("assignment3", "Machine Learning"),
]

for assignment_id, assignment_name in assignments:
    print(f"\nGrading {assignment_name}...")
    
    evaluator = Evaluator(
        solution_path=f"solutions/{assignment_id}.ipynb",
        submissions_dir=f"submissions/{assignment_id}/",
        report_dir=f"reports/{assignment_id}/"
    )
    
    results = evaluator.run()
    
    # Calculate statistics
    scores = [r.score for r in results]
    print(f"  Submissions: {len(scores)}")
    print(f"  Average: {sum(scores)/len(scores):.1f}")
    print(f"  Min: {min(scores)}, Max: {max(scores)}")
```

## Example 4: Custom Report Processing

### Scenario
Extract scores and generate a CSV summary.

```python
import csv
from instantgrade import Evaluator

# Run evaluation
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

results = evaluator.run()

# Export to CSV
with open('grades.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Student', 'Score', 'Status', 'Report'])
    
    for result in results:
        writer.writerow([
            result.filename,
            result.score,
            result.status,
            result.report_path
        ])

print("Grades exported to grades.csv")
```

## Example 5: Automated Feedback Emails

### Scenario
Send automated emails with report attachments.

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from instantgrade import Evaluator

# Run evaluation
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

results = evaluator.run()

# Send emails (example - configure your SMTP settings)
def send_email(student_email, report_path, score):
    msg = MIMEMultipart()
    msg['From'] = 'instructor@university.edu'
    msg['To'] = student_email
    msg['Subject'] = 'Your Assignment Grade'
    
    body = f"""
    Dear Student,
    
    Your assignment has been graded.
    Score: {score}/100
    
    Please see the attached report for details.
    
    Best regards,
    Instructor
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach report
    with open(report_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename=report.html')
        msg.attach(part)
    
    # Send (configure your SMTP server)
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login('your_email', 'your_password')
    # server.send_message(msg)
    # server.quit()

# Map results to students
student_emails = {
    'student1.ipynb': 'student1@university.edu',
    'student2.ipynb': 'student2@university.edu',
}

for result in results:
    if result.filename in student_emails:
        send_email(
            student_emails[result.filename],
            result.report_path,
            result.score
        )
```

## Example 6: Integration with Learning Management System

### Scenario
Upload grades to Canvas/Moodle LMS.

```python
from instantgrade import Evaluator
import requests

# Run evaluation
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

results = evaluator.run()

# Upload to LMS (example - adjust for your LMS API)
LMS_API_URL = 'https://lms.university.edu/api/v1'
API_TOKEN = 'your_api_token'
ASSIGNMENT_ID = '12345'

for result in results:
    # Extract student ID from filename
    student_id = result.filename.split('_')[0]
    
    # Post grade
    response = requests.post(
        f'{LMS_API_URL}/assignments/{ASSIGNMENT_ID}/submissions/{student_id}',
        headers={'Authorization': f'Bearer {API_TOKEN}'},
        json={
            'submission': {
                'posted_grade': result.score
            }
        }
    )
    
    if response.status_code == 200:
        print(f"Uploaded grade for {student_id}")
    else:
        print(f"Error uploading grade for {student_id}")
```

## Example 7: Continuous Integration

### Scenario
Automatically grade submissions pushed to GitHub.

### GitHub Actions Workflow

```yaml
# .github/workflows/grade.yml
name: Auto Grade Submissions

on:
  push:
    branches: [ submissions ]

jobs:
  grade:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install instantgrade
      
      - name: Run grading
        run: |
          python grade_submissions.py
      
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: grading-reports
          path: reports/
```

### Grading Script (`grade_submissions.py`)

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

evaluator.run()
```

## Example 8: Custom Comparison Tolerance

### Scenario
Allow small numerical differences in student outputs.

```python
from instantgrade import Evaluator
from instantgrade.comparison import ComparisonService
import numpy as np

class TolerantComparison(ComparisonService):
    def compare_outputs(self, expected, actual, tolerance=1e-5):
        """Compare with numerical tolerance."""
        try:
            expected_num = float(expected)
            actual_num = float(actual)
            return np.isclose(expected_num, actual_num, rtol=tolerance)
        except (ValueError, TypeError):
            return expected == actual

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/",
    comparison_service=TolerantComparison()
)

evaluator.run()
```

## Example 9: Batch Processing with Progress

### Scenario
Grade many submissions with progress tracking.

```python
from instantgrade import Evaluator
from tqdm import tqdm
import os

submissions_dir = "submissions/"
submission_files = [
    f for f in os.listdir(submissions_dir)
    if f.endswith('.ipynb')
]

results = []

for submission in tqdm(submission_files, desc="Grading"):
    evaluator = Evaluator(
        solution_path="solution.ipynb",
        submissions_dir=submissions_dir,
        report_dir="reports/"
    )
    
    result = evaluator.run()
    results.extend(result)

# Summary statistics
scores = [r.score for r in results]
print(f"\nGrading Complete!")
print(f"Total submissions: {len(scores)}")
print(f"Average score: {sum(scores)/len(scores):.2f}")
print(f"Highest score: {max(scores)}")
print(f"Lowest score: {min(scores)}")
```

## Example 10: Machine Learning Assignment

### Scenario
Grade a machine learning model training notebook.

### Solution Notebook

```python
# Cell 1: Imports
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Cell 2: Load and split data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Cell 3: Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Cell 4: Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
```

### Grading

```python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="ml_solution.ipynb",
    submissions_dir="ml_submissions/",
    report_dir="ml_reports/",
    timeout=600  # ML training may take longer
)

results = evaluator.run()

# Check if students achieved minimum accuracy
for result in results:
    if result.score >= 90:  # At least 90% match
        print(f"✓ {result.filename}: PASS")
    else:
        print(f"✗ {result.filename}: NEEDS REVIEW")
```

## Tips for Each Example

1. **Data Analysis**: Ensure data files are accessible to all notebooks
2. **Excel**: Check that formulas are preserved and calculated correctly
3. **Multi-Assignment**: Use consistent naming conventions
4. **Custom Reports**: Parse HTML reports for structured data extraction
5. **Email Automation**: Test email settings before bulk sending
6. **LMS Integration**: Handle API rate limits and authentication
7. **CI/CD**: Store sensitive credentials in GitHub Secrets
8. **Tolerance**: Define appropriate tolerance levels for your use case
9. **Batch Processing**: Consider memory usage for large batches
10. **ML Assignments**: Account for stochastic behavior in models

## Next Steps

- Check the [API Reference](api.md) for detailed function documentation
- Visit [GitHub](https://github.com/chandraveshchaudhari/instantgrade) for more examples
- Join discussions and share your use cases
