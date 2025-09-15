Changelog
=========

For the complete changelog, see the `CHANGELOG.md <https://github.com/tsnearly/dialogue-guardian/blob/main/dialogue-guardian/CHANGELOG.md>`_ file in the repository.

Recent Changes
--------------

Version 1.2.0 (2025-09-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Changes:**

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

Version 1.1.0 (2025-01-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Added:**

- Complete project restructure with proper Python package layout
- Comprehensive test suite with pytest
- GitHub Actions CI/CD pipeline
- Automated PyPI publishing
- Documentation with Sphinx
- Code quality tools (Black, flake8, isort, mypy)
- Cross-platform compatibility (Windows, macOS, Linux)
- FFmpeg integration for audio processing
- SRT subtitle parsing and profanity detection
- Command-line interface with argparse
- Logging and error handling
- Package distribution setup

**Changed:**

- Migrated from standalone scripts to proper Python package
- Improved error handling and logging
- Enhanced cross-platform support
- Updated dependencies and requirements

**Fixed:**

- Various compatibility issues
- Import and module structure problems
- Path handling across different operating systems


Version 1.0.0 (2024-12-XX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Added:**

- Initial release with basic video censoring functionality
- FFmpeg-based audio censoring
- SRT subtitle processing
- Embedded subtitle extraction
- Command-line interface
- Basic testing framework