# GitHub Actions Setup Guide

This guide explains how to set up and configure the GitHub Actions workflows for the Dialogue Guardian project.

## Overview

The project includes four main workflows:

1. **CI Workflow** - Continuous Integration testing
2. **Documentation Workflow** - Build and deploy documentation
3. **Publishing Workflow** - Publish to PyPI
4. **Release Workflow** - Automated releases

## Required Secrets

To use the publishing workflows, you need to configure these secrets in your GitHub repository:

### PyPI API Tokens

1. **Create PyPI Account**
   - Go to https://pypi.org and create an account
   - Verify your email address

2. **Generate API Token**
   - Go to https://pypi.org/manage/account/
   - Scroll to "API tokens" section
   - Click "Add API token"
   - Name: `dialogue-guardian-github-actions`
   - Scope: "Entire account" (or specific to your project)
   - Copy the token (starts with `pypi-`)

3. **Add to GitHub Secrets**
   - Go to your repository on GitHub
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token
   - Click "Add secret"

### Test PyPI (Optional but Recommended)

1. **Create Test PyPI Account**
   - Go to https://test.pypi.org and create an account

2. **Generate Test PyPI Token**
   - Follow same process as above on test.pypi.org
   - Add as `TEST_PYPI_API_TOKEN` secret

## Workflow Configuration

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to main/master branch
- Pull requests to main/master branch

**What it does:**
- Tests on multiple OS (Ubuntu, Windows, macOS)
- Tests Python versions 3.8-3.12
- Runs linting checks
- Runs test suite
- Builds package
- Uploads coverage to Codecov (optional)

**No configuration needed** - runs automatically.

### 2. Documentation Workflow (`.github/workflows/docs.yml`)

**Triggers:**
- Push to main/master (when docs change)
- Pull requests affecting docs
- Manual trigger

**What it does:**
- Builds Sphinx documentation
- Deploys to GitHub Pages

**Setup GitHub Pages:**
1. Go to repository Settings → Pages
2. Source: "GitHub Actions"
3. The workflow will automatically deploy docs

### 3. Publishing Workflow (`.github/workflows/publish.yml`)

**Triggers:**
- GitHub releases (automatic PyPI publishing)
- Manual trigger (choose TestPyPI or PyPI)

**Manual Publishing:**
1. Go to Actions tab
2. Select "Publish Package"
3. Click "Run workflow"
4. Choose environment (testpypi/pypi)
5. Click "Run workflow"

### 4. Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Manual trigger only

**Creating a Release:**
1. Go to Actions tab
2. Select "Create Release"
3. Click "Run workflow"
4. Choose version bump (patch/minor/major)
5. Optionally mark as prerelease
6. Click "Run workflow"

This will:
- Bump version in all files
- Create git tag
- Create GitHub release
- Trigger publishing workflow

## First Release Setup

### 1. Prepare Repository

```bash
# Ensure all files are committed
git add .
git commit -m "feat: complete project restructure to v1.1.0"
git push origin main
```

### 2. Test the Workflows

Before creating your first release, test the workflows:

```bash
# Test CI by pushing changes
git push origin main

# Test documentation build
# Go to Actions tab and manually trigger "Build and Deploy Documentation"

# Test publishing to TestPyPI
# Go to Actions tab, select "Publish Package", choose "testpypi"
```

### 3. Create First Release

Option A: **Manual GitHub Release**
1. Go to repository → Releases
2. Click "Create a new release"
3. Tag: `v1.1.0`
4. Title: `Release v1.1.0`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

Option B: **Automated Release Workflow**
1. Go to Actions → "Create Release"
2. Run workflow with "minor" bump
3. This will create v1.2.0 (since current is 1.1.0)

## Workflow Customization

### Modify Python Versions

Edit `.github/workflows/ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']  # Remove 3.12 if needed
```

### Modify Operating Systems

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]  # Only test on Ubuntu
```

### Add Environment Variables

```yaml
env:
  CUSTOM_VAR: "value"
```

### Add Additional Steps

```yaml
- name: Custom Step
  run: |
    echo "Custom command here"
```

## Troubleshooting

### Common Issues

1. **Workflow fails with "No module named 'guardian'"**
   ```yaml
   # Ensure this step is included:
   - name: Install dependencies
     run: |
       cd dialogue-guardian
       pip install -e .
   ```

2. **PyPI publishing fails with "403 Forbidden"**
   - Check API token is correct
   - Ensure package name isn't already taken
   - Verify token has correct permissions

3. **Documentation build fails**
   ```yaml
   # Ensure Sphinx dependencies are installed:
   - name: Install dependencies
     run: |
       pip install -r dev-requirements.txt
   ```

4. **Tests fail on Windows**
   - Check path separators (use `pathlib.Path`)
   - Verify FFmpeg is available on Windows runners

### Debug Workflows

1. **Add debug output:**
   ```yaml
   - name: Debug Info
     run: |
       python --version
       pip list
       pwd
       ls -la
   ```

2. **Use tmate for interactive debugging:**
   ```yaml
   - name: Setup tmate session
     uses: mxschmitt/action-tmate@v3
   ```

### Workflow Status Badges

Add to your README.md:

```markdown
[![CI](https://github.com/yourusername/dialogue-guardian/workflows/CI/badge.svg)](https://github.com/yourusername/dialogue-guardian/actions)
[![Documentation](https://github.com/yourusername/dialogue-guardian/workflows/Build%20and%20Deploy%20Documentation/badge.svg)](https://github.com/yourusername/dialogue-guardian/actions)
```

## Security Best Practices

1. **Use specific action versions:**
   ```yaml
   - uses: actions/checkout@v4  # Not @main
   ```

2. **Limit token permissions:**
   ```yaml
   permissions:
     contents: read
     packages: write
   ```

3. **Use environments for sensitive operations:**
   ```yaml
   environment: production  # Requires manual approval
   ```

4. **Never commit secrets:**
   - Use GitHub secrets
   - Use environment variables
   - Review commits before pushing

## Monitoring and Maintenance

### Regular Tasks

1. **Update action versions** (monthly)
2. **Review workflow runs** (weekly)
3. **Update Python versions** (when new versions release)
4. **Monitor security advisories**

### Notifications

Set up notifications:
1. Repository Settings → Notifications
2. Configure email/Slack notifications for workflow failures

## Advanced Configuration

### Matrix Exclusions

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.8', '3.9', '3.10', '3.11']
    exclude:
      - os: windows-latest
        python-version: '3.8'  # Skip Python 3.8 on Windows
```

### Conditional Steps

```yaml
- name: Windows-specific step
  if: runner.os == 'Windows'
  run: echo "Running on Windows"

- name: Only on main branch
  if: github.ref == 'refs/heads/main'
  run: echo "Main branch only"
```

### Caching

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Sphinx GitHub Pages](https://github.com/peaceiris/actions-gh-pages)
- [Action Marketplace](https://github.com/marketplace?type=actions)