# Versioning and Release Process

This document explains how automatic version bumping and releases work for the `instantgrade` package.

## Overview

The project uses **semantic versioning** (MAJOR.MINOR.PATCH) and automates version bumping when code is pushed to the `master` branch.

## Current Version

- **Format**: `MAJOR.MINOR.PATCH` (e.g., `0.1.1`)
- **Current**: Check `pyproject.toml` or `setup.py`

## Automatic Version Bumping

### How It Works

1. **Trigger**: When you push code to `master` branch (specifically changes to `src/`, `setup.py`, or `pyproject.toml`)
2. **Auto-Increment**: The GitHub Action automatically increments the PATCH version (e.g., `0.1.1` → `0.1.2`)
3. **Tag Creation**: Creates a git tag (e.g., `v0.1.2`)
4. **Release**: Creates a GitHub Release
5. **PyPI Publishing**: The release trigger automatically publishes to PyPI

### Workflow Steps

```
Push to master → Version Bump → Create Tag → GitHub Release → Publish to PyPI
```

### Skip Version Bump

If you want to push code WITHOUT bumping the version, include one of these in your commit message:

```bash
git commit -m "docs: update README [skip version]"
git commit -m "chore: minor fix [skip ci]"
```

## Manual Version Updates

### Patch Version (Bug Fixes)
For small bug fixes and minor adjustments:
```bash
# Current: 0.1.1 → New: 0.1.2
# This happens automatically on push to master
```

### Minor Version (New Features)
For new features that don't break backward compatibility:
```bash
# Current: 0.1.x → New: 0.2.0
# Update manually in both files:
```

1. Edit `pyproject.toml`:
```toml
version = "0.2.0"
```

2. Edit `setup.py`:
```python
version="0.2.0",
```

3. Commit and push:
```bash
git add pyproject.toml setup.py
git commit -m "chore: bump version to 0.2.0 for new features"
git push origin master
```

### Major Version (Breaking Changes)
For breaking changes that aren't backward compatible:
```bash
# Current: 0.x.x → New: 1.0.0
# Follow same steps as minor version
```

## Automatic Formatting

The project automatically formats code with `black` to prevent CI failures.

### Auto-Format Workflow

1. **On Push**: When Python files are pushed, Black automatically formats them
2. **Auto-Commit**: Formatted code is committed back with message: `"style: auto-format code with black [skip ci]"`
3. **Prevents Failures**: Eliminates manual formatting issues

### Local Formatting

Before pushing, you can format locally:

```bash
# Format all Python files
black src/

# Check formatting without changes
black --check src/
```

## GitHub Actions Workflows

### 1. `version-bump.yml`
- **Trigger**: Push to master (src/*, setup.py, pyproject.toml)
- **Action**: Auto-increment patch version, create tag and release
- **Skip**: Include `[skip version]` or `[skip ci]` in commit message

### 2. `auto-format.yml`
- **Trigger**: Push/PR with Python file changes
- **Action**: Auto-format code with Black, commit changes
- **Skip**: Include `[skip ci]` in commit message

### 3. `test.yml`
- **Trigger**: Push/PR to master
- **Action**: Run tests, lint checks (with auto-formatting)

### 4. `publish.yml`
- **Trigger**: Release published or version tag pushed
- **Action**: Build and publish package to PyPI

## PyPI Publishing

### Prerequisites

1. **PyPI Account**: Project must be registered on PyPI
2. **Trusted Publishing**: Configure in PyPI settings:
   - Go to: https://pypi.org/manage/account/publishing/
   - Add publisher: `chandraveshchaudhari/instantgrade`
   - Workflow: `publish.yml`
   - Environment: (leave blank)

### Publishing Process

Publishing is **fully automated**:

1. Push code to master → Version bumps → Tag created
2. Tag triggers `publish.yml` workflow
3. Package builds and publishes to PyPI
4. Verification runs to ensure successful installation

### Manual Publishing (if needed)

```bash
# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Best Practices

### 1. Commit Messages
Use conventional commit format:
```bash
git commit -m "feat: add new evaluation feature"
git commit -m "fix: resolve comparison bug"
git commit -m "docs: update installation guide"
git commit -m "style: format code [skip ci]"
git commit -m "chore: update dependencies [skip version]"
```

### 2. Version Strategy
- **Patch (0.1.x)**: Bug fixes, small adjustments → **Automatic**
- **Minor (0.x.0)**: New features, additions → **Manual**
- **Major (x.0.0)**: Breaking changes → **Manual**

### 3. Before Pushing
```bash
# Format code
black src/

# Run tests locally (if available)
pytest

# Check what will be committed
git status
git diff
```

### 4. After Release
- Check GitHub Releases: https://github.com/chandraveshchaudhari/instantgrade/releases
- Verify PyPI: https://pypi.org/project/instantgrade/
- Test installation: `pip install --upgrade instantgrade`

## Troubleshooting

### Version Already Exists on PyPI
- The workflow automatically bumps the version if a tag already exists
- If manual override needed, update version in both `pyproject.toml` and `setup.py`

### Formatting Failure
- Run `black src/` locally to fix formatting
- Or let the auto-format workflow handle it automatically

### Publishing Failure
- Check PyPI Trusted Publishing is configured correctly
- Verify package builds locally: `python -m build`
- Check workflow logs in GitHub Actions

### Tag Already Exists
- Delete tag locally and remotely:
```bash
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1
```
- Push again to trigger new version bump

## Examples

### Example 1: Minor Bug Fix
```bash
# Fix a bug in comparison_service.py
git add src/instantgrade/comparison/comparison_service.py
git commit -m "fix: resolve timeout in comparison service"
git push origin master

# Result: Version 0.1.1 → 0.1.2 (automatic)
```

### Example 2: New Feature
```bash
# Add new feature
# First, manually update version to 0.2.0 in both files
git add pyproject.toml setup.py src/
git commit -m "feat: add Excel comparison feature"
git push origin master

# Result: Version 0.2.0 tagged and released
```

### Example 3: Documentation Update
```bash
# Update docs only
git add docs/
git commit -m "docs: improve API documentation [skip version]"
git push origin master

# Result: No version bump, no release
```

## References

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
