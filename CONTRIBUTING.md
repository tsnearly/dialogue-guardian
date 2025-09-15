# Contributing Guide

This guide covers everything you need to know about contributing to the Dialogue Guardian project.

# 

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