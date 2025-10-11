# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Enhanced Audio Censoring System

### Added

- **Enhanced Audio Censoring System**: Multi-strategy progressive fallback system for improved censoring effectiveness
- **Silence Verification**: Automated verification that censored segments achieve target silence levels (≤ -50 dB)
- **Three-Tier Fallback Strategies**: 
  - Strategy 1: Basic Volume Reduction (legacy approach)
  - Strategy 2: Enhanced Silence with format normalization and compression
  - Strategy 3: Aggressive Null Mixing with advanced filtering
- **Comprehensive Diagnostics**: Detailed JSON diagnostic reports with segment-level analysis
- **Enhanced Logging**: Structured logging with operation tracking and performance metrics
- **Robust Error Handling**: Graceful handling of FFmpeg failures, missing files, and corrupted data
- **Quality Preservation Validation**: Automated verification that video properties are maintained
- **Advanced Filter Construction**: Dynamic FFmpeg filter graph construction based on strategy level
- **RMS Level Measurement**: Precise audio level measurement using FFmpeg astats filter
- **Comprehensive Test Suite**: 
  - `test_integration_complete.py`: Complete integration testing with sample media files
  - `test_end_to_end_workflow.py`: End-to-end workflow validation
- **Integration Validation Summary**: Detailed documentation of system validation and testing results

### Enhanced

- **Audio Censoring Effectiveness**: System now consistently achieves -100 dB silence (50 dB below requirement)
- **Fallback Mechanisms**: Progressive strategy escalation ensures censoring success even with challenging audio
- **Error Recovery**: Improved handling of edge cases and unexpected failures
- **Performance Monitoring**: Detailed timing and effectiveness metrics
- **Test Coverage**: Expanded test suite covering all enhancement scenarios

### Technical Improvements

- **Filter Strategy System**: Configurable multi-level filtering approach
- **Diagnostic Reporting**: Machine-readable JSON reports with recommendations
- **Verification Pipeline**: Automated post-processing validation
- **Logging Infrastructure**: Structured logging with multiple output formats
- **Integration Testing**: Real-world validation with sample media files

### Requirements Addressed

- **1.1-1.4**: Enhanced audio filtering with progressive fallback strategies
- **2.1-2.4**: Comprehensive silence verification and testing
- **3.1-3.3**: Cross-format compatibility and quality preservation  
- **4.1-4.4**: Detailed logging, diagnostics, and error handling

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
