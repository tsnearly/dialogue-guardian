#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Unit tests for guardian.core module
"""

import tempfile
import unittest
from unittest.mock import mock_open, patch

import srt

from guardian.core import GuardianProcessor


class TestGuardianProcessor(unittest.TestCase):
    """Test cases for GuardianProcessor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = GuardianProcessor()
        self.test_video_path = "/test/video.mp4"
        self.test_srt_path = "/test/video.srt"
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_values(self):
        """Test processor initialization with default values"""
        processor = GuardianProcessor()
        self.assertEqual(
            processor.matching_words, GuardianProcessor.DEFAULT_MATCHING_WORDS
        )
        self.assertEqual(processor.ffmpeg_cmd, "ffmpeg")
        self.assertEqual(processor.ffprobe_cmd, "ffprobe")

    def test_init_custom_values(self):
        """Test processor initialization with custom values"""
        custom_words = ["bad", "worse"]
        processor = GuardianProcessor(
            matching_words=custom_words,
            ffmpeg_cmd="/usr/bin/ffmpeg",
            ffprobe_cmd="/usr/bin/ffprobe",
        )
        self.assertEqual(processor.matching_words, custom_words)
        self.assertEqual(processor.ffmpeg_cmd, "/usr/bin/ffmpeg")
        self.assertEqual(processor.ffprobe_cmd, "/usr/bin/ffprobe")

    @patch("os.path.exists")
    def test_process_video_file_not_found(self, mock_exists):
        """Test process_video with non-existent file"""
        mock_exists.return_value = False

        result = self.processor.process_video(self.test_video_path)

        self.assertIsNone(result)

    @patch("os.path.exists")
    def test_process_video_success(self, mock_exists):
        """Test successful video processing"""
        mock_exists.return_value = True

        with patch.object(
            self.processor, "get_video_details"
        ) as mock_details, patch.object(
            self.processor, "censor_audio_with_ffmpeg"
        ) as mock_censor:

            mock_details.return_value = {"duration": "60.0"}
            mock_censor.return_value = "/output/censored.mp4"

            result = self.processor.process_video(self.test_video_path)

            self.assertEqual(result, "/output/censored.mp4")
            mock_details.assert_called_once_with(self.test_video_path)
            mock_censor.assert_called_once_with(self.test_video_path, None)

    def test_matching_words_list(self):
        """Test that matching words list is properly defined"""
        self.assertIsInstance(self.processor.matching_words, list)
        self.assertGreater(len(self.processor.matching_words), 0)
        self.assertIn("fuck", self.processor.matching_words)
        self.assertIn("shit", self.processor.matching_words)
        # Test that all items are strings
        for word in self.processor.matching_words:
            self.assertIsInstance(word, str)

    def test_find_srt_file(self):
        """Test the _find_srt_file method."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            self.assertEqual(
                self.processor._find_srt_file("/test/video.mp4"), "/test/video.srt"
            )

    def test_find_srt_file_language(self):
        """Test the _find_srt_file method with a language-specific SRT file."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path.endswith(".en.srt")
            self.assertEqual(
                self.processor._find_srt_file("/test/video.mp4"), "/test/video.en.srt"
            )

    def test_parse_srt_file(self):
        """Test the _parse_srt_file method."""
        with patch(
            "builtins.open",
            mock_open(read_data="1\n00:00:01,000 --> 00:00:02,000\ntest"),
        ):
            subs = self.processor._parse_srt_file("dummy.srt")
            self.assertEqual(len(subs), 1)
            self.assertEqual(subs[0].content, "test")

    def test_find_profane_segments(self):
        """Test the _find_profane_segments method."""
        subs = [
            srt.Subtitle(
                index=1,
                start=srt.srt_timestamp_to_timedelta("00:00:01,000"),
                end=srt.srt_timestamp_to_timedelta("00:00:02,000"),
                content="this is a fucking test",
            )
        ]
        segments = self.processor._find_profane_segments(subs)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], (1.0, 2.0))

    @patch("platform.system")
    def test_construct_ffmpeg_command(self, mock_system):
        """Test the _construct_ffmpeg_command method."""
        # Test on Linux
        mock_system.return_value = "Linux"
        command = self.processor._construct_ffmpeg_command(
            "/test/video.mp4", "/test/censored.mp4", [(1.0, 2.0)]
        )
        self.assertIn("volume=0:enable='between(t,1.0,2.0)'", command)

        # Test on Windows
        mock_system.return_value = "Windows"
        command = self.processor._construct_ffmpeg_command(
            "/test/video.mp4", "/test/censored.mp4", [(1.0, 2.0)]
        )
        self.assertIn('volume=0:enable="between(t,1.0,2.0)"', command)

    def test_regex_pattern_compilation(self):
        """Test that the profanity regex pattern compiles correctly"""
        import re

        pattern = (
            r"\b("
            + "|".join(re.escape(word) for word in self.processor.matching_words)
            + r")\b"
        )
        compiled_pattern = re.compile(pattern, re.IGNORECASE)

        # Test pattern matches expected words
        test_cases = [
            ("This is fucking bad", True),
            ("Clean content", False),
            ("What the hell", True),
            ("Hello world", False),
            ("SHIT happens", True),  # Test case insensitivity
        ]

        for text, should_match in test_cases:
            match = compiled_pattern.search(text.lower())
            self.assertEqual(bool(match), should_match, f"Failed for text: {text}")


if __name__ == "__main__":
    unittest.main()
