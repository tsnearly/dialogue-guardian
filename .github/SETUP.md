# GitHub Actions Setup

This repository uses GitHub Actions for CI/CD. To enable all features, you'll need to configure the following secrets in your GitHub repository settings.

## Required Secrets

### PyPI Publishing
- `PYPI_API_TOKEN` - Your PyPI API token for publishing releases
- `TEST_PYPI_API_TOKEN` - Your Test PyPI API token for testing releases (optional)

### Code Coverage
- `CODECOV_TOKEN` - Your Codecov token for coverage reporting (optional, public repos work without it)

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Click on **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the name and value

## Getting API Tokens

### PyPI Token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to "API tokens" section
3. Click "Add API token"
4. Give it a name like "dialogue-guardian-ci"
5. Select scope (recommend "Entire account" or specific project)
6. Copy the token (starts with `pypi-`)

### Test PyPI Token (Optional)
1. Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/)
2. Follow same steps as PyPI

### Codecov Token (Optional)
1. Go to [Codecov](https://codecov.io/)
2. Sign in with GitHub
3. Add your repository
4. Copy the repository token

## Workflow Status

Without these secrets, the workflows will still run but:
- ✅ Tests will run normally
- ✅ Code quality checks will run normally  
- ✅ Security scans will run normally
- ⚠️ PyPI publishing will be skipped (no token)
- ⚠️ Coverage reporting may not work (no token)

The workflows are designed to gracefully handle missing secrets and continue with available functionality.