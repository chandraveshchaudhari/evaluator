# InstantGrade Documentation

This directory contains the source files for InstantGrade's documentation, built using Sphinx.

## 📚 Documentation Site

The documentation is automatically built and deployed to:
**https://chandraveshchaudhari.github.io/instantgrade/**

## 🏗️ Building Documentation Locally

### Prerequisites

Install documentation dependencies:

```bash
# From the project root
pip install -e ".[docs]"
```

### Build HTML Documentation

```bash
cd docs
make html
```

The built documentation will be in `build/html/`. Open `build/html/index.html` in your browser.

### Clean Build Files

```bash
cd docs
make clean
```

## 📁 Directory Structure

```
docs/
├── Makefile              # Unix build commands
├── make.bat              # Windows build commands
├── requirements.txt      # Documentation dependencies
├── source/               # Documentation source files
│   ├── conf.py          # Sphinx configuration
│   ├── index.md         # Documentation homepage
│   ├── installation.md  # Installation guide
│   ├── quickstart.md    # Quick start guide
│   ├── usage.md         # Usage guide
│   ├── examples.md      # Examples and use cases
│   ├── api.md           # API reference
│   ├── contributing.md  # Contribution guidelines
│   ├── changelog.md     # Version history
│   ├── _static/         # Static files (CSS, images, etc.)
│   └── _templates/      # Custom Sphinx templates
└── build/               # Generated documentation (ignored by git)
```

## 🛠️ Technology Stack

- **[Sphinx](https://www.sphinx-doc.org/)** - Documentation generator
- **[MyST Parser](https://myst-parser.readthedocs.io/)** - Markdown support for Sphinx
- **[Furo](https://pradyunsg.me/furo/)** - Modern, clean documentation theme
- **[Sphinx AutoDoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)** - Automatic API documentation from docstrings
- **[Napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)** - Google/NumPy docstring support
- **[Jupyter-Sphinx](https://jupyter-sphinx.readthedocs.io/)** - Jupyter notebook integration
- **[Sphinx Autodoc Typehints](https://github.com/tox-dev/sphinx-autodoc-typehints)** - Type hint support
- **[Sphinx CopyButton](https://sphinx-copybutton.readthedocs.io/)** - Copy code buttons
- **[Sphinx Design](https://sphinx-design.readthedocs.io/)** - UI components (cards, grids, etc.)

## 📝 Writing Documentation

### Markdown Files

Documentation is written in Markdown with MyST extensions:

```markdown
# Page Title

Regular markdown content...

## Code Examples

\`\`\`python
from instantgrade import Evaluator

evaluator = Evaluator(
    solution_path="solution.ipynb",
    submissions_dir="submissions/",
    report_dir="reports/"
)
\`\`\`

## Admonitions

:::{note}
This is a note
:::

:::{warning}
This is a warning
:::
```

### API Documentation

API docs are automatically generated from Python docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Short description of the function.
    
    Longer description with more details about what the function does,
    how it works, and when to use it.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter
        
    Returns:
        Description of the return value
        
    Raises:
        ValueError: When something goes wrong
        
    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

## 🚀 Continuous Deployment

Documentation is automatically built and deployed via GitHub Actions:

- **Trigger**: Commits to `master` branch that modify `docs/` or `src/`
- **Workflow**: `.github/workflows/docs.yml`
- **Deployment**: GitHub Pages
- **URL**: https://chandraveshchaudhari.github.io/instantgrade/

## 🔧 Customization

### Theme Configuration

Edit `source/conf.py` to customize the Furo theme:

```python
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#2563eb",
    },
    # ... more options
}
```

### Adding New Pages

1. Create a new `.md` file in `source/`
2. Add it to the `toctree` in `source/index.md`:

```markdown
\`\`\`{toctree}
:maxdepth: 2

installation
quickstart
your-new-page
\`\`\`
```

### Custom Static Files

Add images, CSS, or JavaScript to `source/_static/` and reference them:

```markdown
![My Image](_static/my-image.png)
```

## 📚 Useful Make Commands

```bash
# Build HTML
make html

# Build and open
make html && open build/html/index.html

# Clean build
make clean

# See all targets
make help
```

## 🐛 Troubleshooting

### Build Errors

If you encounter build errors:

```bash
# Clean and rebuild
make clean
make html
```

### Missing Dependencies

```bash
# Reinstall documentation dependencies
pip install -e ".[docs]" --force-reinstall
```

### Import Errors

Make sure the package is installed in development mode:

```bash
# From project root
pip install -e .
```

## 📖 Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser Guide](https://myst-parser.readthedocs.io/)
- [Furo Theme Docs](https://pradyunsg.me/furo/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)

## 💬 Questions?

If you have questions about the documentation:

- Open an issue on [GitHub](https://github.com/chandraveshchaudhari/instantgrade/issues)
- Check the [Contributing Guide](source/contributing.md)
- Join [Discussions](https://github.com/chandraveshchaudhari/instantgrade/discussions)
