# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
.PHONY: help install install-dev test test-verbose clean build upload lint format check docs docs-serve docs-clean docs-build docs-auto

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  test-verbose Run tests with verbose output"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black"
	@echo "  check        Run all checks (lint, format, test)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Build documentation (HTML)"
	@echo "  docs-serve   Build and serve documentation locally"
	@echo "  docs-clean   Clean documentation build files"
	@echo "  docs-build   Force rebuild all documentation"
	@echo "  docs-auto    Auto-rebuild docs on file changes"
	@echo ""
	@echo "Packaging:"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build the package"
	@echo "  upload       Upload to PyPI (requires credentials)"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install -r dev-requirements.txt

test:
	pytest

test-verbose:
	pytest -v -s

clean: docs-clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -f *.log
	rm -rf logs/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.tmp" -delete
	find . -type f -name "*.temp" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

lint:
	flake8 src/guardian/ tests/
	mypy src/guardian/

format:
	black src/guardian/ tests/ examples/ *.py

check: lint test docs
	@echo "All checks passed!"

# Documentation commands
docs:
	@echo "Building documentation..."
	cd docs && make html
	@echo "Documentation built successfully!"
	@echo "Open docs/_build/html/index.html to view"

docs-serve: docs
	@echo "Starting documentation server..."
	@echo "Documentation will be available at http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	cd docs/_build/html && python -m http.server 8000

docs-clean:
	@echo "Cleaning documentation build files..."
	cd docs && make clean
	rm -rf docs/_build/

docs-build: docs-clean docs
	@echo "Documentation rebuilt from scratch"

docs-auto:
	@echo "Starting auto-rebuild documentation server..."
	@echo "Documentation will auto-rebuild on file changes"
	@echo "Available at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	pip install sphinx-autobuild 2>/dev/null || echo "Installing sphinx-autobuild..."
	cd docs && sphinx-autobuild . _build/html --host 0.0.0.0 --port 8000