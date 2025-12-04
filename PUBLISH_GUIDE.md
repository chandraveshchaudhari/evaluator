# 🚀 Publish v0.1.1 to PyPI - Quick Guide

## Current Status
- ✅ Version: 0.1.1 in pyproject.toml and setup.py
- ✅ Tag: v0.1.1 created and pushed to GitHub
- ✅ GitHub Release: Should be created
- ⏳ PyPI Publish: **Need to verify and manually trigger if needed**

## Why Publish Didn't Run

The `publish.yml` workflow is triggered by:
1. **Release published event** - When you create a GitHub Release
2. **Tag push event** - When you push a version tag (v0.1.1)

However, tags created **inside GitHub Actions** don't always trigger other workflows immediately. This is a known GitHub limitation.

## Solution: Manually Trigger Publishing

### Method 1: Via GitHub Web UI (Easiest)

1. Go to: https://github.com/chandraveshchaudhari/instantgrade/actions
2. Find: **"Publish Python Package to PyPI"** workflow
3. Click on it
4. Click: **"Run workflow"** button
5. Select: **Branch: master** or **Tag: v0.1.1**
6. Click: **"Run workflow"**

### Method 2: Via GitHub CLI (Local)

```bash
# Install GitHub CLI if needed
brew install gh

# Authenticate (if needed)
gh auth login

# Trigger publish workflow
gh workflow run publish.yml \
  --repo chandraveshchaudhari/instantgrade \
  --ref v0.1.1

# Check status
gh run list --repo chandraveshchaudhari/instantgrade
```

### Method 3: Via API (Advanced)

```bash
# Create a GitHub Personal Access Token at:
# https://github.com/settings/tokens (with 'actions' and 'repo' scopes)

TOKEN="your_github_token_here"
OWNER="chandraveshchaudhari"
REPO="instantgrade"

curl -X POST \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/publish.yml/dispatches \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"ref":"master"}'

echo "Workflow triggered! Check: https://github.com/$OWNER/$REPO/actions"
```

## Verify PyPI Setup (CRITICAL)

**Before publishing, ensure PyPI Trusted Publishing is configured:**

1. Go to: https://pypi.org/manage/account/publishing/
2. Add a new pending publisher:
   - **PyPI Project Name**: `instantgrade`
   - **GitHub Repository Owner**: `chandraveshchaudhari`
   - **GitHub Repository Name**: `instantgrade`
   - **GitHub Workflow Filename**: `publish.yml`
   - **GitHub Environment**: (leave blank)

This allows GitHub Actions to publish without storing API tokens.

## Check If Package Is Already Published

```bash
# Check on PyPI
pip search instantgrade  # (pip search is deprecated, use the web instead)
# Or visit: https://pypi.org/project/instantgrade/

# Try to install
pip install instantgrade

# Check version
pip show instantgrade
```

## Next Time (Automatic)

After we fix the workflows, subsequent versions will auto-publish:

```bash
# Make code changes
git add .
git commit -m "fix: resolve issue"
git push origin master

# Automatic workflow:
# 1. Version bumps to 0.1.2
# 2. Tag v0.1.2 created
# 3. Release created
# 4. Published to PyPI automatically
```

## Troubleshooting

### "Release already exists"
- GitHub release for v0.1.1 already exists
- That's OK! The publish workflow will still trigger

### "Tag already exists"
- Local: `git tag -d v0.1.1` then recreate
- Remote: Force delete: `git push origin :refs/tags/v0.1.1`

### Publish workflow doesn't run
- Check: https://github.com/chandraveshchaudhari/instantgrade/actions/workflows/publish.yml
- Check workflow permissions in repo settings
- Ensure tag matches pattern `v[0-9]+.[0-9]+.[0-9]+`

## Files Updated

- ✅ `.github/workflows/version-bump.yml` - Improved tag creation and release handling
- ✅ `.github/workflows/publish.yml` - Added workflow_dispatch for manual triggers
- ✅ `PYPI_SETUP.md` - Complete PyPI setup documentation
- ✅ `scripts/publish_manual.sh` - Manual publish helper script
- ✅ `PUBLISH_GUIDE.md` - This file

## Quick Checklist

- [ ] 1. Verify v0.1.1 tag exists: `git tag -l | grep v0.1.1`
- [ ] 2. Check tag is on GitHub: https://github.com/chandraveshchaudhari/instantgrade/releases/tag/v0.1.1
- [ ] 3. Verify release exists: https://github.com/chandraveshchaudhari/instantgrade/releases
- [ ] 4. Set up PyPI Trusted Publishing (see above)
- [ ] 5. Manually trigger publish workflow (Method 1 easiest)
- [ ] 6. Wait 5-10 minutes for PyPI to process
- [ ] 7. Verify: `pip install instantgrade==0.1.1`

---

**Once you complete these steps, v0.1.1 will be available on PyPI!** 🎉
