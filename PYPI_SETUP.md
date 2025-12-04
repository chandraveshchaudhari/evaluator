# PyPI Publishing Setup Guide

## ⚠️ IMPORTANT: PyPI Trusted Publishing Configuration

For the automated publishing to work, you need to configure **PyPI Trusted Publishing**. This allows GitHub Actions to publish to PyPI without storing API tokens.

### Step 1: Register Your Package on PyPI (if not already done)

```bash
# Build locally
python -m build

# Upload to PyPI (requires PyPI account)
twine upload dist/*
```

Or visit: https://pypi.org/account/register/

### Step 2: Configure Trusted Publishing on PyPI

1. Go to: https://pypi.org/manage/account/publishing/
2. Click **"Add a new pending publisher"**
3. Fill in:
   - **PyPI Project Name**: `instantgrade`
   - **GitHub Repository Owner**: `chandraveshchaudhari`
   - **GitHub Repository Name**: `instantgrade`
   - **GitHub Workflow Filename**: `publish.yml`
   - **GitHub Environment Name**: (leave blank)
4. Click **"Add"**

### Step 3: Verify Configuration

Once configured, you can publish automatically by:
1. Creating a GitHub Release
2. Pushing a version tag (e.g., `v0.1.1`)
3. The `publish.yml` workflow will run automatically

## Current Status

### For v0.1.1

**Tag Status:**
- ✅ Tag `v0.1.1` exists on GitHub
- Version in `pyproject.toml`: `0.1.1`
- Version in `setup.py`: `0.1.1`

**Next Steps:**

1. **Option A: Automatic (Recommended)**
   - Ensure PyPI Trusted Publishing is configured (see above)
   - Push any code change to master (with different commit)
   - The workflows will auto-bump version and publish

2. **Option B: Manual Trigger**
   ```bash
   # Go to GitHub Actions
   # Find "Publish Python Package to PyPI"
   # Click "Run workflow"
   # Select branch: master (or use the tag directly)
   ```

3. **Option C: Use Local Script**
   ```bash
   ./scripts/publish_manual.sh 0.1.1
   ```

## Verify Published Package

```bash
# After publishing (wait ~5 minutes for PyPI to process)
pip install --upgrade instantgrade

# Check version
pip show instantgrade
python -c "from instantgrade import Evaluator; print('Success!')"
```

## Troubleshooting

### Publishing Failed: "No file was uploaded to PyPI"

This typically means:
1. **Trusted Publishing not configured** - See Step 2 above
2. **Workflow permission issues** - Check GitHub repo settings > Actions > General > Workflow permissions
3. **PyPI project not registered** - Register at https://pypi.org/project/instantgrade/

### Publishing Failed: "This filename has already been used"

This means version 0.1.1 was already published. To republish:
1. Bump patch version: `0.1.1` → `0.1.2` in both files
2. Commit and push
3. Auto-version-bump workflow will handle it

### Tag Already Exists Error

If you get "tag already exists" locally:
```bash
# Delete local tag
git tag -d v0.1.1

# Create new tag
git tag -a v0.1.1 -m "Release v0.1.1"

# Force push
git push origin v0.1.1 --force
```

## Manual PyPI Setup (Alternative to Trusted Publishing)

If you prefer using PyPI tokens instead of Trusted Publishing:

1. Generate PyPI API token at: https://pypi.org/manage/account/tokens/
2. Add to GitHub secrets:
   - Go to: https://github.com/chandraveshchaudhari/instantgrade/settings/secrets/actions
   - Add new secret: `PYPI_API_TOKEN`
   - Value: Your PyPI token

3. Update `publish.yml` to use the token:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
       verbose: true
   ```

## Recommended Workflow

### For Patch Updates (Bug Fixes)
```bash
# Make changes
git add .
git commit -m "fix: resolve timeout issue"
git push origin master

# Result:
# 1. Version auto-bumps: 0.1.1 → 0.1.2
# 2. Tag created: v0.1.2
# 3. GitHub Release created
# 4. Published to PyPI automatically
```

### For Feature Updates (Minor Version)
```bash
# Update version manually in pyproject.toml and setup.py
# 0.1.x → 0.2.0

git add pyproject.toml setup.py src/
git commit -m "feat: add new comparison features"
git push origin master

# Result:
# 1. Tag created: v0.2.0
# 2. GitHub Release created
# 3. Published to PyPI automatically
```

## GitHub Actions Workflows

### version-bump.yml
- Triggers: Push to master with changes in src/, setup.py, or pyproject.toml
- Actions:
  1. Detects current version
  2. If tag exists, bumps patch version
  3. Creates/pushes tag
  4. Creates GitHub Release
  5. Triggers publish workflow

### publish.yml
- Triggers:
  1. Release published on GitHub
  2. Version tag pushed
  3. Manual workflow_dispatch
- Actions:
  1. Builds package
  2. Verifies package structure
  3. Publishes to PyPI using Trusted Publishing
  4. Verifies installation from PyPI

## Quick Reference

```bash
# Check current version
grep "version" pyproject.toml | head -1

# Build locally
python -m build

# Check package
twine check dist/*

# List local tags
git tag -l

# Check GitHub release
gh release view v0.1.1

# Manually trigger publish workflow
gh workflow run publish.yml --repo chandraveshchaudhari/instantgrade --ref v0.1.1
```
