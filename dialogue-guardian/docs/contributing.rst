Contributing to Dialogue Guardian
==================================

We welcome contributions to Dialogue Guardian! This guide will help you get started with contributing to the project.

Getting Started
---------------

1. **Fork the Repository**
   
   Fork the repository on GitHub and clone your fork locally:
   
   .. code-block:: bash
   
      git clone https://github.com/tsnearly/dialogue-guardian.git
      cd dialogue-guardian

2. **Set Up Development Environment**
   
   .. code-block:: bash
   
      # Create virtual environment
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      
      # Install development dependencies
      cd dialogue-guardian
      pip install -r dev-requirements.txt
      pip install -e .

3. **Run Tests**
   
   Make sure all tests pass before making changes:
   
   .. code-block:: bash
   
      pytest tests/
      
Development Workflow
--------------------

1. **Create a Branch**
   
   Create a new branch for your feature or bug fix:
   
   .. code-block:: bash
   
      git checkout -b feature/your-feature-name

2. **Make Changes**
   
   - Write your code following the existing style
   - Add tests for new functionality
   - Update documentation if needed

3. **Run Quality Checks**
   
   .. code-block:: bash
   
      # Format code
      black src/ tests/
      isort src/ tests/
      
      # Run linting
      flake8 src/ tests/ --config .flake8
      
      # Run tests
      pytest tests/
      
      # Check type hints
      mypy src/guardian/ --ignore-missing-imports

4. **Commit Changes**
   
   Use conventional commit messages:
   
   .. code-block:: bash
   
      git add .
      git commit -m "feat: add new censoring algorithm"
      git commit -m "fix: resolve audio sync issue"
      git commit -m "docs: update installation guide"

5. **Push and Create Pull Request**
   
   .. code-block:: bash
   
      git push origin feature/your-feature-name
   
   Then create a pull request on GitHub.

Code Style Guidelines
---------------------

- **Python Style**: Follow PEP 8, enforced by Black and flake8
- **Line Length**: 88 characters (Black default)
- **Import Sorting**: Use isort for consistent import organization
- **Type Hints**: Add type hints for new functions and methods
- **Docstrings**: Use Google-style docstrings for all public functions

Testing Guidelines
------------------

- **Write Tests**: All new features should include tests
- **Test Coverage**: Aim for high test coverage on new code
- **Test Types**: 
  - Unit tests for individual functions
  - Integration tests for complete workflows
  - CLI tests for command-line interface

- **Test Structure**:
  
  .. code-block:: python
  
     def test_function_name():
         """Test description."""
         # Arrange
         input_data = "test input"
         
         # Act
         result = function_to_test(input_data)
         
         # Assert
         assert result == expected_output

Documentation Guidelines
------------------------

- **Update Documentation**: Update relevant documentation for new features
- **Docstrings**: All public functions need docstrings
- **Examples**: Include usage examples in docstrings
- **README**: Update README.md if adding new functionality

Reporting Issues
----------------

When reporting bugs or requesting features:

1. **Check Existing Issues**: Search existing issues first
2. **Use Templates**: Use the provided issue templates
3. **Provide Details**: Include:
   - Python version
   - Operating system
   - FFmpeg version
   - Steps to reproduce
   - Expected vs actual behavior

Pull Request Process
--------------------

1. **Description**: Provide a clear description of changes
2. **Link Issues**: Reference related issues with "Fixes #123"
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update documentation if needed
5. **Review**: Address feedback from code review

Release Process
---------------

For maintainers:

1. **Update Version**: Update version in ``pyproject.toml``
2. **Update Changelog**: Add entry to ``CHANGELOG.md``
3. **Create Release**: Use GitHub Actions release workflow
4. **Verify**: Check that PyPI package is published correctly

Getting Help
------------

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the documentation first

Thank you for contributing to Dialogue Guardian! 🎉