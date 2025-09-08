#!/usr/bin/env python3
"""
Unit tests for guardian.core module
"""

import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

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

    @patch("subprocess.check_output")
    def test_get_video_details_success(self, mock_check_output):
        """Test successful video details extraction"""
        # Mock ffprobe responses
        mock_check_output.side_effect = [
            "120.5",  # duration
            "aac|44100|2|stereo",  # audio info
            "1920\n1080\n30000/1001",  # video info
        ]

        result = self.processor.get_video_details(self.test_video_path)

        self.assertIsNotNone(result)
        self.assertEqual(result["duration"], "120.5")
        self.assertEqual(result["width"], "1920")
        self.assertEqual(result["height"], "1080")
        self.assertEqual(result["fps"], "29.970")

    @patch("subprocess.check_output")
    def test_get_video_details_ffprobe_error(self, mock_check_output):
        """Test handling of ffprobe command failure"""
        mock_check_output.side_effect = subprocess.CalledProcessError(
            1, "ffprobe", stderr="File not found"
        )

        result = self.processor.get_video_details(self.test_video_path)

        self.assertIsNone(result)

    @patch("subprocess.check_output")
    def test_get_video_details_file_not_found(self, mock_check_output):
        """Test handling of ffprobe not found"""
        mock_check_output.side_effect = FileNotFoundError()

        result = self.processor.get_video_details(self.test_video_path)

        self.assertIsNone(result)

    @patch("subprocess.check_output")
    @patch("json.loads")
    def test_extract_embedded_srt_success(self, mock_json_loads, mock_check_output):
        """Test successful SRT extraction"""
        # Mock ffprobe response
        mock_check_output.return_value = (
            '{"streams": [{"index": 2, "codec_name": "subrip", '
            '"disposition": {"default": 1}}]}'
        )
        mock_json_loads.return_value = {
            "streams": [
                {
                    "index": 2,
                    "codec_name": "subrip",
                    "disposition": {"default": 1},
                }
            ]
        }

        # Mock successful ffmpeg extraction
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.extract_embedded_srt(
                self.test_video_path, self.test_srt_path
            )

        self.assertTrue(result)

    @patch("subprocess.check_output")
    def test_extract_embedded_srt_no_srt_tracks(self, mock_check_output):
        """Test when no SRT tracks are found"""
        mock_check_output.return_value = '{"streams": []}'

        with patch("json.loads") as mock_json:
            mock_json.return_value = {"streams": []}

            result = self.processor.extract_embedded_srt(
                self.test_video_path, self.test_srt_path
            )

        self.assertFalse(result)

    @patch("subprocess.check_output")
    def test_extract_embedded_srt_json_error(self, mock_check_output):
        """Test handling of invalid JSON from ffprobe"""
        mock_check_output.return_value = "invalid json"

        with patch("json.loads") as mock_json:
            mock_json.side_effect = json.JSONDecodeError("Invalid", "", 0)

            result = self.processor.extract_embedded_srt(
                self.test_video_path, self.test_srt_path
            )

        self.assertFalse(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    @patch("subprocess.run")
    def test_censor_audio_with_ffmpeg_external_srt(
        self, mock_run, mock_srt_parse, mock_file, mock_exists
    ):
        """Test audio censoring with external SRT file"""
        # Mock file existence
        mock_exists.return_value = True

        # Mock SRT parsing
        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 10.0
        mock_subtitle.end.total_seconds.return_value = 15.0
        mock_subtitle.content = "This is fucking bad"
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        # Mock successful ffmpeg execution
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertEqual(
            result, f"{os.path.splitext(self.test_video_path)[0]}_censored.mp4"
        )

        # Verify ffmpeg was called with correct filter
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        # Check that the filter is in the command
        filter_found = any("volume=enable=" in str(arg) for arg in call_args)
        self.assertTrue(filter_found)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    @patch("subprocess.run")
    def test_censor_audio_with_custom_output(
        self, mock_run, mock_srt_parse, mock_file, mock_exists
    ):
        """Test audio censoring with custom output path"""
        mock_exists.return_value = True

        # Mock SRT parsing
        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 10.0
        mock_subtitle.end.total_seconds.return_value = 15.0
        mock_subtitle.content = "This is fucking bad"
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        # Mock successful ffmpeg execution
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        custom_output = "/custom/output.mp4"
        result = self.processor.censor_audio_with_ffmpeg(
            self.test_video_path, custom_output
        )

        self.assertEqual(result, custom_output)

    @patch("os.path.exists")
    def test_censor_audio_no_srt_found(self, mock_exists):
        """Test when no SRT file is found"""
        mock_exists.return_value = False

        with patch.object(self.processor, "extract_embedded_srt") as mock_extract:
            mock_extract.return_value = False

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    @patch("subprocess.run")
    def test_censor_audio_no_profanity_found(
        self, mock_run, mock_srt_parse, mock_file, mock_exists
    ):
        """Test when no profanity is found in subtitles"""
        mock_exists.return_value = True

        # Mock SRT with no profanity
        mock_subtitle = MagicMock()
        mock_subtitle.content = "This is clean content"
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        # Mock successful ffmpeg execution
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertEqual(
            result, f"{os.path.splitext(self.test_video_path)[0]}_censored.mp4"
        )

        # Verify no volume filter was applied (anull filter used instead)
        call_args = mock_run.call_args[0][0]
        self.assertIn("-af", call_args)
        af_index = call_args.index("-af")
        self.assertEqual(call_args[af_index + 1], "anull")

    @patch("subprocess.run")
    def test_censor_audio_ffmpeg_failure(self, mock_run):
        """Test handling of FFmpeg command failure"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ffmpeg", stderr="Encoding failed"
        )

        with patch("os.path.exists") as mock_exists, patch(
            "builtins.open", new_callable=mock_open
        ), patch("srt.parse") as mock_srt_parse:
            mock_exists.return_value = True
            mock_subtitle = MagicMock()
            mock_subtitle.content = "This is fucking bad"
            mock_subtitle.index = 1
            mock_srt_parse.return_value = [mock_subtitle]

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNone(result)

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
