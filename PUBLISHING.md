# Publishing to PyPI - Quick Start Guide

This project uses GitHub Actions to automatically publish to PyPI.

## Quick Steps (Recommended Method)

### First Time Setup (One-time)

1. **Configure PyPI Trusted Publishing:**
   - Go to https://pypi.org/ and log in
   - Navigate to Account Settings → Publishing
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name:** `instantgrade`
     - **Owner:** `chandraveshchaudhari`
     - **Repository name:** `evaluator`
     - **Workflow name:** `publish-on-tag.yml`
     - **Environment name:** `pypi` (optional)

### Publishing a New Version

1. **Update the version** in `setup.py` and `pyproject.toml`:
   ```python
   version='0.1.1',  # Increment this
   ```

2. **Commit your changes:**
   ```bash
   git add setup.py pyproject.toml
   git commit -m "Bump version to 0.1.1"
   ```

3. **Create and push a version tag:**
   ```bash
   git tag v0.1.1
   git push origin master
   git push origin v0.1.1
   ```

4. **GitHub Actions automatically:**
   - Builds the package
   - Publishes to PyPI
   - Users can now install with: `pip install instantgrade`

## Alternative: Manual Publishing

If you prefer to publish manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires PyPI credentials)
python -m twine upload dist/*
```

## Checking Your Package

After publishing, verify on:
- PyPI: https://pypi.org/project/instantgrade/
- Install: `pip install instantgrade`

## Version Numbering Guide

Use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- `v0.1.0` → `v0.1.1` - Bug fixes
- `v0.1.0` → `v0.2.0` - New features
- `v0.1.0` → `v1.0.0` - Breaking changes / First stable release

## Need Help?

See detailed instructions in `.github/workflows/README.md`
