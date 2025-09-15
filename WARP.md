# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Dialogue Guardian is a Universal Media Censor that automatically detects and censors profane language in video files using subtitle analysis and FFmpeg audio processing. The project is structured as a Python package with CLI and API interfaces.

## Architecture

### Core Components

- **GuardianProcessor** (`dialogue-guardian/src/guardian/core.py`): Main processing engine that handles video analysis, SRT subtitle processing, profanity detection, and FFmpeg video processing
- **CLI Interface** (`dialogue-guardian/src/guardian/cli.py`): Command-line interface with argument parsing, logging setup, and user interaction
- **Package Structure**: Follows src-layout with source code in `dialogue-guardian/src/guardian/`

### Key Dependencies

- **FFmpeg**: External dependency for video/audio processing (must be installed separately)
- **srt2**: Python library for SRT subtitle file parsing
- **Python 3.8+**: Minimum supported version

### Data Flow

1. Video file input → FFprobe extracts metadata and embedded subtitles
2. SRT subtitle parsing → Profanity detection using configurable word list
3. Time interval extraction → FFmpeg audio muting at specific timestamps
4. Output generation → New censored video file (non-destructive)

## Essential Commands

### Development Setup
```bash
# Navigate to package directory
cd dialogue-guardian

# Install in development mode with all dependencies
make install-dev
# OR manually:
# pip install -e .
# pip install -r dev-requirements.txt
```

### Testing
```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run specific test file
pytest tests/test_guardian_core.py -v

# Run specific test method
pytest tests/test_guardian_core.py::TestGuardianProcessor::test_init_default_values -v

# Run tests with coverage
pytest --cov=guardian --cov-report=html
```

### Code Quality
```bash
# Run linting
make lint
# Individual tools:
# flake8 src/guardian/ tests/
# mypy src/guardian/

# Format code
make format
# Individual tools:
# black src/guardian/ tests/ examples/ *.py

# Run all checks
make check
```

### Documentation
```bash
# Build documentation
make docs

# Serve documentation locally at http://localhost:8000
make docs-serve

# Auto-rebuild docs on changes
make docs-auto

# Clean documentation build
make docs-clean
```

### Package Management
```bash
# Clean build artifacts
make clean

# Build package
make build

# Upload to PyPI (requires credentials)
make upload
```

## Working Directory Context

**Important**: This is a nested repository structure. The main package code is in `dialogue-guardian/` subdirectory, not the root. Most development commands must be run from the `dialogue-guardian/` directory.

```
dialogue-guardian/                    # Root repository
└── dialogue-guardian/                # Package directory
    ├── src/guardian/                 # Source code
    ├── tests/                        # Test suite
    ├── docs/                         # Sphinx documentation
    ├── Makefile                      # Development commands
    └── pyproject.toml                # Package configuration
```

## Testing Strategy

### Test Organization
- `test_guardian_core.py`: Core functionality tests with mocked FFmpeg calls
- `test_guardian_cli.py`: CLI interface tests
- `test_guardian_cli_extended.py`: Extended CLI scenarios
- `test_guardian_edge_cases.py`: Edge cases and error handling
- `test_guardian_integration.py`: Integration tests

### Testing Notes
- Tests extensively mock FFmpeg/FFprobe subprocess calls since they require external binary
- Sample files are used for testing subtitle parsing
- CI runs tests across Python 3.8-3.12 on Ubuntu, Windows, and macOS
- Coverage reports are uploaded to Codecov

## Key Development Considerations

### FFmpeg Integration
- All video processing relies on FFmpeg subprocess calls
- Commands must be constructed carefully to avoid shell injection
- FFmpeg availability is verified before processing
- Error handling includes FFmpeg-specific error codes and messages

### Cross-Platform Compatibility
- Code runs on Windows, macOS, and Linux
- Path handling uses pathlib for cross-platform compatibility
- FFmpeg installation varies by platform (handled in CI)

### Profanity Detection
- Configurable word list in `GuardianProcessor.DEFAULT_MATCHING_WORDS`
- Case-insensitive matching with word boundary detection
- Custom word lists can be provided via constructor

### Non-Destructive Processing
- Original files are never modified
- Output files use `_censored` suffix by default
- Video streams are copied without re-encoding to maintain quality
- Only audio streams are processed for muting

## Entry Points

The package provides two CLI entry points:
- `guardian` - Primary command
- `dialogue-guardian` - Alternative command name

Both execute `guardian.cli:main` function.

## GitHub Actions Workflows

**Important**: The workflows have been extensively optimized for efficiency:
- **Consolidated CI/CD**: Single `ci.yml` combines testing, quality checks, and building
- **Smart Caching**: Multi-layered caching for dependencies, FFmpeg binaries, and build tools
- **Conditional Execution**: Workflows only run when relevant files change
- **Performance**: ~44% faster execution, ~52% bandwidth reduction, ~75% fewer redundant jobs

Key workflows:
- `ci.yml` - Main CI/CD pipeline with fail-fast quality checks
- `quality.yml` - Advanced code analysis and security scanning
- `security.yml` - Comprehensive dependency vulnerability detection
- `docs.yml` - Smart documentation building with change detection
- `publish.yml` - Optimized PyPI publishing with validation
- `release.yml` - Automated version management and releases

## Project Rules

### Code Style
- Uses Black formatter with 88-character line length
- PEP 8 compliance enforced via Flake8
- Type hints required for public APIs
- Google-style docstrings

### Testing Requirements
- New features require corresponding tests
- Mock external dependencies (FFmpeg, file system operations)
- Aim for high test coverage (tracked via Codecov)
- Test both success and failure scenarios

### Documentation
- Sphinx-based documentation in `docs/`
- API documentation auto-generated from docstrings
- README provides quick start and usage examples
- **Workflow documentation** updated to reflect optimizations in `docs/github_actions_setup.md`
