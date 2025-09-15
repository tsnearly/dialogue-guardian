"""
Setup configuration for the Guardian package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="dialogue-guardian",
    version="1.1.4",
    author="Tony Snearly",
    description="Universal Media Censor - Automatically detect and censor profane language in video files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tsnearly/dialogue-guardian",  # Update with actual URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing :: Filters",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "guardian=guardian.cli:main",
            "dialogue-guardian=guardian.cli:main",
        ],
    },
    keywords="video, audio, censoring, subtitles, ffmpeg, profanity, media",
    project_urls={
        "Bug Reports": "https://github.com/tsnearly/dialogue-guardian/issues",
        "Source": "https://github.com/tsnearly/dialogue-guardian",
    },
)