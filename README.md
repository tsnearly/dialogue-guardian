# Dialogue Guardian

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tsnearly/dialogue-guardian/ci.yml?style=plastic)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/tsnearly/dialogue-guardian?token=0XIMSERI3U&style=plastic)](https://codecov.io/gh/tsnearly/dialogue-guardian)
[![PyPI - Version](https://img.shields.io/pypi/v/dialogue-guardian?style=plastic)](https://pypi.org/project/dialogue-guardian/)
[![Python versions](https://img.shields.io/pypi/pyversions/dialogue-guardian.svg)](https://pypi.org/project/dialogue-guardian/)
[![Downloads](https://img.shields.io/pypi/dm/dialogue-guardian.svg)](https://pypi.org/project/dialogue-guardian/)
[![License](https://img.shields.io/badge/license-OSL--3.0-blue.svg)](https://github.com/tsnearly/dialogue-guardian/blob/main/dialogue-guardian/LICENSE)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tsnearly/dialogue-guardian/quality.yml?style=plastic&label=Code%20Quality)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/quality.yml)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tsnearly/dialogue-guardian/security.yml?style=plastic&label=Security%20Scan)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/security.yml)

<p align="center">
  <img src="logo.png" alt="Dialogue Guardian Logo" width="200">
</p>

**Universal Media Censor** - Automatically detect and censor profane language in video files using subtitle analysis and FFmpeg audio processing.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install dialogue-guardian

# Censor a video file
guardian --input movie.mp4

# Output: movie_censored.mp4
```

## ✨ Features

- **🎯 Direct Audio Censoring**: Uses FFmpeg to mute profane segments in video files
- **🌍 Universal Compatibility**: Works on any OS with FFmpeg installed (Windows, macOS, Linux)
- **🔄 Automatic SRT Extraction**: If an external SRT file isn't found, it automatically extracts embedded SRT tracks from the video
- **🛡️ Non-Destructive**: Creates a new video file, leaving the original untouched
- **📦 Package Structure**: Properly structured as a Python package for easy installation and distribution
- **🎬 FCPX Support**: Legacy support available for Final Cut Pro XML generation, but does not require Final Cut Pro
- **📹 Efficient Processing**: Copies video streams without re-encoding to maintain quality
- **🎛 Enhanced Audio Censoring**: Advanced multi-strategy audio filtering system with progressive fallback mechanisms
- **📡 Silence Verification**: Automated verification that censored segments achieve target silence levels (≤ -50 dB)
- **🎚 Fallback Strategies**: Three-tier approach (Basic → Enhanced → Aggressive) ensures effective censoring
- **🎙 Quality Preservation**: Maintains video quality while achieving effective audio silence
- **🧰 Comprehensive Diagnostics**: Detailed logging and JSON diagnostic reports for troubleshooting
- **🏷 Robust Error Handling**: Graceful handling of missing files, corrupted data, and processing failures

## 📋 Requirements

- **Python 3.7+**
- **FFmpeg** (must be installed and accessible in PATH)

## 🛠️ Installation

### From PyPI (Recommended)

```bash
pip install dialogue-guardian
```

### From Source

```bash
git clone https://github.com/tsnearly/dialogue-guardian.git
cd dialogue-guardian
pip install -e .   or   uv sync
```

### Development Installation

```bash
git clone https://github.com/tsnearly/dialogue-guardian.git
cd dialogue-guardian
make install-dev   or   uv sync --group dev
```

## 💻 Usage

### Command Line Interface

```bash
# Basic usage
guardian --input movie.mp4

# Custom output path
guardian --input movie.mp4 --output censored_movie.mp4

# Verbose logging
guardian --input movie.mp4 --verbose

# Custom FFmpeg paths
guardian --input movie.mp4 --ffmpeg-path /usr/local/bin/ffmpeg
 - `--full` : When set, run the full (and slower) verification path which performs per-segment audio analysis using FFmpeg astats, produces a comprehensive diagnostic report, and allows multiple fallback attempts to improve censoring. Default: disabled (fast path). Use `--full` when you want maximum assurance at the cost of slower runs.
```

### Python API

```python
from guardian import GuardianProcessor

# Initialize processor
processor = GuardianProcessor()

# Process video
censored_file = processor.process_video("movie.mp4")

if censored_file:
    print(f"Censored video created: {censored_file}")
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test
pytest tests/test_guardian_core.py -v
```

### 📈 Current code coverage

[![CoverageGraph](https://codecov.io/gh/tsnearly/dialogue-guardian/graphs/icicle.svg?token=0XIMSERI3U)](https://codecov.io/gh/tsnearly/dialogue-guardian)

## 🏗️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/tsnearly/dialogue-guardian.git
cd dialogue-guardian
make install-dev

# Run quality checks
make lint
make format
make check
```

### Building and Publishing

```bash
# Build package
make build

# Upload to PyPI
make upload
```

## Releases

[![GitHub Release Date](https://img.shields.io/github/release-date/tsnearly/dialogue-guardian?display_date=published_at&style=plastic)](https://github.com/tsnearly/dialogue-guardian/releases)
[![GitHub Downloads (specific asset, latest release)](https://img.shields.io/github/downloads/tsnearly/dialogue-guardian/v1.3.1/dialogue-guardian-1.3.1.tar.gz?sort=semver&style=plastic)](https://github.com/tsnearly/dialogue-guardian/releases/download/v1.3.1/dialogue-guardian-1.3.1.tar.gz)

## 📚 Documentation

- **[📖 Full Documentation](https://tsnearly.github.io/dialogue-guardian/)** - Complete documentation on GitHub Pages
- [Development Guide](dialogue-guardian/DEVELOPMENT.md)
- [Testing Documentation](dialogue-guardian/TESTING.md)
- [Migration Summary](dialogue-guardian/MIGRATION_SUMMARY.md)
- [Project Completion Summary](dialogue-guardian/PROJECT_COMPLETION_SUMMARY.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Open Software License version 3.0 - see the [LICENSE](dialogue-guardian/LICENSE) file for details.

## 👨‍💻 Author

**Tony Snearly**

## 🙏 Acknowledgments

- FFmpeg team for the powerful multimedia framework
- Python community for excellent tooling and libraries

---

<p align="center">
  <strong>⭐ Star this repository if you find it helpful!</strong>
</p>
