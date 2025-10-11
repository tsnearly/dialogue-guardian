<p align="center"><img src="logo.png" alt="Dialogue Guardian Logo" width="200"></p>

# Dialogue Guardian: Universal Media Censor

This project provides two Python scripts to automatically detect and censor profane language in video files by processing SRT subtitle files.

- **`guardian_by_ffmpeg.py` (Recommended)**: A standalone, cross-platform tool that directly censors audio using FFmpeg.
- **`guardian.py` (Legacy)**: A tool that generates a Final Cut Pro XML (`.fcpxml`) file with volume keyframes to mute profane segments.

---

## Installation

### From PyPI (when published)
```sh
pip install dialogue-guardian
```

### From Source
```sh
git clone <repository-url>
cd dialogue-guardian
pip install -e .
```

### Development Installation
```sh
git clone <repository-url>
cd dialogue-guardian
make install-dev
```

## Usage

### Command Line Interface

After installation, you can use the `guardian` command:

```sh
# Basic usage
guardian movie.mp4

# With custom output path
guardian movie.mp4 --output censored_movie.mp4

# With verbose logging
guardian movie.mp4 --verbose

# Custom FFmpeg paths
guardian movie.mp4 --ffmpeg-path /usr/local/bin/ffmpeg --ffprobe-path /usr/local/bin/ffprobe
```

### Python API

```python
from guardian import GuardianProcessor

# Initialize the processor
processor = GuardianProcessor()

# Process a video file with enhanced censoring
censored_file = processor.censor_audio_with_ffmpeg("movie.mp4", "censored_movie.mp4")

if censored_file:
    print(f"Censored video created: {censored_file}")
    
    # Check diagnostic files for detailed results
    import glob
    diagnostic_files = glob.glob("*_diagnostic_*.json")
    if diagnostic_files:
        print(f"Diagnostic report: {diagnostic_files[-1]}")
else:
    print("Processing failed")

# Custom configuration with enhanced features
processor = GuardianProcessor(
    matching_words=['custom', 'word', 'list'],
    ffmpeg_cmd='/usr/local/bin/ffmpeg',
    ffprobe_cmd='/usr/local/bin/ffprobe'
)

# Get video details
details = processor.get_video_details("movie.mp4")
print(f"Video duration: {details['duration']}s")
print(f"Resolution: {details['width']}x{details['height']}")
```

### Key Features

- **Enhanced Audio Censoring**: Advanced multi-strategy audio filtering system with progressive fallback mechanisms
- **Silence Verification**: Automated verification that censored segments achieve target silence levels (≤ -50 dB)
- **Fallback Strategies**: Three-tier approach (Basic → Enhanced → Aggressive) ensures effective censoring
- **Universal Compatibility**: Works on any OS with FFmpeg installed (Windows, macOS, Linux)
- **No FCPX Dependency**: Does not require Final Cut Pro
- **Automatic SRT Extraction**: If an external SRT file isn't found, it automatically extracts embedded SRT tracks from the video
- **Non-Destructive**: Creates a new video file, leaving the original untouched
- **Quality Preservation**: Maintains video quality while achieving effective audio silence
- **Comprehensive Diagnostics**: Detailed logging and JSON diagnostic reports for troubleshooting
- **Robust Error Handling**: Graceful handling of missing files, corrupted data, and processing failures
- **Package Structure**: Properly structured as a Python package for easy installation and distribution

### Requirements

- **Python 3.7+**
- **FFmpeg**: Installed and accessible in your system's PATH.
- **Python Packages**: Automatically installed with the package

---

## `guardian.py` (Legacy FCPXML Workflow)

This script is for users who want to import a censorship timeline into Apple's Final Cut Pro.

### Features

- **FCPXML Generation**: Outputs a ready-to-import XML file for Final Cut Pro with volume keyframes to mute profanity.
- **Metadata Extraction**: Uses `ffprobe` to get video details for the FCPXML project.
- **Subtitle Parsing**: Reads an external `.srt` file to find profane words.

### Requirements

- **Python 3.7+**
- **ffprobe** (part of FFmpeg): The script defaults to `/Users/Shared/FFmpegTools/ffprobe`, but you can edit the path in the script.

### Usage

1. **Prepare your files:**
   - Place your video file (e.g., `movie.mp4`) and its subtitle file (`movie.srt`) in the same directory.

2. **Run the script:**
   ```sh
   python guardian.py <path_to_your_video_file>
   ```
   Example:
   ```sh
   python guardian.py movie.mp4
   ```

3. **Output:**
   - A Final Cut Pro XML file (`movie.fcpxml`) will be generated.
   - A log file (`guardian.log`) will be created.

---

## Customization

To customize the list of censored words, edit the `matching_words` list at the top of either `guardian.py` or `guardian_by_ffmpeg.py`.

---

## Development

### Running Tests

```sh
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run specific test file
pytest tests/test_guardian_core.py
```

### Code Quality

```sh
# Format code
make format

# Run linting
make lint

# Run all checks
make check
```

### Building and Publishing

```sh
# Build the package
make build

# Upload to PyPI (requires credentials)
make upload
```

## Testing

This project includes a full suite of unit tests. For detailed instructions on how to run the tests, please see [TESTING.md](TESTING.md).

---

## License

This project is licensed under the Open Software License version 3.0 - see the [LICENSE](LICENSE) file for details.

---

## Author

Created by Tony Snearly.