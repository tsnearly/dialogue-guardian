# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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