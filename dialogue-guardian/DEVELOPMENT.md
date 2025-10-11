<!--
SPDX-FileCopyrightText: 2025 Tony Snearly

SPDX-License-Identifier: OSL-3.0
-->

# Development Guide

This guide covers everything you need to know about developing, testing, and contributing to the Dialogue Guardian project.

## Project Structure

```
dialogue-guardian/
├── src/guardian/              # Main package source
│   ├── __init__.py           # Package initialization and exports
│   ├── core.py               # Core functionality (GuardianProcessor) - REFACTORED
│   └── cli.py                # Command-line interface
├── tests/                    # Test suite - ENHANCED
│   ├── test_guardian_core.py # Core functionality tests
│   ├── test_guardian_pure_functions.py # NEW - Pure function tests (no mocks)
│   ├── test_guardian_cli.py  # CLI tests
│   ├── test_guardian_cli_extended.py # Extended CLI tests
│   ├── test_guardian_edge_cases.py # Edge case tests
│   ├── test_guardian_integration.py # Integration tests
│   ├── test_integration_complete.py # Complete integration tests
│   └── test_end_to_end_workflow.py # End-to-end workflow tests
├── docs/                     # Sphinx documentation
│   ├── conf.py               # Sphinx configuration
│   ├── index.rst             # Main documentation page
│   ├── api/                  # API reference
│   ├── installation.rst     # Installation guide
│   ├── quickstart.rst       # Quick start guide
│   └── cli_usage.rst        # CLI documentation
├── examples/                 # Usage examples
├── samples/                  # Sample files for testing
├── legacy/                   # Original files (preserved)
├── scripts/                  # Utility scripts
├── .github/workflows/        # GitHub Actions
├── setup.py                  # Package setup (traditional)
├── pyproject.toml            # Modern Python packaging
├── Makefile                  # Development commands
└── CHANGELOG.md              # Version history
```

## Development Setup

### Prerequisites

- Python 3.7 or higher
- FFmpeg installed and available in PATH
- Git for version control

### Initial Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd dialogue-guardian
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**

   ```bash
   cd dialogue-guardian
   make install-dev
   ```

   Or manually:

   ```bash
   pip install -e .
   pip install -r dev-requirements.txt
   ```

## Code Architecture

### Refactored Core Module

The `core.py` module has been **significantly refactored** to improve testability and maintainability:

#### Before Refactoring:
- Large monolithic functions mixing I/O with business logic
- Complex parsing logic buried inside subprocess calls
- Difficult to test without extensive mocking
- Hard to debug and maintain

#### After Refactoring:
- **Extracted pure functions** for all complex logic
- **Separation of concerns**: I/O operations separate from parsing logic
- **Highly testable**: Pure functions can be tested with real data
- **Modular design**: Small, focused functions with single responsibilities

#### Key Extracted Functions:

```python
# Video processing pure functions
def _parse_duration(self, duration_output: str) -> Dict[str, str]:
def _parse_audio_streams(self, ffprobe_output: str) -> Dict[str, str]:
def _parse_framerate_info(self, framerate_str: Optional[str]) -> Dict[str, Optional[str]]:
def _parse_video_stream_output(self, ffprobe_output: str) -> Dict[str, Optional[str]]:

# SRT processing pure functions  
def _parse_ffprobe_streams(self, json_output: str) -> List[Dict[str, Any]]:
def _find_srt_streams(self, streams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
def _select_best_srt_stream(self, srt_streams: List[Dict[str, Any]]) -> Optional[int]:
def _generate_srt_candidates(self, video_path: str) -> List[str]:

# Profanity detection pure functions
def _clean_subtitle_text(self, content: str) -> str:
def _build_profanity_pattern(self, words: List[str]) -> re.Pattern[str]:
def _contains_profanity(self, text: str, pattern: re.Pattern[str]) -> bool:

# FFmpeg command construction pure functions
def _build_volume_filters(self, segments: List[Tuple[float, float]], volume_setting: str) -> List[str]:
def _build_audio_filter_chain(self, segments: List[Tuple[float, float]], strategy_level: int) -> str:
def _build_ffmpeg_base_command(self, video_path: str, output_path: str, audio_filter_graph: str) -> List[str]:
```

#### Benefits of the Refactored Architecture:

1. **Better Testability**: Pure functions can be tested directly with real data
2. **Improved Maintainability**: Small, focused functions are easier to understand and modify
3. **Enhanced Debugging**: Issues can be isolated to specific functions
4. **Reduced Complexity**: Complex operations broken down into manageable pieces
5. **Better Code Reuse**: Pure functions can be reused in different contexts
6. **Easier Feature Development**: New features can leverage existing pure functions

## Development Workflow

### Common Commands

The project includes a Makefile with common development tasks:

```bash
# Install package in development mode
make install-dev

# Run tests
make test

# Run tests with coverage
make test-coverage

# Run linting
make lint

# Format code
make format

# Build documentation
make docs

# Serve documentation locally
make docs-serve

# Build package
make build

# Clean build artifacts
make clean
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=guardian --cov-report=html

# Run specific test file
pytest tests/test_guardian_core.py

# Run pure function tests (no mocks - fast execution)
pytest tests/test_guardian_pure_functions.py -v

# Run specific test
pytest tests/test_guardian_core.py::TestGuardianProcessor::test_init_default_values

# Run tests with verbose output
pytest -v

# Run only pure function tests with coverage
pytest tests/test_guardian_pure_functions.py --cov=src/guardian/core --cov-report=html
```

### Code Quality

The project uses several tools for code quality:

- **pytest**: Testing framework
- **flake8**: Linting
- **black**: Code formatting
- **isort**: Import sorting

```bash
# Run linting
flake8 src/ tests/

# Format code
black src/ tests/

# Sort imports
isort src/ tests/
```

### Documentation

Documentation is built with Sphinx:

```bash
# Build documentation
cd docs
make html

# Serve documentation locally
python -m http.server 8000 -d _build/html
```

## Testing

### Test Structure

Tests are organized by module:

- `test_guardian_core.py`: Tests for core functionality
- `test_guardian_cli.py`: Tests for CLI interface
- `test_guardian_cli_extended.py`: Extended CLI tests with edge cases and argument combinations
- `test_guardian_pure_functions.py`: **Pure function tests (34 tests) - no mocks, test actual logic**
- `test_guardian_edge_cases.py`: Tests for edge cases, malformed data, and unexpected failures
- `test_guardian_integration.py`: Integration tests with mocked dependencies
- `test_integration_complete.py`: Comprehensive integration tests with real media files
- `test_end_to_end_workflow.py`: End-to-end workflow validation tests

### Pure Function Testing Architecture

The project features a **hybrid testing approach** that combines traditional mocked tests with pure function tests:

#### Pure Function Tests (`test_guardian_pure_functions.py`)

**34 comprehensive tests** that validate actual business logic without mocks:

```python
# Example: Instead of mocking subprocess calls, test the actual parsing logic

# BEFORE: Mock-heavy integration test
@patch("subprocess.check_output")
def test_get_video_details_multiple_audio_streams(self, mock_check_output):
    mock_check_output.side_effect = [
        "120.5",  # duration
        "aac|44100|1|mono\naac|48000|6|5.1",  # audio streams  
        "1920\n1080\n30000/1001",  # video info
    ]
    result = self.processor.get_video_details(self.test_video_path)
    # Tests mock setup, not actual logic

# AFTER: Pure function tests for each component
def test_parse_audio_streams_multiple_streams(self):
    """Test audio stream selection logic with real data"""
    ffprobe_output = "aac|44100|1|mono\naac|48000|6|5.1"
    result = self.processor._parse_audio_streams(ffprobe_output)
    # Should pick the 6-channel stream
    expected = {"codec": "aac", "samplerate": "48000", "channels": "6", "audioconfig": "5.1"}
    self.assertEqual(result, expected)

def test_parse_video_stream_output_complete(self):
    """Test video dimension and framerate parsing with real data"""
    ffprobe_output = "1920\n1080\n30000/1001"
    result = self.processor._parse_video_stream_output(ffprobe_output)
    expected = {
        "width": "1920", "height": "1080", "framerate": "30000/1001",
        "fps": "29.970", "frameduration": "1001/30000"
    }
    self.assertEqual(result, expected)

def test_parse_framerate_info_division_by_zero(self):
    """Test edge case: division by zero in framerate"""
    result = self.processor._parse_framerate_info("30000/0")
    expected = {"framerate": None, "fps": None, "frameduration": None}
    self.assertEqual(result, expected)  # Should handle gracefully
```

**Categories of Pure Function Tests:**

1. **Video Details Parsing Functions:**
   - `_parse_duration()` - Duration parsing logic
   - `_parse_audio_streams()` - Audio stream selection logic
   - `_parse_framerate_info()` - Complex framerate calculations  
   - `_parse_video_stream_output()` - Video dimension parsing

2. **SRT Processing Functions:**
   - `_parse_ffprobe_streams()` - JSON parsing logic
   - `_find_srt_streams()` - Stream filtering logic
   - `_select_best_srt_stream()` - Stream prioritization logic
   - `_generate_srt_candidates()` - File path generation

3. **Profanity Detection Functions:**
   - `_clean_subtitle_text()` - Text cleaning logic
   - `_build_profanity_pattern()` - Regex compilation
   - `_contains_profanity()` - Profanity matching logic

4. **FFmpeg Command Construction Functions:**
   - `_build_volume_filters()` - Volume filter generation
   - `_build_audio_filter_chain()` - Complete filter chain logic
   - `_build_ffmpeg_base_command()` - Command construction

**Benefits of Pure Function Tests:**
- **Real Logic Testing**: Tests actual parsing, filtering, and processing logic with real data
- **Better Bug Detection**: Catches real parsing errors, edge cases, and logic bugs that mocks would hide
- **No External Dependencies**: Tests pure functions that don't require FFmpeg or file I/O
- **Easy to Maintain**: Simple, direct function calls without complex mock setups
- **Fast Execution**: No subprocess calls or file I/O operations
- **Edge Case Coverage**: Tests division by zero, malformed data, empty inputs, special characters

#### When to Use Pure Function Tests vs Mocked Tests

**Use Pure Function Tests for:**
- Data parsing and transformation logic
- Mathematical calculations and algorithms
- String processing and regex operations
- Data structure manipulation
- Business logic that doesn't require external dependencies

**Use Mocked Tests for:**
- File I/O operations
- Subprocess calls (FFmpeg/ffprobe)
- Network operations
- System-dependent functionality
- Integration between components

### Writing Tests

Follow these guidelines when writing tests:

1. **Use descriptive test names:**

   ```python
   def test_process_video_with_valid_file_succeeds(self):
   ```

2. **Prefer pure function tests over mocked tests when possible:**

   ```python
   # BEFORE - Mock-heavy test that hides actual logic
   @patch("subprocess.check_output")
   def test_get_video_details_multiple_audio_streams(self, mock_check_output):
       mock_check_output.side_effect = [
           "120.5",  # duration
           "aac|44100|1|mono\naac|48000|6|5.1",  # multiple audio streams
           "1920\n1080\n30000/1001",  # video info
       ]
       result = self.processor.get_video_details(self.test_video_path)
       # This tests mock interactions, not the actual parsing logic

   # AFTER - Pure function tests that validate actual logic
   def test_parse_audio_streams_multiple_streams(self):
       """Test audio stream selection logic with real data"""
       ffprobe_output = "aac|44100|1|mono\naac|48000|6|5.1"
       result = self.processor._parse_audio_streams(ffprobe_output)
       # Should pick the 6-channel stream
       self.assertEqual(result["channels"], "6")
       self.assertEqual(result["samplerate"], "48000")

   def test_parse_video_stream_output_complete(self):
       """Test video info parsing logic with real data"""
       ffprobe_output = "1920\n1080\n30000/1001"
       result = self.processor._parse_video_stream_output(ffprobe_output)
       expected = {
           "width": "1920",
           "height": "1080", 
           "framerate": "30000/1001",
           "fps": "29.970",
           "frameduration": "1001/30000"
       }
       self.assertEqual(result, expected)

   def test_parse_framerate_info_fraction_format(self):
       """Test complex framerate calculation logic"""
       result = self.processor._parse_framerate_info("30000/1001")
       self.assertEqual(result["fps"], "29.970")
       self.assertEqual(result["frameduration"], "1001/30000")
   ```

3. **Use fixtures for common setup:**

   ```python
   @pytest.fixture
   def sample_video_file(self):
       return "samples/sample.mp4"
   ```

4. **Mock external dependencies only when necessary:**

   ```python
   @patch('guardian.core.subprocess.run')
   def test_ffmpeg_call(self, mock_run):
   ```

5. **Test both success and failure cases:**
   ```python
   def test_process_video_success(self):
   def test_process_video_file_not_found(self):
   ```

6. **Extract complex logic into pure functions for better testability:**
   ```python
   # Extract this logic into a pure function
   def _parse_framerate(self, framerate_str: str) -> Dict[str, str]:
       # Complex parsing logic here
       
   # Then test it directly without mocks
   def test_parse_framerate_division_by_zero(self):
       result = self.processor._parse_framerate("30000/0")
       self.assertIsNone(result["fps"])
   ```

### Test Coverage

Aim for high test coverage:

```bash
# Generate coverage report
pytest --cov=guardian --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Code Style

### Python Style Guide

Follow PEP 8 with these specific guidelines:

- **Line length**: 88 characters (Black default)
- **Imports**: Use isort for consistent import ordering
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Use where appropriate

### Example Code Style

```python
"""Module docstring describing the module purpose."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

from guardian.core import GuardianProcessor


class ExampleClass:
    """Class docstring describing the class purpose.

    Args:
        param1: Description of parameter 1.
        param2: Description of parameter 2.
    """

    def __init__(self, param1: str, param2: Optional[int] = None) -> None:
        self.param1 = param1
        self.param2 = param2

    def example_method(self, input_data: List[str]) -> Union[str, None]:
        """Method docstring describing what the method does.

        Args:
            input_data: List of input strings to process.

        Returns:
            Processed string or None if processing fails.

        Raises:
            ValueError: If input_data is empty.
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")

        return " ".join(input_data)
```

## Package Management

### Version Management

The project uses `bump2version` for version management:

```bash
# Install bump2version
pip install bump2version

# Bump patch version (1.1.0 -> 1.1.1)
bump2version patch

# Bump minor version (1.1.0 -> 1.2.0)
bump2version minor

# Bump major version (1.1.0 -> 2.0.0)
bump2version major
```

### Building and Distribution

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## GitHub Actions

The project includes several optimized GitHub Actions workflows:

### CI/CD Pipeline (`.github/workflows/ci.yml`)

- **Consolidated workflow** combining testing, quality checks, and building
- Runs on every push and pull request
- Tests on multiple Python versions (3.8-3.12) and operating systems
- **Enhanced caching** for dependencies and FFmpeg binaries
- **Fail-fast quality checks** run before expensive test matrix
- Runs linting, type checking, and comprehensive tests
- Uploads coverage reports to Codecov
- Builds and validates package

### Code Quality Analysis (`.github/workflows/quality.yml`)

- **Advanced quality analysis** beyond basic CI checks
- Runs complexity analysis, dead code detection
- **Path-based triggering** - only runs when relevant code changes
- Includes comprehensive security scanning
- Scheduled weekly runs for ongoing quality assurance

### Security Scanning (`.github/workflows/security.yml`)

- **Focused dependency security analysis**
- Multiple security tools: Safety, pip-audit, OSV scanner, CodeQL
- **Intelligent triggering** on dependency-related changes
- Comprehensive vulnerability detection and reporting

### Documentation (`.github/workflows/docs.yml`)

- Builds and deploys Sphinx documentation to GitHub Pages
- **Smart change detection** - only rebuilds when needed
- **Enhanced caching** for both dependencies and build artifacts
- Supports incremental builds for faster execution

### Publishing (`.github/workflows/publish.yml`)

- Publishes package to PyPI and Test PyPI
- **Optimized validation** with reduced test matrix
- Runs on releases or manual trigger
- **Propagation delays** for reliable package validation
- Post-publish validation for releases

### Release Automation (`.github/workflows/release.yml`)

- Automates version bumping and release creation
- Manual trigger with version bump selection
- Creates GitHub releases with auto-generated changelogs
- **Specialized caching** for release tools
- Triggers publishing workflow automatically

## Contributing

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**

   - Write code following the style guide
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests and linting:**

   ```bash
   make test
   make lint
   ```

5. **Commit your changes:**

   ```bash
   git commit -m "Add feature: description of your feature"
   ```

6. **Push to your fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request**

### Commit Message Guidelines

Use conventional commit messages:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Examples:

```
feat: add support for WebVTT subtitle format
fix: handle missing subtitle files gracefully
docs: update installation instructions
test: add tests for CLI argument parsing
```

## Debugging

### Common Issues

1. **FFmpeg not found:**

   ```bash
   # Check if FFmpeg is installed
   ffmpeg -version

   # Install FFmpeg (macOS)
   brew install ffmpeg

   # Install FFmpeg (Ubuntu)
   sudo apt update && sudo apt install ffmpeg
   ```

2. **Import errors:**

   ```bash
   # Install package in development mode
   pip install -e .
   ```

3. **Test failures:**

   ```bash
   # Run tests with verbose output
   pytest -v -s

   # Run specific failing test
   pytest tests/test_guardian_core.py::test_name -v -s
   ```

### Debugging Tools

- **pdb**: Python debugger

  ```python
  import pdb; pdb.set_trace()
  ```

- **pytest debugging:**

  ```bash
  pytest --pdb  # Drop into debugger on failures
  pytest -s     # Don't capture output
  ```

- **Logging:**
  ```python
  import logging
  logging.basicConfig(level=logging.DEBUG)
  ```

## Performance Considerations

### Profiling

```bash
# Profile code execution
python -m cProfile -o profile.stats your_script.py

# Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

### Memory Usage

```bash
# Monitor memory usage
pip install memory-profiler
python -m memory_profiler your_script.py
```

## Security

### Security Best Practices

1. **Input validation**: Always validate user inputs
2. **Path traversal**: Use `pathlib.Path` for safe path handling
3. **Command injection**: Use `subprocess` with lists, not strings
4. **Dependencies**: Keep dependencies updated

### Security Scanning

```bash
# Scan for security vulnerabilities
pip install safety
safety check

# Scan for secrets
pip install detect-secrets
detect-secrets scan
```

## Release Process

### Creating a Release

1. **Update version and changelog:**

   ```bash
   # Update CHANGELOG.md with new version info
   # Commit changes
   git add CHANGELOG.md
   git commit -m "chore: update changelog for v1.2.0"
   ```

2. **Create release via GitHub Actions:**

   - Go to Actions tab in GitHub
   - Select "Create Release" workflow
   - Choose version bump type
   - Run workflow

3. **Verify release:**
   - Check GitHub releases page
   - Verify PyPI upload
   - Test installation: `pip install dialogue-guardian`

### Hotfix Process

For urgent fixes:

1. **Create hotfix branch from main:**

   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/fix-description
   ```

2. **Make minimal fix and test:**

   ```bash
   # Make changes
   make test
   ```

3. **Create pull request and merge**

4. **Create patch release:**
   - Use release workflow with "patch" option

## Troubleshooting

### Common Development Issues

1. **Virtual environment issues:**

   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Package import issues:**

   ```bash
   # Check package installation
   pip list | grep dialogue-guardian

   # Reinstall in development mode
   pip install -e .
   ```

3. **Test environment issues:**

   ```bash
   # Clear pytest cache
   rm -rf .pytest_cache

   # Reinstall test dependencies
   pip install -r dev-requirements.txt
   ```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

## Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the docs at [project-docs-url]
- **Code Review**: Request reviews on pull requests
