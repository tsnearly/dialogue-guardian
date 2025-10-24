# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Pytest configuration and fixtures.
"""

import shutil
import subprocess

import pytest


@pytest.fixture(scope="session", autouse=True)
def verify_ffmpeg_available(request):
    """
    Fixture to verify that FFmpeg and ffprobe are available before tests run.
    This is a session-scoped fixture that runs automatically.

    FFmpeg should be installed via the system package manager (apt-get, brew, choco, etc.)
    or available in PATH. The download_ffmpeg.py script is no longer used during CI tests.
    """
    # Only run this on the master node in a distributed testing environment
    if not hasattr(request.config, "workerinput"):
        print("\nVerifying FFmpeg availability...")

        # Check if ffmpeg is available in PATH
        ffmpeg_available = shutil.which("ffmpeg") is not None
        ffprobe_available = shutil.which("ffprobe") is not None

        if ffmpeg_available:
            print("✓ FFmpeg found in PATH")
        else:
            print("✗ FFmpeg not found in PATH")

        if ffprobe_available:
            print("✓ ffprobe found in PATH")
        else:
            print("✗ ffprobe not found in PATH")

        if not (ffmpeg_available and ffprobe_available):
            pytest.fail(
                "FFmpeg and/or ffprobe are not available. "
                "Please install FFmpeg using your system package manager "
                "(apt-get on Ubuntu, brew on macOS, choco on Windows).",
                pytrace=False,
            )

        # Verify they actually work
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                print("✓ FFmpeg executable works correctly")
            else:
                pytest.fail("FFmpeg executable exists but failed to run", pytrace=False)
        except Exception as e:
            pytest.fail(f"Failed to run FFmpeg: {e}", pytrace=False)

        print("FFmpeg verification complete.")
