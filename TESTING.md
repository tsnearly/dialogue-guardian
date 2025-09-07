# Testing Guide for Dialogue Guardian

This document provides instructions for running and developing unit tests for the Dialogue Guardian project.

## Test Structure

The test suite is organized into the following components:

- **`test_guardian.py`**: Unit tests for `guardian.py` (FCPXML generation).
- **`test_guardian_by_ffmpeg.py`**: Unit tests for `guardian_by_ffmpeg.py` (FFmpeg-based censoring).

## Running Tests

### Option 1: Using Python's built-in unittest

Run all tests using the provided script:
```bash
python run_tests.py
```

### Option 2: Using pytest (recommended)

First, install the test dependencies:
```bash
pip install -r test_requirements.txt
```

Run all tests:
```bash
pytest
```

Run tests for a specific file:
```bash
pytest test_guardian.py
pytest test_guardian_by_ffmpeg.py
```

Run with coverage for both scripts:
```bash
pytest --cov=guardian --cov=guardian_by_ffmpeg
```

### Option 3: Using unittest directly

```bash
python -m unittest test_guardian.py
python -m unittest test_guardian_by_ffmpeg.py
```

## Test Categories

### `guardian.py` Tests

- **`test_get_video_details_*`**: Tests for video metadata extraction using ffprobe.
- **`test_create_fcpxml_*`**: Tests for FCPXML generation, including SRT parsing, profanity detection, and keyframe logic.
- **`test_xml_structure`**: Tests the basic structure of the generated FCPXML.

### `guardian_by_ffmpeg.py` Tests

- **`test_get_video_details_*`**: Tests for video metadata extraction.
- **`test_extract_embedded_srt_*`**: Tests for SRT subtitle extraction.
- **`test_censor_audio_with_ffmpeg_*`**: Tests for audio censoring functionality.
- **`test_matching_words_list`**: Tests for profanity word list.
- **`test_end_to_end_workflow`**: Tests complete workflow with mocked dependencies.

## Mocking Strategy

The tests use extensive mocking to:
- Avoid actual FFmpeg/ffprobe operations during testing.
- Simulate various error conditions.
- Test edge cases without requiring actual video/SRT files.

### Key Mock Objects
- **`subprocess.Popen` / `subprocess.run`**: Mocks ffprobe/ffmpeg execution.
- **`os.path.exists`**: Mocks file system checks.
- **`builtins.open`**: Mocks file I/O operations.
- **`srt.parse`**: Mocks the parsing of SRT files.

## Test Dependencies

Install test-specific dependencies:
```bash
pip install -r test_requirements.txt
```

## Coverage Report

After running tests with pytest, view the coverage report:
- **Console**: `pytest --cov=guardian --cov=guardian_by_ffmpeg`
- **HTML**: Open `htmlcov/index.html` in your browser after running `pytest --cov-report html`.

## Adding New Tests

1. Add new test methods to the appropriate test class (`TestGuardian` or `TestGuardianByFFmpeg`).
2. Follow the naming convention: `test_<function_name>_<scenario>`.
3. Use mocking for external dependencies.
4. Include both success and failure scenarios.
5. Add docstrings explaining what each test verifies.