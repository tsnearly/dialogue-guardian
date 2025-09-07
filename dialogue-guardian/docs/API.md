# Dialogue Guardian API Documentation

## Overview

The Dialogue Guardian package provides both a command-line interface and a Python API for automatically detecting and censoring profane language in video files by processing SRT subtitle files.

## Python API

### GuardianProcessor Class

The main class for processing video files and censoring profane content.

#### Constructor

```python
from guardian import GuardianProcessor

processor = GuardianProcessor(
    matching_words=None,      # Optional: Custom list of words to censor
    ffmpeg_cmd='ffmpeg',      # Optional: Path to ffmpeg executable
    ffprobe_cmd='ffprobe'     # Optional: Path to ffprobe executable
)
```

**Parameters:**
- `matching_words` (List[str], optional): Custom list of words/phrases to censor. If None, uses the default profanity list.
- `ffmpeg_cmd` (str): Path to the ffmpeg executable. Defaults to 'ffmpeg'.
- `ffprobe_cmd` (str): Path to the ffprobe executable. Defaults to 'ffprobe'.

#### Methods

##### `process_video(video_path, output_path=None)`

Main method to process a video file and create a censored version.

```python
result = processor.process_video("movie.mp4", "censored_movie.mp4")
```

**Parameters:**
- `video_path` (str): Path to the input video file.
- `output_path` (str, optional): Path for the output censored video. If None, generates a default name with "_censored" suffix.

**Returns:**
- `str`: Path to the censored video file if successful, `None` if processing failed.

##### `get_video_details(filename)`

Extracts video and audio details using ffprobe.

```python
details = processor.get_video_details("movie.mp4")
print(f"Duration: {details['duration']} seconds")
print(f"Resolution: {details['width']}x{details['height']}")
```

**Parameters:**
- `filename` (str): Path to the video file.

**Returns:**
- `dict`: Dictionary containing video metadata:
  - `duration`: Video duration in seconds
  - `width`, `height`: Video resolution
  - `fps`: Frames per second
  - `codec`: Audio codec
  - `samplerate`: Audio sample rate
  - `channels`: Number of audio channels

##### `extract_embedded_srt(video_path, output_srt_path)`

Extracts embedded SRT subtitle tracks from a video file.

```python
success = processor.extract_embedded_srt("movie.mp4", "extracted.srt")
```

**Parameters:**
- `video_path` (str): Path to the input video file.
- `output_srt_path` (str): Path where the extracted SRT file will be saved.

**Returns:**
- `bool`: True if extraction was successful, False otherwise.

##### `censor_audio_with_ffmpeg(video_path, output_path=None)`

Censors profane audio segments in a video file using FFmpeg.

```python
censored_file = processor.censor_audio_with_ffmpeg("movie.mp4", "clean_movie.mp4")
```

**Parameters:**
- `video_path` (str): Path to the input video file.
- `output_path` (str, optional): Custom output path. If None, generates default name.

**Returns:**
- `str`: Path to the censored video file if successful, `None` if processing failed.

## Usage Examples

### Basic Usage

```python
from guardian import GuardianProcessor

# Initialize with default settings
processor = GuardianProcessor()

# Process a video file
result = processor.process_video("movie.mp4")

if result:
    print(f"Censored video created: {result}")
else:
    print("Processing failed")
```

### Custom Configuration

```python
from guardian import GuardianProcessor

# Custom profanity list
custom_words = ['bad', 'worse', 'terrible']

# Custom FFmpeg paths
processor = GuardianProcessor(
    matching_words=custom_words,
    ffmpeg_cmd='/usr/local/bin/ffmpeg',
    ffprobe_cmd='/usr/local/bin/ffprobe'
)

# Process with custom output path
result = processor.process_video(
    video_path="input.mp4",
    output_path="output/clean_video.mp4"
)
```

### Video Analysis

```python
from guardian import GuardianProcessor

processor = GuardianProcessor()

# Get detailed video information
details = processor.get_video_details("movie.mp4")

if details:
    print(f"Video Duration: {details['duration']} seconds")
    print(f"Resolution: {details['width']}x{details['height']}")
    print(f"Frame Rate: {details['fps']} fps")
    print(f"Audio Codec: {details['codec']}")
    print(f"Sample Rate: {details['samplerate']} Hz")
    print(f"Audio Channels: {details['channels']}")
```

### Subtitle Extraction

```python
from guardian import GuardianProcessor

processor = GuardianProcessor()

# Extract embedded subtitles
success = processor.extract_embedded_srt("movie.mp4", "subtitles.srt")

if success:
    print("Subtitles extracted successfully")
    
    # Now process the video with the extracted subtitles
    result = processor.process_video("movie.mp4")
```

### Error Handling

```python
from guardian import GuardianProcessor
import logging

# Enable logging to see detailed error messages
logging.basicConfig(level=logging.INFO)

processor = GuardianProcessor()

try:
    result = processor.process_video("movie.mp4")
    
    if result:
        print(f"Success: {result}")
    else:
        print("Processing failed - check logs for details")
        
except FileNotFoundError:
    print("Video file not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Command Line Interface

### Basic Usage

```bash
# Process a video file
guardian movie.mp4

# Specify output path
guardian movie.mp4 --output clean_movie.mp4

# Enable verbose logging
guardian movie.mp4 --verbose

# Custom log file
guardian movie.mp4 --log-file processing.log
```

### Advanced Options

```bash
# Custom FFmpeg paths
guardian movie.mp4 \
    --ffmpeg-path /usr/local/bin/ffmpeg \
    --ffprobe-path /usr/local/bin/ffprobe

# All options combined
guardian movie.mp4 \
    --output clean_movie.mp4 \
    --verbose \
    --log-file detailed.log \
    --ffmpeg-path /usr/local/bin/ffmpeg
```

### Help and Version

```bash
# Show help
guardian --help

# Show version
guardian --version
```

## Configuration

### Default Profanity List

The package includes a comprehensive default list of profane words and phrases. You can view or modify this list:

```python
from guardian import GuardianProcessor

processor = GuardianProcessor()
print("Default profanity list:")
for word in processor.matching_words:
    print(f"  - {word}")
```

### Custom Word Lists

```python
# Load from file
def load_word_list(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

custom_words = load_word_list('my_profanity_list.txt')
processor = GuardianProcessor(matching_words=custom_words)
```

### FFmpeg Configuration

The package requires FFmpeg and FFprobe to be installed. You can specify custom paths:

```python
# For custom installations
processor = GuardianProcessor(
    ffmpeg_cmd='/opt/ffmpeg/bin/ffmpeg',
    ffprobe_cmd='/opt/ffmpeg/bin/ffprobe'
)
```

## Supported File Formats

### Video Formats
- MP4 (recommended)
- AVI
- MOV
- MKV
- Any format supported by FFmpeg

### Subtitle Formats
- SRT (SubRip) - external files
- Embedded SRT tracks in video files
- Language-specific SRT files (e.g., `movie.en.srt`, `movie.fr.srt`)

## Requirements

- Python 3.7+
- FFmpeg and FFprobe installed and accessible in PATH
- Required Python packages (automatically installed):
  - srt2

## Error Handling

The API provides comprehensive error handling:

- **FileNotFoundError**: When video files or FFmpeg executables are not found
- **subprocess.CalledProcessError**: When FFmpeg commands fail
- **json.JSONDecodeError**: When FFprobe output cannot be parsed
- **Exception**: General error handling for unexpected issues

All errors are logged with detailed information to help with debugging.

## Performance Considerations

- **Video Copying**: The video stream is copied without re-encoding for maximum quality and speed
- **Audio Re-encoding**: Only the audio is re-encoded to apply censoring filters
- **Memory Usage**: Processing is done in streaming mode to handle large video files
- **Temporary Files**: SRT files may be temporarily extracted and should be cleaned up automatically

## Limitations

- Requires subtitle files (SRT) to identify profane content
- Only censors audio based on subtitle timing
- Cannot detect profanity in audio without corresponding subtitles
- FFmpeg must be installed separately