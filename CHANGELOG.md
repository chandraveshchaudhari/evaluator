# Changelog

All notable changes to the InstantGrade project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features will be listed here before release

## [0.1.0] - 2025-12-01

### Added
- Initial release of the InstantGrade framework
- Python Jupyter notebook evaluation support
- Excel file evaluation support (.xlsx, .xls)
- Automated evaluation pipeline (ingestion → execution → comparison → reporting)
- HTML report generation
- AST-based code comparison for Python notebooks
- Command-line interface (CLI)
- Batch processing for multiple submissions
- Configurable evaluation criteria via JSON
- Comprehensive documentation and examples
- GitHub Actions for automated testing and PyPI publishing
- Support for Python 3.8 through 3.12

### Features
- **Ingestion Service**: Load solution and submission files
- **Execution Service**: Execute notebooks and compare results
- **Reporting Service**: Generate detailed HTML reports
- **AST Analysis**: Deep code structure comparison
- **Comparison Engine**: Value and function checking

### Documentation
- README with comprehensive usage examples
- Publishing guide (PUBLISHING.md)
- GitHub Actions workflow documentation
- Example notebooks for different evaluation scenarios

## How to Update This Changelog

When releasing a new version:

1. Move items from "Unreleased" to a new version section
2. Add the version number and release date
3. Organize changes under these categories:
   - **Added** for new features
   - **Changed** for changes in existing functionality
   - **Deprecated** for soon-to-be removed features
   - **Removed** for now removed features
   - **Fixed** for any bug fixes
   - **Security** for vulnerability fixes

Example:
```markdown
## [0.2.0] - 2025-12-15

### Added
- Support for R Markdown files
- PDF report export option

### Fixed
- Fixed issue with Excel formula evaluation
- Corrected AST comparison for nested functions

### Changed
- Improved HTML report styling
- Updated dependencies to latest versions
```

[Unreleased]: https://github.com/chandraveshchaudhari/instantgrade/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/chandraveshchaudhari/instantgrade/releases/tag/v0.1.0
