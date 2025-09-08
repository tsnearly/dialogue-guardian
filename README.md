# Dialogue Guardian

[![CI/CD Pipeline](https://github.com/tsnearly/dialogue-guardian/actions/workflows/ci.yml/badge.svg)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/ci.yml)
[![PyPI Package](https://github.com/tsnearly/dialogue-guardian/actions/workflows/publish.yml/badge.svg)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/publish.yml)
[![Tests](https://github.com/tsnearly/dialogue-guardian/actions/workflows/test.yml/badge.svg)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/tsnearly/dialogue-guardian/branch/main/graph/badge.svg)](https://codecov.io/gh/tsnearly/dialogue-guardian)
[![PyPI version](https://img.shields.io/pypi/v/dialogue-guardian.svg)](https://pypi.org/project/dialogue-guardian/)
[![Python versions](https://img.shields.io/pypi/pyversions/dialogue-guardian.svg)](https://pypi.org/project/dialogue-guardian/)
[![Downloads](https://img.shields.io/pypi/dm/dialogue-guardian.svg)](https://pypi.org/project/dialogue-guardian/)
[![License](https://img.shields.io/github/license/tsnearly/dialogue-guardian.svg)](https://github.com/tsnearly/dialogue-guardian/blob/main/LICENSE)
[![Code Quality](https://github.com/tsnearly/dialogue-guardian/actions/workflows/quality.yml/badge.svg)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/quality.yml)
[![Security Scan](https://github.com/tsnearly/dialogue-guardian/actions/workflows/security.yml/badge.svg)](https://github.com/tsnearly/dialogue-guardian/actions/workflows/security.yml)

<p align="center">
  <img src="logo.png" alt="Dialogue Guardian Logo" width="200">
</p>

**Universal Media Censor** - Automatically detect and censor profane language in video files using subtitle analysis and FFmpeg audio processing.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install dialogue-guardian

# Censor a video file
guardian movie.mp4

# Output: movie_censored.mp4
```

## ✨ Features

- **🎯 Direct Audio Censoring**: Uses FFmpeg to mute profane segments in video files
- **🌍 Universal Compatibility**: Works on Windows, macOS, and Linux
- **🔄 Automatic SRT Extraction**: Extracts embedded subtitles when external SRT files aren't available
- **⚡ Efficient Processing**: Copies video streams without re-encoding to maintain quality
- **🛡️ Non-Destructive**: Creates new censored files, leaving originals untouched
- **📦 Easy Installation**: Available as a Python package with CLI and API interfaces
- **🎬 FCPX Support**: Legacy support for Final Cut Pro XML generation

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
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/tsnearly/dialogue-guardian.git
cd dialogue-guardian
make install-dev
```

## 💻 Usage

### Command Line Interface

```bash
# Basic usage
guardian movie.mp4

# Custom output path
guardian movie.mp4 --output censored_movie.mp4

# Verbose logging
guardian movie.mp4 --verbose

# Custom FFmpeg paths
guardian movie.mp4 --ffmpeg-path /usr/local/bin/ffmpeg
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

## 📚 Documentation

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

This project is licensed under the MIT License - see the [LICENSE](dialogue-guardian/LICENSE) file for details.

## 👨‍💻 Author

**Tony Snearly**

## 🙏 Acknowledgments

- FFmpeg team for the powerful multimedia framework
- Python community for excellent tooling and libraries

---

<p align="center">
  <strong>⭐ Star this repository if you find it helpful!</strong>
</p>
