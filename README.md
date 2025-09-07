<p align="center"><img src="logo.png" alt="Dialogue Guardian Logo" width="200"></p>

# Dialogue Guardian: Universal Media Censor

This project provides two Python scripts to automatically detect and censor profane language in video files by processing SRT subtitle files.

- **`guardian_by_ffmpeg.py` (Recommended)**: A standalone, cross-platform tool that directly censors audio using FFmpeg.
- **`guardian.py` (Legacy)**: A tool that generates a Final Cut Pro XML (`.fcpxml`) file with volume keyframes to mute profane segments.

---

## `guardian_by_ffmpeg.py` (Recommended Workflow)

This script provides a modern, streamlined solution that directly creates a censored video file without requiring any video editing software.

### Key Features

- **Direct Audio Censoring**: Uses FFmpeg's audio filters to mute profane segments and create a new, censored video file.
- **Universal Compatibility**: Works on any OS with FFmpeg installed (Windows, macOS, Linux).
- **No FCPX Dependency**: Does not require Final Cut Pro.
- **Automatic SRT Extraction**: If an external SRT file isn't found, it automatically extracts embedded SRT tracks from the video.
- **Non-Destructive**: Creates a new video file, leaving the original untouched.
- **Efficient**: Copies the video stream without re-encoding to maintain quality, only re-encoding the audio.

### Requirements

- **Python 3.7+**
- **FFmpeg**: Installed and accessible in your system's PATH.
- **Python Packages**: `pip install -r requirements.txt`

### Usage

1. **Run the script:**
   ```sh
   python guardian_by_ffmpeg.py <path_to_your_video_file>
   ```
   Example:
   ```sh
   python guardian_by_ffmpeg.py movie.mp4
   ```

2. **Output:**
   - A new censored video file will be created (e.g., `movie_censored.mp4`).
   - A log file (`guardian_by_ffmpeg.log`) will be created with detailed processing information.

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

## Testing

This project includes a full suite of unit tests. For detailed instructions on how to run the tests, please see [TESTING.md](TESTING.md).

---

## License

This project is provided as-is, without warranty. You may modify and distribute as needed.

---

## Author

Created by Tony Snearly.