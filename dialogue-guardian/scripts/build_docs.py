#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Documentation build script for Dialogue Guardian.

This script helps build and serve the Sphinx documentation.
"""

import sys
import subprocess
import webbrowser
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, check=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def build_docs(clean=False):
    """Build the documentation."""
    docs_dir = Path(__file__).parent.parent / "docs"

    if clean:
        print("Cleaning previous build...")
        success, stdout, stderr = run_command("make clean", cwd=docs_dir)
        if not success:
            print(f"Clean failed: {stderr}")
            return False

    print("Building documentation...")
    success, stdout, stderr = run_command("make html", cwd=docs_dir)

    if success:
        print("Documentation built successfully!")
        html_file = docs_dir / "_build" / "html" / "index.html"
        print(f"Documentation available at: file://{html_file.absolute()}")
        return True
    else:
        print(f"Build failed: {stderr}")
        return False


def serve_docs(port=8000):
    """Serve the documentation locally."""
    docs_dir = Path(__file__).parent.parent / "docs" / "_build" / "html"

    if not docs_dir.exists():
        print("Documentation not built. Building now...")
        if not build_docs():
            return False

    print(f"Starting documentation server on port {port}...")
    print(f"Documentation will be available at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")

    # Open browser
    webbrowser.open(f"http://localhost:{port}")

    # Start server
    try:
        subprocess.run([
            sys.executable, "-m", "http.server", str(port)
        ], cwd=docs_dir)
    except KeyboardInterrupt:
        print("\nServer stopped.")

    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build and serve Dialogue Guardian documentation")
    parser.add_argument("--clean", action="store_true", help="Clean build before building")
    parser.add_argument("--serve", action="store_true", help="Serve documentation after building")
    parser.add_argument("--port", type=int, default=8000, help="Port for serving (default: 8000)")

    args = parser.parse_args()

    if args.serve:
        serve_docs(args.port)
    else:
        build_docs(args.clean)


if __name__ == "__main__":
    main()
