# Contributing to InstantGrade

Thank you for your interest in contributing to InstantGrade! This document provides guidelines and instructions for contributing.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features
- 🧪 Write tests
- 📖 Share examples

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/instantgrade.git
cd instantgrade
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Code Style

InstantGrade uses:
- **Black** for code formatting
- **Flake8** for linting
- **Type hints** for better code clarity

```bash
# Format code
black src/

# Check linting
flake8 src/

# Check types (if mypy is installed)
mypy src/
```

### Writing Code

1. **Follow PEP 8** style guidelines
2. **Add type hints** to function signatures
3. **Write docstrings** for all public functions and classes
4. **Keep functions focused** and single-purpose
5. **Use meaningful variable names**

Example:

```python
def compare_outputs(
    expected: str,
    actual: str,
    tolerance: float = 1e-5
) -> bool:
    """
    Compare two outputs with numerical tolerance.
    
    Args:
        expected: The expected output value
        actual: The actual output value
        tolerance: Numerical tolerance for comparison
        
    Returns:
        True if outputs match within tolerance, False otherwise
        
    Raises:
        ValueError: If inputs cannot be compared
    """
    # Implementation here
    pass
```

### Writing Tests

Tests are written using **pytest**.

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_evaluator.py

# Run with coverage
pytest --cov=instantgrade tests/
```

Example test:

```python
import pytest
from instantgrade import Evaluator

def test_evaluator_initialization():
    """Test that Evaluator initializes correctly."""
    evaluator = Evaluator(
        solution_path="tests/fixtures/solution.ipynb",
        submissions_dir="tests/fixtures/submissions/",
        report_dir="tests/output/"
    )
    assert evaluator is not None

def test_evaluator_run():
    """Test that evaluation runs successfully."""
    evaluator = Evaluator(
        solution_path="tests/fixtures/solution.ipynb",
        submissions_dir="tests/fixtures/submissions/",
        report_dir="tests/output/"
    )
    results = evaluator.run()
    assert len(results) > 0
```

### Running the Test Suite

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run tests with coverage report
pytest --cov=instantgrade --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Submitting Changes

### 1. Commit Your Changes

```bash
git add .
git commit -m "Add feature: description of your changes"
```

Write clear commit messages:
- Use present tense ("Add feature" not "Added feature")
- First line should be concise (50 chars or less)
- Add detailed description if needed

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Go to the [InstantGrade repository](https://github.com/chandraveshchaudhari/instantgrade)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - **Title**: Clear description of changes
   - **Description**: What, why, and how
   - **Related Issues**: Link any related issues
   - **Testing**: Describe how you tested changes

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No unnecessary dependencies added
- [ ] Type hints added where appropriate
- [ ] Docstrings added for public APIs

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Update to latest version** to see if bug is fixed
3. **Reproduce the bug** in a clean environment

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With these files '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.11]
- InstantGrade version: [e.g., 0.1.0]

**Additional context**
Add any other context about the problem.
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

## Documentation

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build docs
cd docs
make html

# View docs
open build/html/index.html
```

### Documentation Guidelines

1. **Use Markdown** for most documentation
2. **Follow existing structure** and formatting
3. **Include code examples** where helpful
4. **Keep it concise** but complete
5. **Update API docs** when changing code

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers warmly
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what's best for the community
- ❌ No harassment or discriminatory behavior
- ❌ No trolling or insulting comments

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: chandravesh.chaudhari@example.com (update with actual email)

## License

By contributing to InstantGrade, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for making InstantGrade better! 🎉
