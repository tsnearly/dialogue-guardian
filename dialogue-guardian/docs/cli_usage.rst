Command Line Interface
======================

The ``guardian`` command provides a comprehensive command-line interface for processing video files.

Basic Syntax
------------

.. code-block:: bash

   guardian [OPTIONS] VIDEO_FILE

Arguments
---------

``VIDEO_FILE``
  Path to the video file to process. This is the only required argument.

Options
-------

``-o, --output OUTPUT``
  Specify a custom output path for the censored video file. If not provided, 
  creates a file with "_censored" suffix in the same directory as the input file.

  Example:
  
  .. code-block:: bash
  
     guardian movie.mp4 --output /path/to/clean_movie.mp4

``-v, --verbose``
  Enable verbose logging (DEBUG level). This provides detailed information 
  about the processing steps.

  Example:
  
  .. code-block:: bash
  
     guardian movie.mp4 --verbose

``--log-file LOG_FILE``
  Specify a custom path for the log file. Default is ``guardian_by_ffmpeg.log`` 
  in the current directory.

  Example:
  
  .. code-block:: bash
  
     guardian movie.mp4 --log-file /path/to/custom.log

``--ffmpeg-path FFMPEG_PATH``
  Specify a custom path to the ffmpeg executable. Default is ``ffmpeg`` 
  (assumes it's in your PATH).

  Example:
  
  .. code-block:: bash
  
     guardian movie.mp4 --ffmpeg-path /usr/local/bin/ffmpeg

``--ffprobe-path FFPROBE_PATH``
  Specify a custom path to the ffprobe executable. Default is ``ffprobe`` 
  (assumes it's in your PATH).

  Example:
  
  .. code-block:: bash
  
     guardian movie.mp4 --ffprobe-path /usr/local/bin/ffprobe

``--version``
  Show the program version and exit.

``-h, --help``
  Show help message and exit.

Examples
--------

**Basic Usage:**

.. code-block:: bash

   guardian movie.mp4

**Custom Output Location:**

.. code-block:: bash

   guardian /path/to/movie.mp4 --output /path/to/output/clean_movie.mp4

**Verbose Logging with Custom Log File:**

.. code-block:: bash

   guardian movie.mp4 --verbose --log-file detailed.log

**Custom FFmpeg Installation:**

.. code-block:: bash

   guardian movie.mp4 \
     --ffmpeg-path /opt/ffmpeg/bin/ffmpeg \
     --ffprobe-path /opt/ffmpeg/bin/ffprobe

**Processing Multiple Files (using shell):**

.. code-block:: bash

   # Process all MP4 files in current directory
   for file in *.mp4; do
     guardian "$file" --verbose
   done

Alternative Command
-------------------

You can also use the alternative command name:

.. code-block:: bash

   dialogue-guardian movie.mp4

This is identical to the ``guardian`` command and accepts all the same options.

Exit Codes
----------

The command returns different exit codes based on the result:

* ``0``: Success - video was processed successfully
* ``1``: Error - processing failed (check logs for details)

Error Handling
--------------

Common error scenarios and their solutions:

**File Not Found:**

.. code-block:: text

   Error: Video file not found: /path/to/movie.mp4

Solution: Check that the file path is correct and the file exists.

**Output Directory Doesn't Exist:**

.. code-block:: text

   Error: Output directory does not exist: /nonexistent/path

Solution: Create the output directory first or use a valid path.

**FFmpeg Not Found:**

.. code-block:: text

   Error: ffmpeg not found. Please ensure FFmpeg is installed...

Solution: Install FFmpeg or specify the correct path with ``--ffmpeg-path``.

**No Subtitles Found:**

.. code-block:: text

   Error: No SRT file (external or embedded) found or extractable...

Solution: Ensure your video has subtitles (external .srt file or embedded).

Logging
-------

The command creates detailed logs of the processing steps. By default, logs are 
written to ``guardian_by_ffmpeg.log`` in the current directory.

Log levels:

* **INFO**: General processing information
* **DEBUG**: Detailed processing steps (use ``--verbose``)
* **ERROR**: Error messages and failures
* **WARNING**: Non-fatal issues

Example log output:

.. code-block:: text

   2025-01-05 10:30:15,123 - INFO - Processing file: /path/to/movie.mp4
   2025-01-05 10:30:15,456 - INFO - Found external SRT file: /path/to/movie.srt
   2025-01-05 10:30:16,789 - DEBUG - Match found in subtitle #42: "bad language here"
   2025-01-05 10:30:45,012 - INFO - Successfully created censored video: /path/to/movie_censored.mp4