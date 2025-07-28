# Censor

## Overview

`guardian.py` is a Python script designed to automate the process of generating Final Cut Pro XML (FCPXML) files for video projects. It scans a video and its corresponding subtitle file (`.srt`) for a list of predefined words and phrases, then creates an FCPXML file with automated audio volume keyframes to mute those words in the video. This is useful for quickly censoring inappropriate language or content in videos.

---

## Features

- **Automatic Video Metadata Extraction:** Uses `ffprobe` to extract video duration, frame rate, resolution, and audio configuration.
- **Subtitle Parsing:** Reads and cleans `.srt` subtitle files.
- **Censorship Logic:** Searches for a customizable list of words/phrases and generates mute keyframes in the FCPXML.
- **FCPXML Generation:** Outputs a ready-to-import XML file for Final Cut Pro, with all necessary resources and keyframes.
- **Logging:** Detailed logging to both console and `guardian.log` file.

---

## Requirements

- **Python 3.7+**
- **ffprobe** (part of [FFmpeg](https://ffmpeg.org/)), installed and accessible at the path specified in the script (`/Users/Shared/FFmpegTools/ffprobe` by default).
- No external Python packages required.

---

## Usage

1. **Prepare your files:**
   - Place your video file (e.g., `movie.mp4`) and its corresponding subtitle file (`movie.srt`) in the same directory.

2. **Run the script:**
   ```sh
   python guardian.py <videofile>
   ```
   Example:
   ```sh
   python guardian.py movie.mp4
   ```

3. **Output:**
   - The script will generate a Final Cut Pro XML file (`movie.fcpxml`) in the same directory.
   - A log file (`guardian.log`) will be created with detailed processing information.

---

## Customization

- **Censored Words/Phrases:**  
  Edit the `matching_words` list in `guardian.py` to add or remove words/phrases you consicer to be profane and want to clip the audio.

- **ffprobe Path:**  
  If your `ffprobe` binary is located elsewhere, update the path in the `get_video_details()` function.

---

## How It Works

1. **Extract Video Details:**  
   Uses `ffprobe` to get duration, frame rate, resolution, audio channels, and sample rate.

2. **Parse Subtitles:**  
   Reads the `.srt` file, cleans the text, and searches for matches against the `matching_words` list.

3. **Generate Keyframes:**  
   For each match, calculates the time range and adds mute/unmute keyframes to the FCPXML.

4. **Write FCPXML:**  
   Outputs a standards-compliant XML file for Final Cut Pro, version 1.9 of the DTD, ready for import.

---

## Troubleshooting

- **ffprobe Not Found:**  
  Make sure `ffprobe` is installed and the path in the script is correct.
- **Missing SRT File:**  
  The script expects a subtitle file with the same base name as the video.
- **No Output:**  
  Check `guardian.log` for errors and debug information.

---

## License

This project is provided as-is, without warranty.  
You may modify and distribute as needed.

---

## Author

Created by Tony Snearly.  
Feel free to contribute or suggest