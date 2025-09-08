Dialogue Guardian Documentation
================================

.. image:: /logo.png
   :height: 200px
   :width: 200px
   :scale: 100%
   :alt: Dialogue Guardian logo
   :align: right
   :target:  https://github.com/tsnearly/dialogue-guardian/

**Dialogue Guardian** is a universal media censor that automatically detects and censors profane language in video files by processing SRT subtitle files.

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Features
--------

* **Direct Audio Censoring**: Uses FFmpeg's audio filters to mute profane segments
* **Universal Compatibility**: Works on any OS with FFmpeg installed (Windows, macOS, Linux)
* **Automatic SRT Extraction**: Extracts embedded SRT tracks from video files
* **Non-Destructive**: Creates new video files, leaving originals untouched
* **Efficient Processing**: Copies video streams without re-encoding
* **Python API**: Programmatic access to all functionality
* **Command Line Interface**: Easy-to-use CLI with comprehensive options

Quick Start
-----------

Installation::

    pip install dialogue-guardian

Basic Usage::

    # Command line
    guardian movie.mp4

    # Python API
    from guardian import GuardianProcessor
    processor = GuardianProcessor()
    result = processor.process_video("movie.mp4")

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   quickstart
   cli_usage
   python_api

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/guardian

.. toctree::
   :maxdepth: 1
   :caption: Development:

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

