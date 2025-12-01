# GitHub Actions Workflows for PyPI Publishing

This directory contains GitHub Actions workflows for automatically publishing the `instantgrade` package to PyPI.

## Available Workflows

### 1. `publish-on-tag.yml` (RECOMMENDED)
**Trigger:** When you push a version tag (e.g., `v0.1.0`, `v1.2.3`)

**Best for:** Controlled releases with semantic versioning

**Usage:**
```bash
# Update version in setup.py and pyproject.toml first
git add setup.py pyproject.toml
git commit -m "Bump version to 0.1.0"
git tag v0.1.0
git push origin master
git push origin v0.1.0
```

### 2. `publish-to-pypi.yml`
**Trigger:** When you create a GitHub Release

**Best for:** Formal releases with release notes

**Usage:**
1. Go to GitHub repository → Releases → "Draft a new release"
2. Create a new tag (e.g., `v0.1.0`)
3. Add release title and description
4. Click "Publish release"

### 3. `test-build.yml`
**Trigger:** On every push to master/main branch

**Best for:** Testing that the package builds correctly (publishes to TestPyPI)

**Note:** This helps catch build issues early without affecting production PyPI

## Setup Instructions

### Option A: Using Trusted Publishing (Recommended - No API tokens needed)

This is the modern, more secure approach that doesn't require managing API tokens.

1. **Build your package first** (optional, but good to test locally):
   ```bash
   pip install build
   python -m build
   ```

2. **Go to PyPI** (https://pypi.org/)
   - Log in to your account
   - Go to your account settings
   - Click on "Publishing" tab
   - Click "Add a new pending publisher"

3. **Fill in the trusted publishing form:**
   - PyPI Project Name: `instantgrade`
   - Owner: `chandraveshchaudhari`
   - Repository name: `evaluator`
   - Workflow name: `publish-on-tag.yml` (or whichever workflow you're using)
   - Environment name: `pypi` (optional, but recommended)

4. **Push a tag to trigger publishing:**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

5. **On first publish**, PyPI will automatically create the project and link it to your GitHub Actions workflow.

### Option B: Using API Tokens (Traditional method)

If you prefer using API tokens instead of trusted publishing:

1. **Get PyPI API Token:**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token
   - Set scope to "Entire account" or specific to "instantgrade" project (after first upload)
   - Copy the token (starts with `pypi-`)

2. **Add token to GitHub Secrets:**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your PyPI token
   - Click "Add secret"

3. **For TestPyPI** (optional):
   - Go to https://test.pypi.org/manage/account/token/
   - Create a token
   - Add to GitHub as `TEST_PYPI_API_TOKEN`

4. **Update workflow files** to use the token:
   - The workflows are already configured to use `PYPI_API_TOKEN`
   - For `publish-on-tag.yml`, add this under the publish step:
     ```yaml
     - name: Publish to PyPI
       uses: pypa/gh-action-pypi-publish@release/v1
       with:
         password: ${{ secrets.PYPI_API_TOKEN }}
     ```

## Workflow Comparison

| Workflow | Trigger | Target | Best For |
|----------|---------|--------|----------|
| `publish-on-tag.yml` | Version tags | PyPI | Production releases with semantic versioning |
| `publish-to-pypi.yml` | GitHub Releases | PyPI | Formal releases with release notes |
| `test-build.yml` | Every push to master | TestPyPI | Testing builds without affecting production |

## Recommended Workflow

For most projects, we recommend using **`publish-on-tag.yml`** with trusted publishing:

1. Develop and commit your changes
2. Update version in `setup.py`
3. Commit version change
4. Create and push a version tag
5. GitHub Actions automatically builds and publishes to PyPI
6. Users can install via `pip install evaluator`

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `v0.1.0` - Initial development release
- `v0.1.1` - Bug fix
- `v0.2.0` - New feature
- `v1.0.0` - First stable release

## Troubleshooting

### Build fails
- Check `setup.py` syntax
- Ensure all required files are in the repository
- Test locally with `python -m build`

### PyPI upload fails
- Verify API token is correct (if using tokens)
- Check if version already exists on PyPI
- Ensure package name is available
- For trusted publishing: verify PyPI publisher settings

### Import errors after installation
- Ensure `src/evaluator/__init__.py` exports correctly
- Check that all dependencies are listed in `setup.py`
- Verify package structure with `python -m build --wheel` and inspect the wheel

## Testing Before Publishing

Always test your package before publishing to production PyPI:

```bash
# Build the package
python -m build

# Install locally in development mode
pip install -e .

# Test import
python -c "from instantgrade import Evaluator; print('Success!')"

# Or publish to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

## Additional Resources

- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [PyPA Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Semantic Versioning](https://semver.org/)
