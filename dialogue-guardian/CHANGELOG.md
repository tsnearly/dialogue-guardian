# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-15

### Changes
- Bump version: 1.1.5 → 1.2.0
- Workflow is now self-contained and will handle publishing to PyPI or TestPyPI, eliminating the new for a separate publish workflow.
- Update CHANGELOG.md and docs/changelog.rst for version 1.1.5
- Bump version: 1.1.4 → 1.1.5
- Correct versioning numbering
- Added license tag header
- Update CHANGELOG.md and docs/changelog.rst for version 1.1.4
- Bump version: 1.1.3 → 1.1.4
- Refactor version update process in release workflow to use a Python script for modifying docs/conf.py
- "Removed bumpversion configuration for src/guardian/cli.py"
- Addied a conditional setuptools installation
- Minor Python 3.8 compatibility issues
- Yet more minor code formatting issues that required adjustments
- The tests were failing because they were written for an older version of the CLI interface but the actual CLI had evolved to use named arguments instead of positional ones. This is a common issue when CLI interfaces change but tests aren't updated accordingly.
- Invalid dependency has been fixed
- Correct minor source formatting issues
- Shorten code lines that were too long
- Tweak testcases
- feat: update CLI argument handling to support multiple input files and change verbosity flag to debug
- feat: add OSV-Scanner installation to security workflow
- chore: update licensing information in pytest.ini and reorder imports in cli.py
- Split development doc into contributing; move license file to root; reduce length of a handful of lines that were too long in formatting.
- feat: optimize GitHub Actions workflows for 44% faster CI execution
- Enhance README and improve CLI argument handling
- Update release workflow to verify .bumpversion.cfg existence and enhance changelog generation
- Refactor logging setup and improve code readability in cli.py and core.py
- - Link to GitHub Pages documentation added - License reference corrected for consistency on upgrade; correction to project badges for license - Fix documentation for missing logo - Code coverage improved to nearly 95% by incorporating several test groups with many test cases
## [1.1.5] - 2025-09-15

### Changes
- Bump version: 1.1.4 → 1.1.5
- Correct versioning numbering
- Added license tag header
- Update CHANGELOG.md and docs/changelog.rst for version 1.1.4
- Bump version: 1.1.3 → 1.1.4
- Refactor version update process in release workflow to use a Python script for modifying docs/conf.py
- "Removed bumpversion configuration for src/guardian/cli.py"
- Addied a conditional setuptools installation
- Minor Python 3.8 compatibility issues
- Yet more minor code formatting issues that required adjustments
- The tests were failing because they were written for an older version of the CLI interface but the actual CLI had evolved to use named arguments instead of positional ones. This is a common issue when CLI interfaces change but tests aren't updated accordingly.
- Invalid dependency has been fixed
- Correct minor source formatting issues
- Shorten code lines that were too long
- Tweak testcases
- feat: update CLI argument handling to support multiple input files and change verbosity flag to debug
- feat: add OSV-Scanner installation to security workflow
- chore: update licensing information in pytest.ini and reorder imports in cli.py
- Split development doc into contributing; move license file to root; reduce length of a handful of lines that were too long in formatting.
- feat: optimize GitHub Actions workflows for 44% faster CI execution
- Enhance README and improve CLI argument handling
- Update release workflow to verify .bumpversion.cfg existence and enhance changelog generation
- Refactor logging setup and improve code readability in cli.py and core.py
- - Link to GitHub Pages documentation added - License reference corrected for consistency on upgrade; correction to project badges for license - Fix documentation for missing logo - Code coverage improved to nearly 95% by incorporating several test groups with many test cases

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2025-09-15

### Changes
- Bump version: 1.1.3 → 1.1.4
- Refactor version update process in release workflow to use a Python script for modifying docs/conf.py
- "Removed bumpversion configuration for src/guardian/cli.py"
- Addied a conditional setuptools installation
- Minor Python 3.8 compatibility issues
- Yet more minor code formatting issues that required adjustments
- The tests were failing because they were written for an older version of the CLI interface but the actual CLI had evolved to use named arguments instead of positional ones. This is a common issue when CLI interfaces change but tests aren't updated accordingly.
- Invalid dependency has been fixed
- Correct minor source formatting issues
- Shorten code lines that were too long
- Tweak testcases
- feat: update CLI argument handling to support multiple input files and change verbosity flag to debug
- feat: add OSV-Scanner installation to security workflow
- chore: update licensing information in pytest.ini and reorder imports in cli.py
- Split development doc into contributing; move license file to root; reduce length of a handful of lines that were too long in formatting.
- feat: optimize GitHub Actions workflows for 44% faster CI execution
- Enhance README and improve CLI argument handling
- Update release workflow to verify .bumpversion.cfg existence and enhance changelog generation
- Refactor logging setup and improve code readability in cli.py and core.py
- - Link to GitHub Pages documentation added - License reference corrected for consistency on upgrade; correction to project badges for license - Fix documentation for missing logo - Code coverage improved to nearly 95% by incorporating several test groups with many test cases
## [1.1.0] - 2025-01-07

### Added

- Complete project restructure into proper Python package
- Comprehensive Sphinx documentation with API reference
- GitHub Actions workflows for CI/CD, documentation, and publishing
- Professional package structure with src/ layout
- Makefile with documentation building commands
- Development tools and scripts
- Automated version bumping with bump2version
- Enhanced .gitignore for better project hygiene
- Python API for programmatic access
- Enhanced CLI with comprehensive options
- Automated PyPI publishing on releases
- Documentation deployment to GitHub Pages

### Changed

- Moved from single script to modular package structure
- Separated core functionality (`guardian.core`) from CLI (`guardian.cli`)
- Updated all configuration files for new structure
- Improved test organization and coverage
- Enhanced error handling and logging
- Version bumped to 1.1.0 to reflect major restructuring

### Fixed

- Package installation and distribution issues
- Test imports and module paths
- Documentation generation and serving

## [1.0.0] - 2024-12-XX

### Added

- Initial release with basic video censoring functionality
- FFmpeg-based audio censoring
- SRT subtitle processing
- Embedded subtitle extraction
- Command-line interface
- Basic testing framework
