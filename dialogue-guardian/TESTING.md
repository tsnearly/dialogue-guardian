<!--
SPDX-FileCopyrightText: 2025 Tony Snearly

SPDX-License-Identifier: OSL-3.0
-->

# Testing Guide for Dialogue Guardian

This document provides instructions for running and developing unit tests for the Dialogue Guardian project.

## Test Structure

The test suite is organized into the following files located in the `tests/` directory:

-   **`test_guardian_cli.py`**: Unit tests for the command-line interface (CLI) argument parsing and main execution flow.
-   **`test_guardian_cli_extended.py`**: Extended tests for the CLI, covering more edge cases and argument combinations.
-   **`test_guardian_core.py`**: Unit tests for the core processing logic in `guardian/core.py`.
-   **`test_guardian_pure_functions.py`**: **NEW** - Pure function tests that test actual logic without mocks (34 tests).
-   **`test_guardian_edge_cases.py`**: Tests for specific edge cases in the core logic, such as malformed data and unexpected failures.
-   **`test_guardian_integration.py`**: Integration tests that verify the interaction between different components and with `ffmpeg`/`ffprobe` (using mocks).
-   **`test_integration_complete.py`**: Comprehensive integration tests for the enhanced audio censoring system with sample media files.
-   **`test_end_to_end_workflow.py`**: End-to-end workflow validation tests covering complete SRT parsing to output verification.

## Running Tests

### Using pytest (Recommended)

First, install the test dependencies:

```bash
pip install -r test_requirements.txt
```

Run all tests from the `dialogue-guardian` directory:

```bash
pytest
```

Or more explicitly:
```bash
python3 -m pytest tests/
```

Run tests for a specific file:

```bash
pytest tests/test_guardian_core.py
```

Run tests with coverage:

```bash
pytest --cov=src/guardian
```

### Option 2: Using Makefile

Convenience targets are available in the `Makefile`:

```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose
```

## Test Categories

### CLI Tests (`test_guardian_cli.py`, `test_guardian_cli_extended.py`)

-   Tests for argument parsing (`--input`, `--output`, `--debug`, etc.).
-   Validation of arguments (e.g., file existence).
-   Main application entry point (`main()`) success and failure scenarios.
-   Logging setup.

### Core Logic Tests (`test_guardian_core.py`)

-   Tests for `GuardianProcessor` initialization.
-   SRT file finding and parsing logic.
-   Profanity detection in subtitle segments.
-   Construction of `ffmpeg` commands.

### Pure Function Tests (`test_guardian_pure_functions.py`) - **NEW**

**34 tests that validate actual logic without mocks:**

-   **Video Details Parsing**: Tests audio stream selection, framerate calculations, and video dimension parsing with real data
-   **SRT Processing**: Tests JSON parsing, stream filtering, and stream prioritization logic
-   **Profanity Detection**: Tests text cleaning, regex compilation, and profanity matching with various patterns
-   **FFmpeg Command Construction**: Tests volume filter generation, audio filter chains, and command building
-   **Edge Cases**: Division by zero, malformed data, empty inputs, special characters, and encoding issues

**Key Benefits:**
- Tests real parsing logic instead of mock interactions
- Catches actual bugs in data processing
- Validates edge cases with real data scenarios
- No external dependencies required (pure functions)

### Edge Case Tests (`test_guardian_edge_cases.py`)

-   Tests for handling malformed video metadata.
-   Graceful failure on unexpected exceptions.
-   Behavior with empty or specially-formatted profanity lists.

### Integration Tests (`test_guardian_integration.py`)

-   Tests the end-to-end workflow, from video processing to censoring.
-   Interaction with `ffmpeg` and `ffprobe` (mocked).
-   Extraction of embedded SRT files.
-   Fallback mechanisms (e.g., from external to embedded SRT).

### Enhanced Integration Tests (`test_integration_complete.py`)

-   Comprehensive testing of the enhanced audio censoring system.
-   Sample media file validation with real video and SRT files.
-   Profanity pattern variations and audio format compatibility testing.
-   Silence verification and quality preservation validation.

### End-to-End Workflow Tests (`test_end_to_end_workflow.py`)

-   Complete workflow validation from SRT parsing to final output verification.
-   Error handling and fallback mechanism testing.
-   Logging and diagnostic system validation.
-   Embedded SRT workflow testing.

## Testing Strategy

The project uses a **hybrid testing approach** combining mocked integration tests with pure function tests:

### Mocked Integration Tests

Traditional tests use extensive mocking via `unittest.mock` to:

-   Avoid actual FFmpeg/ffprobe operations during unit testing, ensuring tests are fast and don't require external dependencies to be installed.
-   Simulate various error conditions (e.g., `subprocess.CalledProcessError`, `FileNotFoundError`).
-   Test edge cases without requiring actual video/SRT files.

### Pure Function Tests (**NEW**)

**34 pure function tests** validate actual business logic without mocks:

-   **Real Data Testing**: Uses actual data structures and strings to test parsing logic
-   **No External Dependencies**: Tests pure functions that don't require FFmpeg or file I/O
-   **Better Bug Detection**: Catches real parsing errors, edge cases, and logic bugs
-   **Maintainable**: Easy to understand and modify without complex mock setups

### Key Mock Objects

-   **`subprocess.run` / `subprocess.check_output`**: Mocks `ffprobe`/`ffmpeg` execution.
-   **`os.path.exists`**: Mocks file system checks.
-   **`builtins.open`**: Mocks file I/O operations.
-   **`srt.parse`**: Mocks the parsing of SRT files.
-   **`platform.system`**: Mocks the operating system check for cross-platform testing.

## Test Dependencies

Install test-specific dependencies:

```bash
pip install -r test_requirements.txt
```

## Coverage Report

After running tests with pytest, view the coverage report:

-   **Console**: `pytest --cov=src/guardian`
-   **HTML**: Open `htmlcov/index.html` in your browser after running `pytest --cov-report html src/guardian`.

## Adding New Tests

1.  Add new test methods to the appropriate test class in the `tests/` directory.
2.  Follow the naming convention: `test_<function_name>_<scenario>`.
3.  Use mocking for external dependencies in unit tests.
4.  Include both success and failure scenarios.
5.  Add docstrings explaining what each test verifies.