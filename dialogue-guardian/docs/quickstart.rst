Quick Start Guide
=================

This guide will help you get started with Dialogue Guardian quickly.

Basic Usage
-----------

The simplest way to use Dialogue Guardian is with the command line interface:

.. code-block:: bash

   guardian movie.mp4

This will:

1. Look for a subtitle file (``movie.srt``) in the same directory
2. If no external subtitle file is found, attempt to extract embedded subtitles
3. Scan the subtitles for profane language
4. Create a censored version (``movie_censored.mp4``) with profane audio segments muted

Command Line Options
--------------------

**Custom Output Path:**

.. code-block:: bash

   guardian movie.mp4 --output clean_movie.mp4

**Verbose Logging:**

.. code-block:: bash

   guardian movie.mp4 --verbose

**Custom FFmpeg Paths:**

.. code-block:: bash

   guardian movie.mp4 --ffmpeg-path /usr/local/bin/ffmpeg --ffprobe-path /usr/local/bin/ffprobe

**Help:**

.. code-block:: bash

   guardian --help

Python API
----------

You can also use Dialogue Guardian programmatically:

.. code-block:: python

   from guardian import GuardianProcessor

   # Initialize the processor
   processor = GuardianProcessor()

   # Process a video file
   result = processor.process_video("movie.mp4")

   if result:
       print(f"Censored video created: {result}")
   else:
       print("Processing failed")

Custom Configuration
--------------------

**Custom Word List:**

.. code-block:: python

   from guardian import GuardianProcessor

   # Use a custom list of words to censor
   custom_words = ['badword1', 'badword2', 'inappropriate']
   processor = GuardianProcessor(matching_words=custom_words)

   result = processor.process_video("movie.mp4")

**Custom FFmpeg Paths:**

.. code-block:: python

   from guardian import GuardianProcessor

   processor = GuardianProcessor(
       ffmpeg_cmd='/usr/local/bin/ffmpeg',
       ffprobe_cmd='/usr/local/bin/ffprobe'
   )

   result = processor.process_video("movie.mp4")

File Requirements
-----------------

**Subtitle Files:**

Dialogue Guardian works with:

* External SRT files (``movie.srt`` alongside ``movie.mp4``)
* Language-specific SRT files (``movie.en.srt``, ``movie.fr.srt``, etc.)
* Embedded SRT subtitles in the video file

**Supported Video Formats:**

Any video format supported by FFmpeg, including:

* MP4
* AVI
* MKV
* MOV
* WMV
* And many more

Troubleshooting
---------------

**"ffmpeg not found" Error:**

Make sure FFmpeg is installed and accessible in your system's PATH. Test with:

.. code-block:: bash

   ffmpeg -version

**No Subtitles Found:**

Ensure you have either:

* An external SRT file with the same name as your video file
* Embedded subtitles in your video file

**Permission Errors:**

Make sure you have write permissions in the directory where you're trying to create the output file.