# Dialoque Guardian: Universal Media Censor
This project provides a powerful and accessible Python application designed to automatically detect and censor profane language in video files. Leveraging the robust capabilities of FFmpeg, Guardian now offers a streamlined, platform-independent solution, eliminating the previous reliance on Apple's Final Cut Pro.

## Key Features:
Automated Profanity Detection: Scans subtitle tracks (SRT) for a predefined list of offensive words and phrases.

Direct Audio Censoring: Utilizes FFmpeg's audio filters to precisely mute or reduce the volume of identified profane segments, creating a new, censored video file.

Universal Compatibility:

No FCP Dependency: The tool no longer requires Final Cut Pro, making it usable on any operating system where FFmpeg is installed (Windows, macOS, Linux).

FFmpeg-Centric Workflow: All media processing is handled directly by FFmpeg, a free and open-source command-line tool.

Automatic SRT Extraction: If an external SRT subtitle file is not found, the application will automatically attempt to extract embedded SRT tracks from the video file (e.g., from MKV containers), ensuring a comprehensive subtitle source.

Non-Destructive Editing: Creates a new video file with censored audio, leaving the original media untouched.

Efficient Processing: Copies the video stream directly to avoid re-encoding and maintain original video quality, focusing re-encoding only on the audio stream.

## How it Works:
The user provides a path to a video file (e.g., an MKV or MP4).

The script first looks for an external SRT file with the same base name.

If no external SRT is found, it uses ffprobe to detect and ffmpeg to extract any embedded SRT subtitle tracks from the video.

It then parses the SRT content, identifying time segments that contain words from its internal profanity list.

Finally, it constructs and executes an FFmpeg command that applies a volume filter to mute the audio during these identified time segments, outputting a new, censored video file.

Guardian aims to provide a simple, effective, and universally available tool for content creators and consumers to manage explicit language in their media.

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
