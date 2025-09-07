# Development Guide

This guide covers everything you need to know about developing, testing, and contributing to the Dialogue Guardian project.

## Project Structure

```
dialogue-guardian/
├── src/guardian/              # Main package source
│   ├── __init__.py           # Package initialization and exports
│   ├── core.py               # Core functionality (GuardianProcessor)
│   └── cli.py                # Command-line interface
├── tests/                    # Test suite
│   ├── test_guardian_core.py # Core functionality tests
│   └── test_guardian_cli.py  # CLI tests
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

# Run specific test
pytest tests/test_guardian_core.py::TestGuardianProcessor::test_init_default_values

# Run tests with verbose output
pytest -v
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

### Writing Tests

Follow these guidelines when writing tests:

1. **Use descriptive test names:**
   ```python
   def test_process_video_with_valid_file_succeeds(self):
   ```

2. **Use fixtures for common setup:**
   ```python
   @pytest.fixture
   def sample_video_file(self):
       return "samples/sample.mp4"
   ```

3. **Mock external dependencies:**
   ```python
   @patch('guardian.core.subprocess.run')
   def test_ffmpeg_call(self, mock_run):
   ```

4. **Test both success and failure cases:**
   ```python
   def test_process_video_success(self):
   def test_process_video_file_not_found(self):
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

The project includes several GitHub Actions workflows:

### CI Workflow (`.github/workflows/ci.yml`)
- Runs on every push and pull request
- Tests on multiple Python versions and operating systems
- Runs linting and tests
- Uploads coverage reports

### Documentation Workflow (`.github/workflows/docs.yml`)
- Builds and deploys documentation
- Runs on documentation changes
- Deploys to GitHub Pages

### Publishing Workflow (`.github/workflows/publish.yml`)
- Publishes package to PyPI
- Runs on releases or manual trigger
- Supports both PyPI and Test PyPI

### Release Workflow (`.github/workflows/release.yml`)
- Automates version bumping and release creation
- Manual trigger only
- Creates GitHub releases with changelogs

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