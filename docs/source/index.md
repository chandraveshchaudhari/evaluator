# InstantGrade Documentation

Welcome to **InstantGrade**, an automated evaluation framework for grading Python Jupyter notebooks and Excel spreadsheets. InstantGrade simplifies the assessment process by comparing student submissions against reference solutions and generating comprehensive HTML reports.

```{toctree}
:maxdepth: 2
:caption: Contents

installation
quickstart
usage
examples
api
contributing
changelog
```

## What is InstantGrade?

InstantGrade is a powerful tool designed for educators and course administrators who need to:

- ✅ **Automate grading** of Jupyter notebooks and Excel files
- 📊 **Compare outputs** between student submissions and reference solutions
- 📝 **Generate reports** showing detailed comparisons and scores
- ⚡ **Save time** by eliminating manual comparison work
- 🎯 **Ensure consistency** in grading across multiple submissions

## Key Features

### 🐍 Python Notebook Support
- Execute and compare Jupyter notebooks
- Cell-by-cell output comparison
- Variable state tracking
- Error handling and reporting

### 📊 Excel File Support
- Compare spreadsheet data
- Support for multiple sheets
- Formula validation
- Cell-by-cell difference highlighting

### 📈 Comprehensive Reporting
- HTML reports with detailed comparisons
- Visual diff highlighting
- Score calculations
- Execution logs and error tracking

### 🔧 Flexible Configuration
- Customizable evaluation criteria
- Support for multiple file formats
- Batch processing capabilities
- CLI and Python API

## Quick Example

```python
from instantgrade import Evaluator

# Initialize the evaluator
evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)

# Run evaluation
evaluator.run()

# Results are saved in reports/ directory
```

## Use Cases

### Education
- Grade programming assignments
- Evaluate data analysis projects
- Assess Excel spreadsheet exercises
- Provide detailed feedback to students

### Training
- Evaluate workshop exercises
- Check coding bootcamp submissions
- Assess certification exams

### Research
- Validate experimental results
- Compare data analysis outputs
- Reproduce computational research

## Get Started

::::{grid} 1 2 2 3
:gutter: 4

:::{grid-item-card} 📦 Installation
:link: installation
:link-type: doc

Get InstantGrade installed and ready to use in minutes.
:::

:::{grid-item-card} 🚀 Quick Start
:link: quickstart
:link-type: doc

Learn the basics with a simple example.
:::

:::{grid-item-card} 📖 Usage Guide
:link: usage
:link-type: doc

Explore all features and configuration options.
:::

:::{grid-item-card} 💡 Examples
:link: examples
:link-type: doc

See real-world examples and use cases.
:::

:::{grid-item-card} 🔍 API Reference
:link: api
:link-type: doc

Complete API documentation for developers.
:::

:::{grid-item-card} 🤝 Contributing
:link: contributing
:link-type: doc

Help improve InstantGrade.
:::

::::

## Community & Support

- **GitHub**: [chandraveshchaudhari/instantgrade](https://github.com/chandraveshchaudhari/instantgrade)
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/chandraveshchaudhari/instantgrade/issues)
- **PyPI**: [pypi.org/project/instantgrade](https://pypi.org/project/instantgrade/)

## License

InstantGrade is released under the MIT License. See the [LICENSE](https://github.com/chandraveshchaudhari/instantgrade/blob/master/LICENSE.txt) file for details.
