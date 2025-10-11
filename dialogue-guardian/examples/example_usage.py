#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Example usage of the Guardian package.
"""

from guardian import GuardianProcessor


def main():
    """Demonstrate package usage."""
    # Initialize the processor
    processor = GuardianProcessor()

    # Example: Process a video file
    video_path = "sample.mp4"

    print(f"Processing video: {video_path}")

    # Process the video (this would normally create a censored version)
    result = processor.process_video(video_path)

    if result:
        print(f"Censored video created: {result}")
    else:
        print(
            "Processing failed - check that FFmpeg is installed and the video file exists"
        )


if __name__ == "__main__":
    main()
