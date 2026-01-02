# Dialogue Guardian Setup Guide for Windows

## Complete Step-by-Step Instructions for Fresh Installation

This guide is designed for users with no prior Python or programming experience. Follow each step carefully in order.

---

## What is Dialogue Guardian?

Dialogue Guardian is a tool that automatically finds and censors profanity in video files. It:

- Takes a video file as input
- Analyzes subtitles to find profanity
- Removes/mutes the offensive audio
- Creates a clean version of your video

**Supported video formats:** MP4, AVI, MOV, MKV, and most other common video formats.

---

## Part 1: Install Python

Python is a programming language that Dialogue Guardian needs to run.

### Step 1: Download Python

1. Open your web browser and go to: **https://www.python.org/downloads/windows/**
2. Click the large yellow **"Download Python 3.x.x"** button (version 3.11 or higher recommended)
3. A file named something like `python-3.11.x-amd64.exe` will download

### Step 2: Install Python

1. **Find the downloaded file** - Usually in your Downloads folder, named `python-3.11.x-amd64.exe` (or similar)
2. **Double-click** the installer to open it
3. **IMPORTANT: Check this box:**
   - Look for the checkbox that says **"Add Python to PATH"** ✓ (make sure it's checked)
   - This allows Windows to find Python easily
4. Click **"Install Now"**
5. Wait for installation to complete (may take 1-2 minutes)
6. When complete, click **"Close"**

### Step 3: Verify Python Installation

1. Press the **Windows key** and type: `cmd`
2. Click **"Command Prompt"** to open it
3. Type this command and press Enter:
   ```
   python --version
   ```
4. You should see something like: `Python 3.11.x`
   - If you see this, Python is installed correctly ✓
   - If you see an error, go back and make sure you checked "Add Python to PATH"

---

## Part 2: Install FFmpeg

FFmpeg is software that processes video and audio. Dialogue Guardian needs it to work.

### Step 1: Download FFmpeg

1. Open your web browser and go to: **https://ffmpeg.org/download.html**
2. Click the **Windows link** under "Get packages & executable files"
3. Look for a link that says something like **"ffmpeg-release-full.7z"** or **"ffmpeg-git-full.7z"**
   - Download this file (it's about 80-100 MB)

### Step 2: Extract FFmpeg

1. **Find the downloaded file** - Usually named `ffmpeg-release-full.7z` (or similar) in Downloads
2. **Right-click** the file and select **"Extract All..."** (if you have WinRAR or 7-Zip installed)
   - If you don't have extraction software, download and install **7-Zip** first:
     - Go to https://www.7-zip.org/
     - Download and install it
     - Then extract the FFmpeg file
3. A folder will be created, typically named `ffmpeg-xxx`
4. **Inside this folder**, navigate to the **`bin` folder**
5. You should see three files:
   - `ffmpeg.exe`
   - `ffprobe.exe`
   - `ffplay.exe`

### Step 3: Create a Folder for FFmpeg

We'll create a permanent location for FFmpeg on your computer.

1. Open **File Explorer** (Windows key + E)
2. Navigate to **C:\ drive** (usually shows as "Local Disk (C:)" on the left)
3. Right-click in empty space and select **"New" → "Folder"**
4. Name it: `ffmpeg`
5. Open the new `ffmpeg` folder
6. Copy the three files (`ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe`) from the extracted FFmpeg folder into this new folder
   - Tip: You can drag and drop them, or copy (Ctrl+C) and paste (Ctrl+V)

### Step 4: Add FFmpeg to Windows PATH

This tells Windows where to find FFmpeg.

1. Right-click **"This PC"** or **"My Computer"** on the desktop (or in File Explorer left sidebar)
2. Select **"Properties"**
3. Click **"Advanced system settings"** (on the left side)
4. Click the **"Environment Variables"** button (bottom right)
5. In the window that opens, click **"Path"** in the lower section (System variables)
6. Click **"Edit"**
7. Click **"New"** and type: `C:\ffmpeg`
8. Click **"OK"** three times to close all windows
9. **Restart your computer** for the changes to take effect

### Step 5: Verify FFmpeg Installation

1. Press **Windows key** and type: `cmd`
2. Click **"Command Prompt"**
3. Type this command and press Enter:
   ```
   ffmpeg -version
   ```
4. You should see version information and copyright details
   - If you see this, FFmpeg is installed correctly ✓
   - If you see an error, restart your computer and try again

---

## Part 3: Install Dialogue Guardian

Now that Python and FFmpeg are ready, we can install Dialogue Guardian.

### Step 1: Open Command Prompt

1. Press the **Windows key** and type: `cmd`
2. Click **"Command Prompt"** to open it

### Step 2: Install Dialogue Guardian

Type this command and press Enter:

```
pip install dialogue-guardian
```

This will download and install Dialogue Guardian automatically. It may take 1-2 minutes.

You should see something like:

```
Successfully installed dialogue-guardian-1.3.0
```

---

## Part 4: How to Use Dialogue Guardian

### Basic Usage

1. Open **Command Prompt** (Windows key → type `cmd` → press Enter)
2. Navigate to where your video file is located. For example:

   ```
   cd C:\Users\YourName\Videos
   ```

   (Replace `YourName` with your actual Windows username)

3. Run the command:

   ```
   guardian --input your_video.mp4
   ```

   (Replace `your_video.mp4` with your actual filename)

4. Wait for processing to complete (may take several minutes depending on video length)
5. A new file called `your_video_censored.mp4` will be created in the same folder

### Example Commands

**Example 1: Basic censoring**

```
guardian --input movie.mp4
```

Creates: `movie_censored.mp4`

**Example 2: Custom output filename**

```
guardian --input movie.mp4 --output cleaned_movie.mp4
```

Creates: `cleaned_movie.mp4`

**Example 3: Show detailed information (for troubleshooting)**

```
guardian --input movie.mp4 --verbose
```

**Example 4: Using the full verification system (slower but more thorough)**

```
guardian --input movie.mp4 --full
```

---

## Troubleshooting

### Problem: "python: command not found"

**Solution:**

1. Go back to Part 1, Step 2
2. Make sure you checked "Add Python to PATH" during installation
3. If you already installed Python without checking this box, uninstall it and reinstall with that box checked
4. Restart your computer

### Problem: "ffmpeg: command not found"

**Solution:**

1. Go back to Part 2, Step 5
2. Make sure you restarted your computer after adding FFmpeg to PATH
3. Try the verification command again

### Problem: "guardian: command not found"

**Solution:**

1. Make sure Python is installed and working (test with `python --version`)
2. Try installing again: `pip install dialogue-guardian`
3. Close and reopen Command Prompt
4. Try again

### Problem: Command Prompt can't find my video file

**Solution:**

1. Make sure you're in the correct folder where the video is stored
2. Use `cd` command to change directories, for example:
   ```
   cd C:\Users\YourName\Downloads
   ```
3. To see files in the current folder, type: `dir`
4. Make sure your filename is typed exactly as it appears (including the file extension like `.mp4`)

### Problem: Processing takes a very long time or freezes

**Solution:**

1. This is normal for large video files (processing can take 30 minutes to several hours)
2. Don't close the Command Prompt window - let it continue
3. For faster processing on large files, try without the `--full` flag first

### Problem: Error message about missing SRT file

**Solution:**

1. Dialogue Guardian looks for subtitles in your video
2. If no subtitles are found, it will try to extract them automatically
3. If the video has no subtitles at all, censoring cannot be performed
4. Make sure your video has embedded or external subtitle files

---

## Tips for Best Results

1. **Keep it simple:** Start with the basic command:

   ```
   guardian --input your_video.mp4
   ```

2. **Check your filenames:** Make sure the filename is spelled exactly right, including the extension (`.mp4`, `.avi`, etc.)

3. **Allow enough time:** Depending on video length, processing can take:

   - 10-15 minutes for 30-minute videos
   - 30+ minutes for full-length movies
   - Don't close the Command Prompt while processing

4. **Backup your files:** Always keep the original video file. Dialogue Guardian creates a new file and doesn't modify the original.

5. **Video requirements:** Your video should have:
   - Subtitles (embedded or external SRT file in the same folder)
   - Common video format (MP4, AVI, MOV, MKV, etc.)

---

## Getting Help

If you encounter problems:

1. **Check the error message** - Read what Command Prompt says carefully
2. **Try the troubleshooting section** above
3. **Visit the GitHub page:** https://github.com/tsnearly/dialogue-guardian
4. **Check the documentation:** The project has detailed information about all features

---

## Summary of What You Installed

| Component         | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| Python            | Programming language that runs Dialogue Guardian |
| FFmpeg            | Processes video and audio files                  |
| Dialogue Guardian | The tool that censors profanity in videos        |

---

## Quick Reference - Common Commands

After everything is installed, here are the most common commands:

```bash
# See if everything is installed correctly
python --version
ffmpeg -version
guardian --help

# Basic censoring
guardian --input movie.mp4

# With custom output name
guardian --input movie.mp4 --output clean_movie.mp4

# Verbose mode (shows more details)
guardian --input movie.mp4 --verbose

# Full verification (more thorough, slower)
guardian --input movie.mp4 --full
```

---

**Notes:**

- All commands are typed in Command Prompt
- Filenames and paths are case-sensitive on some systems, so be careful with spelling
- When typing file paths, you can drag the file into Command Prompt window to automatically fill in the path
- The original video file is never modified - a new file is always created

Good luck! If you have any questions, feel free to ask for clarification.
