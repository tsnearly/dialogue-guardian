"""
Command-line interface for the Guardian media censoring system.
"""

import argparse
import logging
import os
import sys
from typing import List, Optional

from . import __version__
from .core import GuardianProcessor


def setup_logging(log_file: Optional[str] = None, debug: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        log_file: Optional path to log file. If None, uses script name.
        verbose: If True, sets DEBUG level, otherwise INFO.
    """
    level = logging.DEBUG if debug else logging.INFO

    if log_file is None:
        log_file = "dialogue-guardian.log"

    # Configure logging handlers
    handlers: List[logging.Handler] = [logging.StreamHandler()]

    # Try to add file handler, fall back gracefully if it fails
    try:
        handlers.append(logging.FileHandler(log_file, mode="w"))
    except (PermissionError, OSError, IOError) as e:
        # If file handler fails, just use console logging
        print(f"Warning: Could not create log file '{log_file}': {e}", file=sys.stderr)

    # Configure logging to file and console
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="guardian",
        description="Dialogue Guardian: Universal Media Censor - "
        "Automatically detect and censor profane language in video files.",
        epilog="Example: guardian movie.mp4",
    )

    parser.add_argument(
        "--input",
        "-i",
        dest="inputfile",
        nargs="*",
        required=True,
        help="Path of the video file to process",
    )

    parser.add_argument(
        "--output",
        "-o",
        dest="outputfile",
        help="Output path for the censored video file. "
        "If not specified, creates a file with '_censored' suffix.",
    )

    parser.add_argument(
        "--log-file",
        "-l",
        dest="logfile",
        nargs="*",
        help="Path to log file (default: dialogue-guardian.log)",
    )

    parser.add_argument(
        "--debug",
        "-d",
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
    # Check if video file exists
    if not os.path.exists(args.inputfile):
        print(f"Error: Input video file not found: {args.inputfile}", file=sys.stderr)
        return False

    # Validate output path if provided
    if args.output:
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if not os.path.exists(output_dir):
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
    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    if not validate_args(args):
        return 1

    # Setup logging
    setup_logging(args.log_file, args.debug)

    # Get absolute path for the video file
    video_path = os.path.abspath(args.inputfile)
    logging.info(f"Processing file: {video_path}")

    try:
        # Initialize the processor
        processor = GuardianProcessor(
            ffmpeg_cmd=args.ffmpeg_path, ffprobe_cmd=args.ffprobe_path
        )

        # Process the video
        censored_file = processor.process_video(video_path, args.output)

        if censored_file:
            logging.info("Censoring process completed successfully.")
            logging.info(f"Output file: {censored_file}")
            print(f"Censored video created: {censored_file}")
            return 0
        else:
            logging.error("Censoring process failed.")
            print(
                "Error: Censoring process failed. Check the log for details.",
                file=sys.stderr,
            )
            return 1

    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
        print("\nProcess interrupted by user.", file=sys.stderr)
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error: An unexpected error occurred: {e}", file=sys.stderr)
        return 1
    finally:
        logging.info("Script finished.")


if __name__ == "__main__":
    sys.exit(main())
