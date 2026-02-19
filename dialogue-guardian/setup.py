# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Setup configuration for the Guardian package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

setup(
    name="dialogue-guardian",
    version="1.3.1",
    author="Tony Snearly",
    description="Universal Media Censor - Automatically detect and censor profane language in video files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tsnearly/dialogue-guardian",  # Update with actual URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: Open Software License 3.0 (OSL-3.0)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Text Processing :: Filters",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Pytest",
        "Framework :: Sphinx",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "guardian=guardian.cli:main",
            "dialogue-guardian=guardian.cli:main",
        ],
    },
    keywords="video, audio, censoring, subtitles, ffmpeg, profanity, media",
    project_urls={
        "Homepage" = "https://github.com/tsnearly/dialogue-guardian",
        "Documentation" = "https://dialogue-guardian.readthedocs.io/en/latest/",
        "Repository" = "https://github.com/tsnearly/dialogue-guardian.git",
        "Source" = "https://github.com/tsnearly/dialogue-guardian",
        "Issues" = "https://github.com/tsnearly/dialogue-guardian/issues",
        "Changelog" = "https://tsnearly.github.io/dialogue-guardian/changelog.html",
    },
)
