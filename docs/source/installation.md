# Installation

## Requirements

InstantGrade requires Python 3.8 or higher. It supports:

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## Install from PyPI

The easiest way to install InstantGrade is via pip:

```bash
pip install instantgrade
```

This will install InstantGrade along with all required dependencies.

## Install from Source

To install the latest development version from GitHub:

```bash
# Clone the repository
git clone https://github.com/chandraveshchaudhari/instantgrade.git
cd instantgrade

# Install in development mode
pip install -e .
```

## Optional Dependencies

### Excel Support (Windows)

For enhanced Excel functionality on Windows, you can install xlwings:

```bash
pip install instantgrade[excel]
```

### Development Tools

If you want to contribute or run tests:

```bash
pip install instantgrade[dev]
```

This includes:
- pytest (testing)
- black (code formatting)
- flake8 (linting)
- twine (package management)

### Documentation Building

To build documentation locally:

```bash
pip install instantgrade[docs]
```

### All Optional Dependencies

To install everything:

```bash
pip install instantgrade[all]
```

## Verify Installation

After installation, verify that InstantGrade is installed correctly:

```python
from instantgrade import Evaluator
print("InstantGrade installed successfully!")
```

Or using the command-line interface:

```bash
instantgrade --version
```

## Dependencies

InstantGrade automatically installs these required packages:

- **openpyxl** (≥3.0.0) - Excel file handling
- **pandas** (≥1.0.0) - Data manipulation
- **nbformat** (≥5.0.0) - Jupyter notebook format
- **nbclient** (≥0.5.0) - Notebook execution
- **click** (≥7.0) - Command-line interface

## Platform Support

InstantGrade is tested on:

- **Linux** (Ubuntu, Debian, etc.)
- **macOS** (10.15+)
- **Windows** (10, 11)

## Troubleshooting

### Import Error

If you encounter import errors:

```bash
# Reinstall the package
pip uninstall instantgrade
pip install --no-cache-dir instantgrade
```

### Permission Errors

On Linux/macOS, you might need to use `--user`:

```bash
pip install --user instantgrade
```

Or use a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install InstantGrade
pip install instantgrade
```

### Version Conflicts

If you have dependency conflicts:

```bash
# Create a fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows
pip install instantgrade
```

## Next Steps

- Continue to the [Quick Start Guide](quickstart.md)
- Read the [Usage Guide](usage.md)
- Explore [Examples](examples.md)
