# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Pytest configuration and fixtures.
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def download_ffmpeg_fixture(request):
    """
    Fixture to run the FFmpeg download script before any tests run.
    This is a session-scoped fixture that runs automatically.
    """
    # Only run this on the master node in a distributed testing environment
    if not hasattr(request.config, "workerinput"):
        script_path = Path(__file__).parent.parent / "scripts" / "download_ffmpeg.py"
        print(f"\nRunning FFmpeg download script: {script_path}")

        # Use the same Python executable that is running pytest
        python_executable = sys.executable
        result = subprocess.run(
            [python_executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if "skipping download" not in result.stdout.lower():
            print("--- FFmpeg Download Script STDOUT ---")
            print(result.stdout)

        if result.returncode != 0:
            print("--- FFmpeg Download Script STDERR ---")
            print(result.stderr)
            pytest.fail(
                "The FFmpeg download script failed. Halting tests.", pytrace=False
            )

        print("FFmpeg setup is complete.")
