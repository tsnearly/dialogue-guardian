# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Command-line interface for the Guardian media censoring system.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .core import GuardianProcessor

# Supported video file extensions
SUPPORTED_VIDEO_EXTENSIONS = {".mkv"}


def setup_logging(log_file: Optional[List[str]] = None, verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        log_file: Optional path to log file. If None, uses script name.
        verbose: If True, sets DEBUG level, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO

    log_path = "dialogue-guardian.log"
    if log_file:
        log_path = log_file[0]

    # Configure logging handlers
    handlers: List[logging.Handler] = [logging.StreamHandler()]

    # Try to add file handler, fall back gracefully if it fails
    try:
        handlers.append(logging.FileHandler(log_path, mode="w"))
    except (PermissionError, OSError, IOError) as e:
        # If file handler fails, just use console logging
        print(f"Warning: Could not create log file '{log_path}': {e}", file=sys.stderr)

    # Configure logging to file and console
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def expand_input_paths(input_paths: List[str]) -> List[str]:
    """
    Expand input paths to include video files from directories.

    If an input path is a directory, discover all video files in that directory.
    If an input path is a file, include it as-is.

    Args:
        input_paths: List of file or directory paths provided by user.

    Returns:
        List of file paths to process.
    """
    expanded_files: List[str] = []

    for path in input_paths:
        if os.path.isdir(path):
            # Find all video files in the directory
            video_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if Path(file).suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        video_files.append(full_path)

            if video_files:
                logging.info(
                    f"Found {len(video_files)} video file(s) in directory: {path}"
                )
                expanded_files.extend(sorted(video_files))
            else:
                logging.warning(f"No video files found in directory: {path}")
        else:
            # It's a file, include it as-is
            expanded_files.append(path)

    return expanded_files


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="guardian",
        description=(
            "Dialogue Guardian: Universal Media Censor - "
            "Automatically detect and censor profane language in video files."
        ),
        epilog="Example: guardian movie.mp4",
    )

    parser.add_argument(
        "--input",
        "-i",
        dest="inputfile",
        nargs="+",
        required=True,
        help="Path(s) of video file(s) or directory to process. "
        "If a directory is provided, all video files in that directory will be processed.",
    )

    parser.add_argument(
        "--output",
        "-o",
        dest="outputfile",
        help=(
            "Output path for the censored video file. "
            "If not specified, creates a file with '_censored' suffix."
        ),
    )

    parser.add_argument(
        "--log-file",
        "-l",
        dest="logfile",
        nargs="*",
        help="Path to log file (default: dialogue-guardian.log)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    parser.add_argument(
        "--ffmpeg-path",
        "-m",
        dest="ffmpeg",
        default="ffmpeg",
        help="Path to ffmpeg executable (default: ffmpeg)",
    )

    parser.add_argument(
        "--ffprobe-path",
        "-p",
        dest="ffprobe",
        default="ffprobe",
        help="Path to ffprobe executable (default: ffprobe)",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        dest="full",
        help=(
            "Execute full audio verification routines (slower). "
            "By default the processor will assume censoring succeeded and "
            "skip repeated audio checks to speed up processing."
        ),
    )

    parser.add_argument(
        "--version", "-ver", help="Show version", action="version", version=__version__
    )

    return parser


def validate_args(args: argparse.Namespace) -> bool:
    """
    Validate command line arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        True if arguments are valid, False otherwise.
    """
    # Check if input files/directories exist
    for input_path in args.inputfile:
        if not os.path.exists(input_path):
            print(f"Error: Input path not found: {input_path}", file=sys.stderr)
            return False

    # Validate output path if provided
    if args.outputfile:
        output_dir = os.path.dirname(os.path.abspath(args.outputfile))
        if output_dir and not os.path.exists(output_dir):
            print(
                f"Error: Output directory does not exist: {output_dir}",
                file=sys.stderr,
            )
            return False

    return True


def main() -> int:
    """
    Main entry point for the CLI application.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Validate arguments
        if not validate_args(args):
            return 1

        # Setup logging
        setup_logging(args.logfile, args.verbose)

        # Expand directories to video files
        video_files = expand_input_paths(args.inputfile)

        if not video_files:
            print("Error: No video files found to process.", file=sys.stderr)
            logging.error("No video files found to process.")
            return 1

        logging.info(f"Processing {len(video_files)} video file(s)...")

        # Process each video file
        for input_file in video_files:
            video_path = os.path.abspath(input_file)
            logging.info(f"Processing file: {video_path}")

            # Initialize the processor
            processor = GuardianProcessor(
                ffmpeg_cmd=args.ffmpeg, ffprobe_cmd=args.ffprobe
            )

            # Process the video
            # Keep the CLI call backwards-compatible: do not pass the optional
            # `full` parameter positionally so existing callers and tests
            # that expect a two-argument call continue to work. The
            # `censor_audio_with_ffmpeg` API accepts an optional `full`
            # parameter if callers want to pass it directly.
            censored_file = processor.censor_audio_with_ffmpeg(
                video_path, args.outputfile, full=args.full
            )

            if censored_file:
                logging.info("Censoring process a success.")
                logging.info(f"Output file: {censored_file}")
                print(f"Censored video created: {censored_file}")
            else:
                logging.error(f"Censoring process failed for file: {video_path}")
                print(
                    f"Error: Censoring process failed for file: {video_path}. "
                    "See log for details.",
                    file=sys.stderr,
                )
                return 1
        return 0

    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
        print("\nProcess interrupted by user.", file=sys.stderr)
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error: An unexpected error occurred: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
