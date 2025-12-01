# Changelog

All notable changes to InstantGrade will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation with Sphinx
- GitHub Pages deployment workflow
- API reference documentation
- Examples and use cases

## [0.1.0] - 2025-12-01

### Added
- Initial release of InstantGrade
- Core `Evaluator` class for automated grading
- Support for Jupyter notebooks (.ipynb)
- Support for Excel files (.xlsx, .xls)
- Cell-by-cell output comparison
- HTML report generation
- Command-line interface (CLI)
- Batch processing capabilities
- Configurable timeout settings
- Error handling and reporting
- Python API and CLI interface
- Multi-platform support (Windows, macOS, Linux)
- GitHub Actions CI/CD workflows
- PyPI publishing automation
- Comprehensive test suite

### Dependencies
- openpyxl >= 3.0.0
- pandas >= 1.0.0
- nbformat >= 5.0.0
- nbclient >= 0.5.0
- click >= 7.0

### Documentation
- README with installation and usage instructions
- PUBLISHING.md for release guidelines
- LICENSE.txt (MIT License)

### Infrastructure
- GitHub Actions workflows for testing
- GitHub Actions workflows for PyPI publishing
- Multi-Python version testing (3.8-3.12)
- Multi-OS testing (Ubuntu, Windows, macOS)

## Release Notes

### Version 0.1.0

InstantGrade 0.1.0 is the first public release! 🎉

This release provides a solid foundation for automated grading of Python notebooks and Excel files. Key features include:

- **Easy Installation**: Available on PyPI via `pip install instantgrade`
- **Jupyter Notebook Support**: Execute and compare notebook outputs
- **Excel Support**: Compare spreadsheet data across multiple sheets
- **Automated Reporting**: Generate detailed HTML reports
- **Flexible API**: Use via Python API or command-line interface
- **Well-Tested**: Comprehensive test coverage across platforms

### Upgrade Guide

This is the initial release, no upgrade steps needed.

### Known Issues

None at this time. Please report issues on [GitHub](https://github.com/chandraveshchaudhari/instantgrade/issues).

## Future Plans

### Planned for 0.2.0
- [ ] Support for additional file formats (CSV, JSON)
- [ ] Customizable report templates
- [ ] Parallel processing for faster batch grading
- [ ] Integration with popular LMS platforms
- [ ] Enhanced comparison algorithms
- [ ] Plugin system for custom comparisons

### Long-term Roadmap
- Web-based dashboard for viewing results
- API for integration with other tools
- Support for R notebooks
- Machine learning model comparison
- Automated feedback generation
- Student analytics and insights

## Contributing

We welcome contributions! See [CONTRIBUTING.md](contributing.md) for guidelines.

## Links

- **Homepage**: https://chandraveshchaudhari.github.io/instantgrade/
- **Repository**: https://github.com/chandraveshchaudhari/instantgrade
- **Issue Tracker**: https://github.com/chandraveshchaudhari/instantgrade/issues
- **PyPI**: https://pypi.org/project/instantgrade/
- **Documentation**: https://chandraveshchaudhari.github.io/instantgrade/

[Unreleased]: https://github.com/chandraveshchaudhari/instantgrade/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/chandraveshchaudhari/instantgrade/releases/tag/v0.1.0
