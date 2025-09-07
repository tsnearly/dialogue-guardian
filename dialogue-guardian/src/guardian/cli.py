"""
Command-line interface for the Guardian media censoring system.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from .core import GuardianProcessor


def setup_logging(log_file: Optional[str] = None, verbose: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_file: Optional path to log file. If None, uses script name.
        verbose: If True, sets DEBUG level, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    if log_file is None:
        log_file = "guardian_by_ffmpeg.log"
    
    # Configure logging to file and console
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler()
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='guardian',
        description='Dialogue Guardian: Universal Media Censor - '
                   'Automatically detect and censor profane language in video files.',
        epilog='Example: guardian movie.mp4'
    )
    
    parser.add_argument(
        'video_file',
        help='Path to the video file to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output path for the censored video file. '
             'If not specified, creates a file with "_censored" suffix.'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Path to log file (default: guardian_by_ffmpeg.log)'
    )
    
    parser.add_argument(
        '--ffmpeg-path',
        default='ffmpeg',
        help='Path to ffmpeg executable (default: ffmpeg)'
    )
    
    parser.add_argument(
        '--ffprobe-path',
        default='ffprobe',
        help='Path to ffprobe executable (default: ffprobe)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.1.0'
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
    if not os.path.exists(args.video_file):
        print(f"Error: Video file not found: {args.video_file}", file=sys.stderr)
        return False
    
    # Validate output path if provided
    if args.output:
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if not os.path.exists(output_dir):
            print(f"Error: Output directory does not exist: {output_dir}", file=sys.stderr)
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
    setup_logging(args.log_file, args.verbose)
    
    # Get absolute path for the video file
    video_path = os.path.abspath(args.video_file)
    logging.info(f"Processing file: {video_path}")
    
    try:
        # Initialize the processor
        processor = GuardianProcessor(
            ffmpeg_cmd=args.ffmpeg_path,
            ffprobe_cmd=args.ffprobe_path
        )
        
        # Process the video
        censored_file = processor.process_video(video_path, args.output)
        
        if censored_file:
            logging.info(f"Censoring process completed successfully.")
            logging.info(f"Output file: {censored_file}")
            print(f"Censored video created: {censored_file}")
            return 0
        else:
            logging.error("Censoring process failed.")
            print("Error: Censoring process failed. Check the log for details.", file=sys.stderr)
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