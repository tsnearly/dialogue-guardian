#!/usr/bin/env python3
"""
Migration script to help users transition from the old guardian_by_ffmpeg.py
to the new package structure.

This script provides backward compatibility by wrapping the new package API.
"""

import sys
import os
import logging
from guardian import GuardianProcessor


def main():
    """
    Backward compatibility wrapper for the old guardian_by_ffmpeg.py usage.
    """
    if len(sys.argv) != 2:
        print("Usage: python migrate_old_usage.py <videofile>")
        sys.exit(1)

    # Setup logging similar to the old script
    script_fullpath = sys.argv[0]
    script_filename = os.path.basename(script_fullpath)
    log_file = f"{os.path.splitext(script_filename)[0]}.log"
    
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s', 
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler()
        ]
    )
    
    filepath = os.path.abspath(sys.argv[1])
    logging.info(f"Processing file: {filepath}")
    
    # Check if the video file exists
    if not os.path.exists(filepath):
        logging.error(f"Video file not found: {filepath}. Exiting.")
        sys.exit(1)

    # Use the new package API
    processor = GuardianProcessor()
    
    # Get video details (for compatibility)
    video_info = processor.get_video_details(filepath)
    if not video_info:
        logging.error("Could not get video details. Exiting.")
        sys.exit(1)

    # Perform the audio censoring
    censored_file = processor.censor_audio_with_ffmpeg(filepath)
    
    if censored_file:
        logging.info(f"Censoring process completed. Output file: {censored_file}")
    else:
        logging.error("Censoring process failed.")
        sys.exit(1)

    logging.info("Script finished successfully.")


if __name__ == "__main__":
    main()